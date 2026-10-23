"""Extiende T07 con ajustes anuales separados y diagnósticos de referencia fija, nunca historias personales."""

import argparse
import csv
from itertools import combinations
import json
from pathlib import Path
import re
import sys
import tempfile

import numpy as np
import pandas as pd
import sklearn
from threadpoolctl import threadpool_limits

import compare_segments as engine
from clean_ccpc import COUNTS, require
from download_ccpc import sha256


ROOT = Path(__file__).resolve().parents[1]
SERIES = [("2012_2018_2024", (2012, 2018, 2024), 2024),
          ("2009_2015_2021", (2009, 2015, 2021), 2021)]


def keyed(frame, values):
    return pd.Series(np.asarray(values), index=pd.MultiIndex.from_frame(frame[engine.KEYS]))


def fixed_reference(name, years, reference_year, datasets, k):
    reference = datasets[reference_year]["baseline"]
    model = engine.kmeans_model(k)
    model.fit(reference[["participation_pct"]].to_numpy())
    centers = np.sort(model.cluster_centers_.ravel())
    boundaries = (centers[:-1] + centers[1:]) / 2
    summaries, partitions = {}, {}
    for year in years:
        frame = datasets[year]["baseline"]
        distances = (frame["participation_pct"].to_numpy()[:, None] - centers[None, :]) ** 2
        labels = pd.Series(np.argmin(distances, axis=1) + 1, index=frame.index)
        partitions[year] = keyed(frame, labels)
        rows = []
        for rank in range(1, k + 1):
            selected = frame.loc[labels.eq(rank)]
            if len(selected):
                summary = engine.cluster_summaries(selected, labels.loc[selected.index])[0]
                summary["ln_share_pct"] = 100 * summary["LN"] / engine.totals(frame)["LN"]
            else:
                summary = {**dict.fromkeys(COUNTS, 0), "groups": 0, "entities": 0,
                           "ln_share_pct": 0, "participation_pct": None,
                           "participation_min_pct": None, "participation_max_pct": None,
                           "unspecified_pct": None, "age_ln_share_pct": {}, "sex_ln_share_pct": {}}
            rows.append({"reference_rank": rank, **summary})
        summaries[str(year)] = rows
    return {
        "series": name, "reference_year": reference_year, "k": k,
        "centroids_pct": centers.tolist(), "boundaries_pct": boundaries.tolist(),
        "parameters": model.get_params(), "years": summaries,
        "assignment": "Centroide fijo más cercano; los empates eligen el rango de menor participación; los rangos no son identificadores de perfiles finales",
    }, partitions


def paired_diagnostic(name, from_year, to_year, reference_year, k, datasets, fixed, annual_labels):
    left = datasets[from_year]["baseline"].set_index(engine.KEYS)
    right = datasets[to_year]["baseline"].set_index(engine.KEYS)
    common = left.index.intersection(right.index)
    result = {"series": name, "from_year": from_year, "to_year": to_year,
              "reference_year": reference_year, "k": k, "common_groups": len(common),
              "from_only_groups": len(left) - len(common), "to_only_groups": len(right) - len(common)}
    if len(common) < 2:
        return {**result, "status": "unavailable", "reason": "Menos de dos claves agregadas elegibles comunes"}
    start, end = left.loc[common, "participation_pct"], right.loc[common, "participation_pct"]
    delta = end - start
    before, after = fixed[from_year].loc[common], fixed[to_year].loc[common]
    movements = pd.crosstab(before, after)
    return {
        **result, "status": "ok", "mean_delta_pp": float(delta.mean()),
        "median_delta_pp": float(delta.median()),
        "spearman_rate_rank": float(start.rank().corr(end.rank())) if start.nunique() > 1 and end.nunique() > 1 else None,
        "common_ln_from": sum(map(int, left.loc[common, "LN"])),
        "common_ln_to": sum(map(int, right.loc[common, "LN"])),
        "same_reference_band_group_pct": float(100 * before.eq(after).mean()),
        "annual_ari": {method: engine.agreement(annual_labels[from_year, k, method], annual_labels[to_year, k, method])
                       for method in ("kmeans", "ward")},
        "aggregate_key_movements": [
            {"from_rank": int(old), "to_rank": int(new), "groups": int(movements.loc[old, new])}
            for old in movements.index for new in movements.columns if movements.loc[old, new] > 0
        ],
    }


