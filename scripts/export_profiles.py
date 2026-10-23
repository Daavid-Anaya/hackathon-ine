"""Selecciona cinco perfiles agregados de 2024 y exporta el contexto histórico T07."""

import argparse
from itertools import combinations
import json
import math
from pathlib import Path
import re
import sys
import tempfile

import numpy as np
import pandas as pd
import sklearn
from threadpoolctl import threadpool_limits

import compare_history as history
import compare_segments as engine
from clean_ccpc import COUNTS, require
from download_ccpc import sha256


ROOT = Path(__file__).resolve().parents[1]
YEARS = sorted(year for _, years, _ in history.SERIES for year in years)
SUMMARY_FIELDS = ["groups", "entities", *COUNTS, "ln_share_pct", "participation_pct",
                  "participation_min_pct", "participation_max_pct", "unspecified_pct",
                  "sex_ln_share_pct", "age_ln_share_pct"]
METRIC_FIELDS = ["groups", "silhouette", "minimum_cluster_groups", "minimum_cluster_ln_share_pct"]
LIMITATIONS = [
    "Los perfiles seleccionados son estratos agregados de participación de 2024, no tipos individuales ni causas de abstención.",
    "Los modelos usan SV/(SV+NV), sin escalado y con igual peso por grupo; la composición demográfica no interviene en las distancias.",
    "La ponderación por LN responde a otro objetivo y puede cambiar pertenencias; no se selecciona en esta entrega.",
    "Los cinco perfiles centrales no imponen cinco conglomerados óptimos a los demás años; se conservan los 36 candidatos anuales.",
    "Las referencias de 4, 5 y 6 bandas son retrospectivas: 2024 para 2012/2018/2024 y 2021 para 2009/2015/2021; no son validación predictiva.",
    "No se suman poblaciones entre elecciones ni se equiparan identificadores de las dos series; las coincidencias de claves no son trayectorias individuales.",
    "La cobertura, los no especificados y la composición pueden cambiar; la ausencia histórica de sexo 2 no representa población cero.",
    "Los grupos no elegibles se contabilizan sin asignación ni tasa exportada; los umbrales exploratorios no son una política de divulgación.",
    "Todas las salidas son internas: requieren revisión de divulgación antes de publicarse o incorporarse a materiales públicos.",
    "Se verifican nuevamente ajustes base y referencias; las sensibilidades y barridos de estabilidad se conservan como evidencia T07, no se recalculan aquí.",
]


def equivalent(actual, expected, context):
    """Compara evidencia numérica sin confundir cambios de prosa con cambios de cálculo."""
    if isinstance(expected, dict):
        require(isinstance(actual, dict) and actual.keys() == expected.keys(), f"Evidencia incompatible: {context}")
        for key, value in expected.items():
            equivalent(actual[key], value, f"{context}.{key}")
    elif isinstance(expected, list):
        require(isinstance(actual, list) and len(actual) == len(expected), f"Evidencia incompleta: {context}")
        for index, value in enumerate(expected):
            equivalent(actual[index], value, f"{context}[{index}]")
    elif isinstance(expected, (float, int)) and not isinstance(expected, bool):
        require(isinstance(actual, (float, int)) and not isinstance(actual, bool)
                and math.isfinite(actual) and math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-9),
                f"Evidencia numérica incompatible: {context}")
    else:
        require(type(actual) is type(expected) and actual == expected, f"Evidencia incompatible: {context}")


def confined(root, value, directory):
    path = (root / value).resolve()
    require(path.is_relative_to(root / directory), f"La ruta debe estar dentro de {directory}")
    return path


def indexed(items, fields, expected, context):
    require(isinstance(items, list), f"Evidencia no válida: {context}")
    result = {tuple(item[field] for field in fields): item for item in items}
    require(len(result) == len(items) and set(result) == set(expected), f"Evidencia incompleta: {context}")
    return result


def environment():
    return {"python": sys.version.split()[0], "numpy": np.__version__,
            "pandas": pd.__version__, "sklearn": sklearn.__version__}


def validate_stability(recorded, method, entity_count):
    for key, expected in (("leave_entity_out_ari", entity_count),
                          ("seed_stability_ari", len(engine.SEEDS) - 1)):
        if key == "seed_stability_ari" and method == "ward":
            require(recorded[key] is None, "Ward no tiene estabilidad entre semillas")
            continue
        scores = recorded[key]
        require(isinstance(scores, dict) and isinstance(scores["unavailable"], list)
                and type(scores["evaluated"]) is int and scores["evaluated"] > 0
                and scores["evaluated"] + len(scores["unavailable"]) == expected,
                "Evidencia de estabilidad incompleta")
        for name in ("min", "median", "max"):
            value = scores[name]
            require(type(value) in (int, float) and math.isfinite(value) and -1 <= value <= 1,
                    "ARI de estabilidad no válido")
        require(scores["min"] <= scores["median"] <= scores["max"], "Distribución ARI no válida")


