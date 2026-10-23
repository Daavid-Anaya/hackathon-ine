"""Compara 4, 5 y 6 segmentos agregados de participación para T07, no perfiles finales de T08."""

import argparse
import csv
import json
from pathlib import Path
import re
import sys
import tempfile

import numpy as np
import pandas as pd
import sklearn
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits

from clean_ccpc import BANDS, COUNTS, YEARS, integers, require
from download_ccpc import sha256


ROOT = Path(__file__).resolve().parents[1]
KEYS = ["EDOCVE", "SEXO", "age_band"]
CHECKS = ["source_integrity_before_after", "schema", "key_uniqueness_exact", "domains",
          "geographic_consistency", "accounting_identity", "entity_coverage", "totals_reconciled"]
SEEDS = list(range(20))
SCENARIOS = {
    "baseline": (30, 80), "min_d15": (15, 80), "min_d60": (60, 80),
    "coverage70": (30, 70), "coverage90": (30, 90), "ln_weighted": (30, 80),
    "participation_unspecified": (30, 80), "without_age_over_110": (30, 80),
}


def totals(frame):
    return {name: sum(map(int, frame[name])) for name in COUNTS}


def load_input(bundle, year=2024):
    require(year in YEARS, "Año electoral no admitido")
    table, report_path = bundle / "table.csv", bundle / "report.json"
    hashes = {"table_sha256": sha256(table), "report_sha256": sha256(report_path)}
    report = json.loads(report_path.read_text(encoding="utf-8"))
    require(report.get("table_sha256") == hashes["table_sha256"], "La suma de comprobación de la tabla T06 no coincide")
    require(report.get("election_year") == year and report.get("unit") == KEYS, f"Se esperaba la unidad T06 de {year}")
    require(all(report.get("checks", {}).get(name) is True for name in CHECKS), "Faltan comprobaciones T06")
    frame = pd.read_csv(table, dtype=str, keep_default_na=False)
    required = ["AELEC", *KEYS, *COUNTS, *[f"age_over_110_{name}" for name in COUNTS]]
    require(set(required).issubset(frame.columns), "Faltan columnas analíticas")
    require(len(frame) > 0 and frame["AELEC"].eq(str(year)).all(), f"Solo se admite {year}")
    for name, low, high in [("EDOCVE", 1, 32), ("SEXO", 0, 2 if year == 2024 else 1)]:
        frame[name] = integers(frame[name], name, low, high).astype(str)
    frame["EDOCVE"] = frame["EDOCVE"].str.zfill(2)
    require(frame["age_band"].isin(BANDS).all(), "age_band no válido")
    require(not frame.duplicated(KEYS).any(), "Se encontraron claves analíticas duplicadas")
    for name in COUNTS:
        frame[name] = integers(frame[name], name, 1 if name == "LN" else 0)
        audit = f"age_over_110_{name}"
        frame[audit] = integers(frame[audit], audit, 0)
        require(frame[audit].le(frame[name]).all(), "Contribución age_over_110 no válida")
        require(frame.loc[frame["age_band"].ne("60+"), audit].eq(0).all(),
                "Contribuciones age_over_110 fuera de 60+")
    # Los enteros de Python evitan desbordamientos en la identidad contable.
    for prefix in ("", "age_over_110_"):
        values = frame[[prefix + name for name in COUNTS]].itertuples(index=False, name=None)
        require(all(int(ln) == int(sv) + int(nv) + int(ns) for ln, sv, nv, ns in values),
                f"Identidad contable {prefix}no válida")
    require(len(frame) == report.get("analytical_rows") and totals(frame) == report.get("analytical_totals"),
            "Las filas o los totales analíticos T06 no coinciden")
    frame = frame.sort_values(KEYS).reset_index(drop=True)
    return frame, report, hashes