def write_csv(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def compare_history(root, input_path, run_name):
    root = root.resolve()
    source = (root / input_path).resolve()
    require(source.is_relative_to(root / "data" / "processed"), "La entrada debe estar dentro de data/processed")
    destination = root / "outputs" / run_name
    require(not destination.exists(), "La salida ya existe; elija otro --run-name")
    annual, datasets, annual_labels, fingerprints = {}, {}, {}, {}
    # Valida los seis paquetes antes de ajustar modelos o crear cualquier directorio de salida.
    for _, years, _ in SERIES:
        for year in years:
            frame, provenance, hashes = engine.load_input(source / str(year), year=year)
            datasets[year], accounting = engine.prepare_scenarios(frame)
            base = datasets[year]["baseline"]
            require(len(base) > 6 and base["participation_pct"].nunique() >= 6,
                    f"El escenario base de {year} necesita más de seis grupos elegibles y seis tasas distintas")
            fingerprints[year] = hashes
            annual[str(year)] = {
                "input": {"election_year": year, "directory": (source / str(year)).relative_to(root).as_posix(),
                          "rows": len(frame), "totals": engine.totals(frame), **hashes,
                          "source": provenance.get("source"), "manifest_sha256": provenance.get("manifest_sha256"),
                          "t06_pipeline_sha256": provenance.get("pipeline_sha256")},
                "eligibility": accounting, "candidates": [],
            }
    references, pairs = [], []
    with threadpool_limits(limits=1):
        for year, scenarios in datasets.items():
            base = scenarios["baseline"]
            for k in (4, 5, 6):
                for method in ("kmeans", "ward"):
                    result, labels = engine.candidate(base, scenarios, k, method)
                    annual[str(year)]["candidates"].append(result)
                    annual_labels[year, k, method] = keyed(base, labels)
        for name, years, reference_year in SERIES:
            for k in (4, 5, 6):
                reference, partitions = fixed_reference(name, years, reference_year, datasets, k)
                references.append(reference)
                for start, end in combinations(years, 2):
                    pairs.append(paired_diagnostic(name, start, end, reference_year, k,
                                                   datasets, partitions, annual_labels))
    report = {
        "contract": "t07-history/v1", "selection": "deferred_to_T08", "internal_only": True,
        "pipeline_sha256": sha256(Path(__file__)), "comparison_engine_sha256": sha256(Path(engine.__file__)),
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__,
                        "pandas": pd.__version__, "sklearn": sklearn.__version__},
        "config": {"seeds": engine.SEEDS, "annual_features": ["participation_pct"],
                    "annual_weighting": "igual peso por grupo agregado", "scenarios": engine.SCENARIOS,
                   "kmeans_parameters_example_k6": engine.kmeans_model(6).get_params(),
                    "ward": "Ward euclidiano sin ponderación; no se sustituye por una predicción fuera de muestra",
                    "fixed_reference": "KMeans con semilla 0 y los mismos parámetros anuales; referencia ajustada una vez por serie y k",
                   "unit": ["AELEC", *engine.KEYS]},
        "series": [{"name": name, "years": list(years), "reference_year": reference} for name, years, reference in SERIES],
        "annual": annual, "references": references, "pairs": pairs,
        "limitations": [
            "Las elecciones anuales nunca se agrupan; aquí no tiene sentido un total poblacional entre elecciones.",
            "Las referencias usan retrospectivamente el último año de cada serie; no es una validación predictiva fuera del período.",
            "Los rangos fijos conservan las definiciones de participación, mientras que las etiquetas de conglomerados anuales no comparten significado numérico.",
            "Los movimientos cuentan claves agregadas coincidentes de entidad/sexo/edad, no personas, cohortes ni historias individuales de voto.",
            "La ausencia histórica del código de sexo 2 no es población cero; no se fabrican categorías ni observaciones faltantes.",
            "La cobertura, la participación no especificada y las referencias geográficas cambian; las coincidencias de claves agregadas no son territorios longitudinales validados.",
            "Los umbrales de elegibilidad son exploratorios, no garantías de divulgación; las salidas siguen siendo internas.",
            "Los rangos estables, el ARI o los estratos recurrentes no demuestran causalidad, tipos naturales de ciudadanos ni efectos de intervenciones.",
        ],
    }
    for year, hashes in fingerprints.items():
        require(sha256(source / str(year) / "table.csv") == hashes["table_sha256"]
                and sha256(source / str(year) / "report.json") == hashes["report_sha256"],
                 f"La entrada de {year} cambió durante la comparación")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent, prefix=".history-") as temporary:
        staging = Path(temporary) / "bundle"
        staging.mkdir()
        (staging / "report.json").write_text(
            json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False) + "\n", encoding="utf-8")
        annual_rows = []
        for year, result in annual.items():
            for candidate in result["candidates"]:
                annual_rows.append({"year": year, "scenario": "baseline", **candidate})
                annual_rows.extend({"year": year, "method": candidate["method"], "k": candidate["k"], **item}
                                   for item in candidate["sensitivities"])
        write_csv(staging / "annual_comparison.csv", ["year", "method", "k", "scenario", "status", "groups", "silhouette",
                  "minimum_cluster_groups", "minimum_cluster_ln_share_pct", "common_groups", "ari_on_common_groups"], annual_rows)
        fixed_rows = []
        for reference in references:
            for year, rows in reference["years"].items():
                fixed_rows.extend({"series": reference["series"], "reference_year": reference["reference_year"],
                                   "year": year, "k": reference["k"], **row} for row in rows)
        write_csv(staging / "fixed_reference.csv", ["series", "reference_year", "year", "k", "reference_rank",
                  "groups", *COUNTS, "ln_share_pct", "participation_pct", "unspecified_pct"], fixed_rows)
        write_csv(staging / "pairwise.csv", ["series", "reference_year", "from_year", "to_year", "k", "status", "common_groups",
                  "from_only_groups", "to_only_groups", "mean_delta_pp", "median_delta_pp", "spearman_rate_rank",
                  "same_reference_band_group_pct", "annual_kmeans_ari", "annual_ward_ari"],
                  [{**pair, **{f"annual_{method}_ari": score for method, score in pair.get("annual_ari", {}).items()}} for pair in pairs])
        require(not destination.exists(), "La salida ya existe")
        staging.rename(destination)
    return {"status": "ok", "directory": destination.relative_to(root).as_posix(), "annual_candidates": 36,
            "reference_solutions": len(references), "pairwise_comparisons": len(pairs), "selection": "deferred_to_T08"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Raíz del proyecto o de un conjunto sintético aislado de prueba")
    parser.add_argument("--input", default="data/processed/ccpc_all", help="Seis directorios anuales T06 dentro de data/processed, relativos a --root")
    parser.add_argument("--run-name", default="t07_history", help="Directorio nuevo dentro de outputs; las ejecuciones existentes nunca se sobrescriben")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", args.run_name):
        parser.error("--run-name debe ser un nombre alfanumérico simple con guiones o guiones bajos opcionales")
    try:
        result = compare_history(args.root, args.input, args.run_name)
    except (ValueError, OSError, KeyError, OverflowError, TypeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