def load_evidence(path):
    evidence = json.loads(path.read_text(encoding="utf-8"))
    require(evidence["contract"] == "t07-history/v1" and evidence["internal_only"] is True,
            "Se requiere evidencia histórica interna T07")
    require(evidence["selection"] == "deferred_to_T08", "La evidencia no es una comparación T07 pendiente de selección")
    equivalent(evidence["environment"], environment(), "entorno; use la imagen fijada de T07")
    equivalent(evidence["series"], [{"name": name, "years": list(years), "reference_year": reference}
                                  for name, years, reference in history.SERIES], "series")
    config = evidence["config"]
    equivalent(config["annual_features"], ["participation_pct"], "variables")
    equivalent(config["seeds"], engine.SEEDS, "semillas")
    equivalent(config["scenarios"], {name: list(value) for name, value in engine.SCENARIOS.items()}, "escenarios")
    equivalent(config["kmeans_parameters_example_k6"], engine.kmeans_model(6).get_params(), "parámetros")
    equivalent(config["unit"], ["AELEC", *engine.KEYS], "unidad")
    require(config["annual_weighting"] in ("equal aggregate groups", "igual peso por grupo agregado"),
            "La evidencia no usa igual peso por grupo")
    require(set(evidence["annual"]) == set(map(str, YEARS)), "La evidencia debe incluir las seis elecciones")
    for name in ("pipeline_sha256", "comparison_engine_sha256"):
        require(re.fullmatch(r"[a-f0-9]{64}", evidence[name]) is not None, "Falta la procedencia del proceso T07")
    return evidence


def verify_and_rebuild(root, source, evidence):
    datasets, fingerprints, annual_labels, accounting = {}, {}, {}, {}
    candidate_keys = {(method, k) for method in ("kmeans", "ward") for k in (4, 5, 6)}
    for year in YEARS:
        bundle = confined(root, source / str(year), "data/processed")
        for filename in ("table.csv", "report.json"):
            confined(root, bundle / filename, "data/processed")
        frame, source_report, hashes = engine.load_input(bundle, year=year)
        annual = evidence["annual"][str(year)]
        equivalent({key: annual["input"][key] for key in hashes}, hashes, f"huellas T06 de {year}")
        equivalent(annual["input"]["election_year"], year, f"año {year}")
        equivalent(annual["input"]["rows"], len(frame), f"filas {year}")
        equivalent(annual["input"]["totals"], engine.totals(frame), f"totales {year}")
        for recorded_key, source_key in (("source", "source"), ("manifest_sha256", "manifest_sha256"),
                                         ("t06_pipeline_sha256", "pipeline_sha256")):
            equivalent(annual["input"][recorded_key], source_report.get(source_key), f"procedencia {year}/{recorded_key}")
        scenarios, eligibility = engine.prepare_scenarios(frame)
        equivalent(annual["eligibility"], eligibility, f"elegibilidad {year}")
        datasets[year], fingerprints[year], accounting[year] = scenarios, hashes, eligibility
        candidates = indexed(annual["candidates"], ("method", "k"), candidate_keys, f"candidatos {year}")
        base = scenarios["baseline"]
        for (method, k), recorded in candidates.items():
            require(recorded["status"] == "ok", f"Candidato no disponible de {year}")
            indexed(recorded["sensitivities"], ("scenario",),
                    {(scenario,) for scenario in engine.SCENARIOS if scenario != "baseline"}, f"sensibilidades {year}/{method}/{k}")
            validate_stability(recorded, method, int(base["EDOCVE"].nunique()))
            labels, matrix = engine.fit(base, k, method)
            equivalent({key: recorded[key] for key in METRIC_FIELDS}, engine.metrics(base, labels, matrix),
                       f"métricas {year}/{method}/{k}")
            equivalent(recorded["clusters"], engine.cluster_summaries(base, labels), f"resúmenes {year}/{method}/{k}")
            annual_labels[year, k, method] = history.keyed(base, labels)
    reference_keys = {(name, k) for name, _, _ in history.SERIES for k in (4, 5, 6)}
    references = indexed(evidence["references"], ("series", "k"), reference_keys, "referencias")
    pair_keys = {(name, start, end, k) for name, years, _ in history.SERIES
                 for start, end in combinations(years, 2) for k in (4, 5, 6)}
    pairs = indexed(evidence["pairs"], ("series", "from_year", "to_year", "k"), pair_keys, "pares históricos")
    rebuilt = []
    for name, years, reference_year in history.SERIES:
        for k in (4, 5, 6):
            reference, partitions = history.fixed_reference(name, years, reference_year, datasets, k)
            for key in ("series", "reference_year", "k", "centroids_pct", "boundaries_pct", "parameters", "years"):
                equivalent(references[name, k][key], reference[key], f"referencia {name}/{k}/{key}")
            for start, end in combinations(years, 2):
                pair = history.paired_diagnostic(name, start, end, reference_year, k, datasets, partitions, annual_labels)
                equivalent(pairs[name, start, end, k], pair, f"par {name}/{start}/{end}/{k}")
            rebuilt.append((reference, partitions))
    return datasets, fingerprints, accounting, rebuilt, annual_labels