def derive(frame):
    frame = frame.copy()
    frame["known_denominator"] = frame["SV"] + frame["NV"]
    frame["participation_pct"] = 100 * frame["SV"] / frame["known_denominator"].replace(0, np.nan)
    frame["unspecified_pct"] = 100 * frame["NS"] / frame["LN"].replace(0, np.nan)
    frame["known_coverage_pct"] = 100 * frame["known_denominator"] / frame["LN"].replace(0, np.nan)
    return frame


def prepare_scenarios(frame):
    datasets, accounting = {}, {}
    for name, (minimum, coverage) in SCENARIOS.items():
        source = frame.copy()
        if name == "without_age_over_110":
            for field in COUNTS:
                source[field] -= source[f"age_over_110_{field}"]
        source = derive(source)
        valid = source["known_denominator"].ge(minimum) & source["known_coverage_pct"].ge(coverage)
        datasets[name] = source.loc[valid].copy()
        accounting[name] = {
            "minimum_known_denominator": minimum, "minimum_coverage_pct": coverage,
            "eligible_groups": int(valid.sum()), "excluded_groups": int((~valid).sum()),
            "eligible_totals": totals(source.loc[valid]), "excluded_totals": totals(source.loc[~valid]),
            "removed_age_over_110_totals": {field: totals(frame)[field] - totals(source)[field] for field in COUNTS},
        }
    return datasets, accounting


def kmeans_model(k, seed=0):
    return KMeans(n_clusters=k, random_state=seed, n_init=20, max_iter=300,
                  tol=1e-4, algorithm="lloyd")


def fit(frame, k, method, scenario="baseline", seed=0):
    features = ["participation_pct"]
    if scenario == "participation_unspecified":
        features.append("unspecified_pct")
    matrix = frame[features].to_numpy(dtype=float)
    require(len(matrix) > k and len(np.unique(matrix, axis=0)) >= k,
            "No hay suficientes grupos elegibles distintos")
    if len(features) > 1:
        matrix = StandardScaler().fit_transform(matrix)
    if method == "kmeans":
        model = kmeans_model(k, seed)
        weights = frame["LN"].to_numpy(dtype=float) if scenario == "ln_weighted" else None
        model.fit(matrix, sample_weight=weights)
        labels = model.labels_
    else:
        require(scenario != "ln_weighted", "Ward no tiene aquí un equivalente con ponderación de muestras")
        labels = AgglomerativeClustering(n_clusters=k, linkage="ward").fit_predict(matrix)
    require(len(np.unique(labels)) == k, "El ajuste no produjo el k solicitado")
    return pd.Series(labels, index=frame.index), matrix


def agreement(left, right):
    common = left.index.intersection(right.index)
    require(len(common) > 1, "No hay suficientes grupos comunes para ARI")
    return float(adjusted_rand_score(left.loc[common], right.loc[common]))


def distribution(values, unavailable=None):
    return {"evaluated": len(values), "min": float(min(values)) if values else None,
            "median": float(np.median(values)) if values else None,
            "max": float(max(values)) if values else None, "unavailable": unavailable or []}


def metrics(frame, labels, matrix):
    sizes = labels.value_counts()
    population = frame.groupby(labels)["LN"].sum()
    return {"groups": len(frame), "silhouette": float(silhouette_score(matrix, labels)),
            "minimum_cluster_groups": int(sizes.min()),
            "minimum_cluster_ln_share_pct": float(100 * population.min() / population.sum())}