def serial_rows(rows):
    return [{key: json.dumps(value, sort_keys=True, ensure_ascii=True) if isinstance(value, dict) else value
             for key, value in row.items()} for row in rows]


def export(root, input_path, history_path, run_name):
    root = root.resolve()
    source = confined(root, input_path, "data/processed")
    evidence_path = confined(root, history_path, "outputs")
    destination = confined(root, Path("outputs") / run_name, "outputs")
    require(not destination.exists(), "La salida ya existe; elija otro --run-name")
    evidence_hash = sha256(evidence_path)
    evidence = load_evidence(evidence_path)
    with threadpool_limits(limits=1):
        datasets, fingerprints, accounting, references, annual_labels = verify_and_rebuild(root, source, evidence)
    fixed_rows, historical_assignments, profiles, assignments = [], [], [], []
    for reference, partitions in references:
        name, k, reference_year = reference["series"], reference["k"], reference["reference_year"]
        for year_string, summaries in reference["years"].items():
            year = int(year_string)
            for row in summaries:
                rank = row["reference_rank"]
                identity = f"CCPC-REF-{reference_year}-K{k}-R{rank:02d}"
                metadata = {"series": name, "reference_year": reference_year, "year": year, "k": k}
                fixed_rows.append({**metadata, "reference_id": identity,
                                   "centroid_pct": reference["centroids_pct"][rank - 1], **row})
                if reference_year == year == 2024 and k == 5:
                    profiles.append({"profile_id": f"CCPC-2024-K5-P{rank:02d}", "year": year,
                                     "reference_id": identity, "centroid_pct": reference["centroids_pct"][rank - 1], **row})
            base = datasets[year]["baseline"]
            ranks = partitions[year].reindex(pd.MultiIndex.from_frame(base[engine.KEYS]))
            for values, rank in zip(base.to_dict("records"), ranks, strict=True):
                record = {"year": year, **{key: values[key] for key in [*engine.KEYS, *COUNTS, "participation_pct"]}}
                historical_assignments.append({**metadata, **record,
                                               "reference_id": f"CCPC-REF-{reference_year}-K{k}-R{rank:02d}"})
                if reference_year == year == 2024 and k == 5:
                    assignments.append({**record, "profile_id": f"CCPC-2024-K5-P{rank:02d}"})
    selected_reference = next(partitions[2024] for reference, partitions in references
                              if reference["reference_year"] == 2024 and reference["k"] == 5)
    require(engine.agreement(selected_reference, annual_labels[2024, 5, "kmeans"]) == 1,
            "La asignación por centroides no reproduce el ajuste seleccionado")
    require(len(profiles) == 5 and all(row["groups"] > 0 for row in profiles),
            "No hay cinco perfiles diferenciados; revisar variables o método")
    exclusions = []
    for year in YEARS:
        frame, _, _ = engine.load_input(source / str(year), year=year)
        derived = engine.derive(frame)
        for row in derived.loc[~derived.index.isin(datasets[year]["baseline"].index)].to_dict("records"):
            reasons = []
            if row["known_denominator"] < 30:
                reasons.append("denominador conocido menor que 30")
            if row["known_coverage_pct"] < 80:
                reasons.append("cobertura conocida menor que 80%")
            exclusions.append({"year": year, **{key: row[key] for key in [*engine.KEYS, *COUNTS]},
                               "reason": "; ".join(reasons)})
    annual_rows = []
    for year, annual in evidence["annual"].items():
        for candidate in annual["candidates"]:
            annual_rows.append({"year": year, "scenario": "baseline", **candidate})
            annual_rows.extend({"year": year, "method": candidate["method"], "k": candidate["k"], **item}
                               for item in candidate["sensitivities"])
    selected = next(item for item in evidence["annual"]["2024"]["candidates"]
                    if item["method"] == "kmeans" and item["k"] == 5)
    report = {
        "contract": "t08-profiles/v1", "internal_only": True,
        "selection": {"year": 2024, "method": "kmeans", "k": 5, "scenario": "baseline",
                      "features": ["participation_pct"], "scaling": "ninguno", "weighting": "igual peso por grupo agregado",
                      "parameters": engine.kmeans_model(5).get_params(), "evidence": selected,
                      "rationale": "Decisión explícita de T08: cinco perfiles centrales; equilibrio entre separación, estabilidad, tamaño e interpretación. No es una selección anual automática por máxima silueta."},
        "environment": environment(), "pipeline_sha256": sha256(Path(__file__)),
        "comparison_engine_sha256": sha256(Path(engine.__file__)), "history_engine_sha256": sha256(Path(history.__file__)),
        "evidence": {"path": evidence_path.relative_to(root).as_posix(), "sha256": evidence_hash,
                     "producer_sha256": evidence["pipeline_sha256"], "engine_sha256": evidence["comparison_engine_sha256"]},
        "inputs": {str(year): {**evidence["annual"][str(year)]["input"],
                               "directory": (source / str(year)).relative_to(root).as_posix()} for year in YEARS},
        "eligibility": {str(year): value["baseline"] for year, value in accounting.items()},
        "series": evidence["series"], "profiles": profiles, "limitations": LIMITATIONS,
        "identity_scope": "Identificadores versionados por año de referencia y k, ordenados por centroide creciente; los identificadores REF no son perfiles finales de otras elecciones.",
        "verification": {"annual_baseline_fits": 36, "fixed_references": 6, "pairwise_comparisons": 18,
                         "stability_and_sensitivities": "Evidencia T07 conservada, no recalculada"},
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent, prefix=".profiles-") as temporary:
        staging = Path(temporary) / "bundle"
        staging.mkdir()
        history.write_csv(staging / "profiles.csv", ["profile_id", "year", "reference_id", "reference_rank", "centroid_pct", *SUMMARY_FIELDS], serial_rows(profiles))
        history.write_csv(staging / "assignments.csv", ["profile_id", "year", *engine.KEYS, *COUNTS, "participation_pct"], assignments)
        history.write_csv(staging / "historical_assignments.csv", ["series", "reference_year", "year", "k", "reference_id", *engine.KEYS, *COUNTS, "participation_pct"], historical_assignments)
        history.write_csv(staging / "fixed_reference.csv", ["series", "reference_year", "year", "k", "reference_id", "reference_rank", "centroid_pct", *SUMMARY_FIELDS], serial_rows(fixed_rows))
        history.write_csv(staging / "exclusions.csv", ["year", *engine.KEYS, *COUNTS, "reason"], exclusions)
        history.write_csv(staging / "annual_comparison.csv", ["year", "method", "k", "scenario", "status", *METRIC_FIELDS, "common_groups", "ari_on_common_groups"], annual_rows)
        history.write_csv(staging / "pairwise.csv", ["series", "reference_year", "from_year", "to_year", "k", "status", "common_groups",
                          "from_only_groups", "to_only_groups", "mean_delta_pp", "median_delta_pp", "spearman_rate_rank",
                          "same_reference_band_group_pct", "annual_kmeans_ari", "annual_ward_ari"],
                          [{**pair, **{f"annual_{method}_ari": score for method, score in pair.get("annual_ari", {}).items()}}
                           for pair in evidence["pairs"]])
        (staging / "t07_evidence.json").write_bytes(evidence_path.read_bytes())
        report["artifacts_sha256"] = {path.name: sha256(path) for path in sorted(staging.iterdir())}
        (staging / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False) + "\n", encoding="utf-8")
        require(sha256(evidence_path) == evidence_hash and sha256(staging / "t07_evidence.json") == evidence_hash,
                "La evidencia T07 cambió durante la exportación")
        for year, hashes in fingerprints.items():
            require(all(sha256(source / str(year) / filename) == hashes[key]
                        for filename, key in (("table.csv", "table_sha256"), ("report.json", "report_sha256"))),
                    f"Las entradas de {year} cambiaron durante la exportación")
        require(not destination.exists(), "La salida ya existe")
        staging.rename(destination)
    return {"status": "ok", "directory": destination.relative_to(root).as_posix(), "profiles": 5,
            "years": YEARS, "annual_candidates": 36, "reference_solutions": 6, "pairwise_comparisons": 18,
            "assigned_groups": len(assignments), "historical_assignments": len(historical_assignments), "internal_only": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Raíz del proyecto o de datos de prueba aislados")
    parser.add_argument("--input", default="data/processed/ccpc_all", help="Paquetes T06 de seis años dentro de data/processed")
    parser.add_argument("--history", default="outputs/t07_history/report.json", help="Informe histórico T07 dentro de outputs; no se modifica")
    parser.add_argument("--run-name", default="t08_profiles", help="Directorio nuevo dentro de outputs; nunca se sobrescribe")
    arguments = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", arguments.run_name):
        parser.error("--run-name debe ser un nombre alfanumérico simple con guiones o guiones bajos opcionales")
    try:
        result = export(arguments.root, arguments.input, arguments.history, arguments.run_name)
    except (ValueError, OSError, KeyError, OverflowError, TypeError, AttributeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