def cluster_summaries(frame, labels):
    summaries = []
    population = totals(frame)["LN"]
    for label in sorted(labels.unique()):
        selected = frame.loc[labels.eq(label)]
        counts = totals(selected)
        shares = {}
        for field, title in [("SEXO", "sex"), ("age_band", "age")]:
            shares[title + "_ln_share_pct"] = {
                str(key): 100 * sum(map(int, group["LN"])) / counts["LN"]
                for key, group in selected.groupby(field, sort=True)
            }
        summaries.append({
            **counts, **shares, "groups": len(selected), "entities": int(selected["EDOCVE"].nunique()),
            "ln_share_pct": 100 * counts["LN"] / population,
            "participation_pct": 100 * counts["SV"] / (counts["SV"] + counts["NV"]),
            "participation_min_pct": float(selected["participation_pct"].min()),
            "participation_max_pct": float(selected["participation_pct"].max()),
            "unspecified_pct": 100 * counts["NS"] / counts["LN"],
        })
    # El orden local facilita la lectura; no son identificadores de perfiles finales de T08.
    return sorted(summaries, key=lambda item: item["participation_pct"])


def candidate(frame, datasets, k, method):
    labels, matrix = fit(frame, k, method)
    seed_scores = []
    if method == "kmeans":
        for seed in SEEDS[1:]:
            other, _ = fit(frame, k, method, seed=seed)
            seed_scores.append(agreement(labels, other))
    entity_scores, unavailable = [], []
    for entity in sorted(frame["EDOCVE"].unique()):
        retained = frame.loc[frame["EDOCVE"].ne(entity)]
        try:
            other, _ = fit(retained, k, method)
            entity_scores.append(agreement(labels, other))
        except ValueError as error:
            unavailable.append({"entity": entity, "reason": str(error)})
    sensitivities = []
    for name, selected in datasets.items():
        if name == "baseline":
            continue
        result = {"scenario": name}
        if name == "ln_weighted" and method == "ward":
            result.update(status="not_applicable", reason="Ward no está ponderado; no se sustituye por una aproximación")
        else:
            try:
                other, other_matrix = fit(selected, k, method, name)
                result.update(status="ok", **metrics(selected, other, other_matrix),
                              common_groups=len(labels.index.intersection(other.index)),
                              ari_on_common_groups=agreement(labels, other))
            except ValueError as error:
                result.update(status="unavailable", reason=str(error))
        sensitivities.append(result)
    return {
        "method": method, "k": k, "status": "ok", **metrics(frame, labels, matrix),
        "seed_stability_ari": distribution(seed_scores) if method == "kmeans" else None,
        "leave_entity_out_ari": distribution(entity_scores, unavailable),
        "clusters": cluster_summaries(frame, labels), "sensitivities": sensitivities,
    }, labels


def compare(root, input_path, run_name):
    root = root.resolve()
    bundle = (root / input_path).resolve()
    require(bundle.is_relative_to(root / "data" / "processed"), "La entrada debe ser un paquete T06 dentro de data/processed")
    destination = root / "outputs" / run_name
    require(not destination.exists(), "La salida ya existe; elija otro --run-name")
    frame, source_report, hashes = load_input(bundle)
    datasets, accounting = prepare_scenarios(frame)
    reference = datasets["baseline"]
    require(len(reference) > 6 and reference["participation_pct"].nunique() >= 6,
            "El escenario base necesita más de seis grupos elegibles y seis tasas distintas")
    candidates, method_agreement = [], []
    with threadpool_limits(limits=1):
        for k in (4, 5, 6):
            partitions = {}
            for method in ("kmeans", "ward"):
                result, partitions[method] = candidate(reference, datasets, k, method)
                candidates.append(result)
            method_agreement.append({"k": k, "ari": agreement(partitions["kmeans"], partitions["ward"])})
    report = {
        "contract": "t07-comparison/v1", "selection": "deferred_to_T08", "internal_only": True,
        "input": {"directory": bundle.relative_to(root).as_posix(), "rows": len(frame),
                  "unit": ["AELEC", *KEYS], "totals": totals(frame), **hashes,
                  "t06_pipeline_sha256": source_report.get("pipeline_sha256"),
                  "source": source_report.get("source"), "manifest_sha256": source_report.get("manifest_sha256")},
        "environment": {"python": sys.version.split()[0], "pandas": pd.__version__,
                        "numpy": np.__version__, "sklearn": sklearn.__version__},
        "pipeline_sha256": sha256(Path(__file__)),
        "config": {
            "baseline_features": ["participation_pct"], "baseline_scaling": "ninguno; una variable porcentual",
            "baseline_weighting": "igual peso por grupo agregado", "seeds": SEEDS,
            "kmeans": {"n_init": 20, "max_iter": 300, "tol": 1e-4, "algorithm": "lloyd", "reference_seed": 0},
            "ward": {"linkage": "ward", "distance": "euclidean", "weighting": "igual peso por grupo"},
            "feature_sensitivity": "StandardScaler reajustado a participation_pct y unspecified_pct",
            "weight_sensitivity": "Pesos muestrales LN solo para KMeans; sin cambio de escala",
            "stability": "ARI sobre grupos comunes; reajuste al excluir cada entidad; no es incertidumbre muestral",
            "thresholds": "Heurísticas exploratorias, no garantías estadísticas ni una política de divulgación",
        },
        "eligibility": accounting, "candidates": candidates, "method_agreement": method_agreement,
        "limitations": [
            "Estratos agregados de participación de 2024, no tipos de ciudadanos individuales ni explicaciones causales.",
            "Edad, sexo y entidad solo describen la composición; las distancias no incluyen identificadores ni conteos poblacionales.",
            "La participación no especificada no es abstención; los grupos pequeños o no elegibles siguen contabilizados, no fusionados.",
            "No se exportan asignaciones por fila ni tasas de grupos pequeños; la política de publicación sigue sin resolverse.",
            "La silueta no está ponderada ni siquiera en ajustes ponderados por LN y no es comparable entre espacios de variables.",
            "Una estabilidad o silueta alta no demuestra la existencia de cuatro a seis grupos naturales.",
        ],
    }
    require(sha256(bundle / "table.csv") == hashes["table_sha256"]
            and sha256(bundle / "report.json") == hashes["report_sha256"], "Las entradas cambiaron durante la comparación")
    parent = destination.parent
    parent.mkdir(parents=True, exist_ok=True)
    # La preparación en outputs/ ignorado, en el mismo sistema de archivos, permite un renombrado atómico sin sobrescritura.
    with tempfile.TemporaryDirectory(dir=parent, prefix=".compare-") as temporary:
        staging = Path(temporary) / "bundle"
        staging.mkdir()
        (staging / "report.json").write_text(
            json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False) + "\n", encoding="utf-8")
        fields = ["method", "k", "scenario", "status", "groups", "silhouette", "minimum_cluster_groups",
                  "minimum_cluster_ln_share_pct", "common_groups", "ari_on_common_groups"]
        with (staging / "comparison.csv").open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
            writer.writeheader()
            for item in candidates:
                writer.writerow({**item, "scenario": "baseline"})
                for sensitivity in item["sensitivities"]:
                    writer.writerow({"method": item["method"], "k": item["k"], **sensitivity})
        require(not destination.exists(), "La salida ya existe")
        staging.rename(destination)
    return {"status": "ok", "directory": destination.relative_to(root).as_posix(),
            "candidates": len(candidates), "eligible_groups": len(reference), "selection": "deferred_to_T08"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Raíz del proyecto (también admite datos de prueba aislados)")
    parser.add_argument("--input", default="data/processed/ccpc_all/2024",
                        help="Directorio del paquete T06 dentro de data/processed, relativo a --root; predeterminado: ccpc_all/2024")
    parser.add_argument("--run-name", default="t07_comparison", help="Nombre de un directorio nuevo dentro de outputs; nunca se sobrescribe")
    arguments = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", arguments.run_name):
        parser.error("--run-name debe ser un nombre alfanumérico simple con guiones o guiones bajos opcionales")
    try:
        result = compare(arguments.root, arguments.input, arguments.run_name)
    except (ValueError, OSError, KeyError, OverflowError, TypeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
