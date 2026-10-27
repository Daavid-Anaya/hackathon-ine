"""Diagnóstico interno U/M/R de 2024, sin ajustar ni modificar los perfiles T08."""

import argparse
from collections import defaultdict
import csv
import io
import json
from pathlib import Path
import re
from statistics import median
import sys
import tempfile
import zipfile

import pandas as pd

from clean_ccpc import BANDS, COLUMNS, COUNTS, normalize, require, sha256
from compare_history import write_csv
from compare_segments import KEYS, load_input
from export_profiles import confined


ROOT = Path(__file__).resolve().parents[1]
TYPES = ("U", "M", "R")
FIELDS = ["TIPOSEC", *COUNTS, "participation_pct", "unspecified_pct", "ln_share_pct",
          "eligible_strata", "common_known_share_pct", "common_participation_pct",
          "standardized_participation_pct"]
LIMITATIONS = [
    "Diagnóstico interno pendiente de revisión de divulgación; no autoriza publicación ni envío externo.",
    "TIPOSEC describe secciones, no atributos individuales, municipios homogéneos ni causas de participación.",
    "Urbana, mixta y rural son categorías separadas; no se ordenan numéricamente ni se fusionan.",
    "La tasa usa SV/(SV+NV); NS es participación desconocida, no abstención.",
    "La estandarización usa solo estratos entidad-sexo-edad elegibles presentes en los tres tipos; no imputa ausencias.",
    "D>=30 y cobertura conocida>=80% son heurísticas exploratorias, no reglas de confidencialidad.",
    "Las tasas brutas, las de soporte común y las estandarizadas no tienen necesariamente la misma población de referencia.",
    "La comparación es descriptiva: no prueba efectos causales, preferencias, barreras ni trayectorias individuales.",
    "No se ajustan modelos, no se reasignan perfiles y no se generan estrategias dirigidas a grupos demográficos.",
]


def counts(rows):
    return {name: sum(int(row[name]) for row in rows) for name in COUNTS}


def ratio(numerator, denominator):
    return 100 * numerator / denominator if denominator else None


def known(row):
    return row["SV"] + row["NV"]


def aggregate(source, source_report, chunk_size):
    groups = defaultdict(lambda: dict.fromkeys(COUNTS, 0))
    members = {item["member"]: item for item in source_report["members"]}
    seen_rows = 0
    with zipfile.ZipFile(source) as archive:
        csvs = sorted(name for name in archive.namelist() if name.lower().endswith(".csv"))
        require(len(csvs) == len(set(csvs)) and set(csvs) == set(members), "Inventario CSV incompatible con T06")
        for name in csvs:
            member_rows = 0
            with archive.open(name) as binary, io.TextIOWrapper(binary, encoding="utf-8-sig", newline="") as stream:
                require(next(csv.reader(stream), None) == COLUMNS, "Esquema original incompatible")
                stream.seek(0)
                chunks = pd.read_csv(stream, dtype=str, keep_default_na=False, chunksize=chunk_size,
                                     index_col=False, skip_blank_lines=False)
                for frame in chunks:
                    frame = normalize(frame, 2024)
                    require(frame["EDOCVE"].eq(int(members[name]["entity"])).all(), "Entidad incompatible con T06")
                    frame["age_band"] = pd.cut(frame["EDAD"], [17, 24, 34, 44, 59, float("inf")], labels=BANDS)
                    frame[COUNTS] = frame[COUNTS].astype(object)
                    summed = frame.groupby(["EDOCVE", "TIPOSEC", "SEXO", "age_band"], observed=True)[COUNTS].sum()
                    for key, values in summed.iterrows():
                        identity = (f"{key[0]:02d}", key[1], str(key[2]), str(key[3]))
                        for field in COUNTS:
                            groups[identity][field] += int(values[field])
                    member_rows += len(frame)
            require(member_rows == members[name]["rows"], "Cantidad de filas incompatible con T06")
            seen_rows += member_rows
    require(seen_rows == source_report["source_rows"], "Total de filas incompatible con T06")
    rows = [{"EDOCVE": state, "TIPOSEC": kind, "SEXO": sex, "age_band": age, **values}
            for (state, kind, sex, age), values in sorted(groups.items())]
    return rows, seen_rows


def compare(rows):
    by_type = {kind: [row for row in rows if row["TIPOSEC"] == kind] for kind in TYPES}
    eligible = {kind: {tuple(row[key] for key in KEYS): row for row in records
                       if known(row) >= 30 and ratio(known(row), row["LN"]) >= 80}
                for kind, records in by_type.items()}
    common = sorted(set.intersection(*(set(eligible[kind]) for kind in TYPES)))
    reference = {key: sum(known(eligible[kind][key]) for kind in TYPES) for key in common}
    reference_total = sum(reference.values())
    total_ln = counts(rows)["LN"]
    summaries, compositions = [], {}
    for kind in TYPES:
        records = by_type[kind]
        if not records:
            continue
        totals = counts(records)
        selected = [eligible[kind][key] for key in common]
        selected_totals = counts(selected)
        standardized = (sum(reference[key] * ratio(eligible[kind][key]["SV"], known(eligible[kind][key]))
                            for key in common) / reference_total if common else None)
        summaries.append({"TIPOSEC": kind, **totals,
                          "participation_pct": ratio(totals["SV"], known(totals)),
                          "unspecified_pct": ratio(totals["NS"], totals["LN"]),
                          "ln_share_pct": ratio(totals["LN"], total_ln),
                          "eligible_strata": len(eligible[kind]),
                          "common_known_share_pct": ratio(known(selected_totals), known(totals)),
                          "common_participation_pct": ratio(selected_totals["SV"], known(selected_totals)),
                          "standardized_participation_pct": standardized})
        compositions[kind] = {}
        for field in ("SEXO", "age_band"):
            categories = sorted({row[field] for row in records})
            compositions[kind][field] = {category: ratio(sum(row["LN"] for row in records if row[field] == category),
                                                        totals["LN"]) for category in categories}
    pairs = []
    for left, right in (("U", "M"), ("U", "R"), ("M", "R")):
        differences = [ratio(eligible[left][key]["SV"], known(eligible[left][key]))
                       - ratio(eligible[right][key]["SV"], known(eligible[right][key])) for key in common]
        pairs.append({"left": left, "right": right, "common_strata": len(common),
                      "left_higher": sum(value > 1e-10 for value in differences),
                      "right_higher": sum(value < -1e-10 for value in differences),
                      "equal_within_1e_10_pp": sum(abs(value) <= 1e-10 for value in differences),
                      "median_delta_pp_unweighted": median(differences) if differences else None})
    return summaries, compositions, {"strata": len(common), "reference_known_denominator": reference_total,
                                     "paired_differences": pairs}


def diagnose(root, run_name, chunk_size):
    root = root.resolve()
    require(chunk_size > 0, "--chunk-size debe ser positivo")
    destination = confined(root, Path("outputs") / run_name, "outputs")
    require(not destination.exists(), "La salida ya existe; elija otro --run-name")
    bundle = confined(root, Path("data/processed/ccpc_all/2024"), "data/processed")
    frame, source_report, fingerprints = load_input(bundle, year=2024)
    source_metadata = source_report["source"]
    source = confined(root, Path(source_metadata["local_path"]), "data/raw")
    require(source.stat().st_size == source_metadata["bytes"] and sha256(source) == source_metadata["sha256"],
            "La fuente original cambió respecto de T06")
    rows, source_rows = aggregate(source, source_report, chunk_size)
    collapsed = defaultdict(lambda: dict.fromkeys(COUNTS, 0))
    for row in rows:
        for name in COUNTS:
            collapsed[tuple(row[key] for key in KEYS)][name] += row[name]
    expected = {tuple(row[key] for key in KEYS): {name: int(row[name]) for name in COUNTS}
                for row in frame.to_dict("records")}
    require(dict(collapsed) == expected, "La agregación por tipo no reconcilia cada grupo T06")
    summaries, compositions, common = compare(rows)
    report = {"contract": "section-type-diagnostic/v1", "year": 2024, "internal_only": True,
              "publication_authorized": False, "source_rows": source_rows, "totals": counts(rows),
              "input": {**fingerprints, "source_sha256": source_metadata["sha256"]},
              "pipeline_sha256": sha256(Path(__file__)),
              "normalizer_sha256": sha256(Path(__file__).with_name("clean_ccpc.py")),
              "unit": ["EDOCVE", "TIPOSEC", "SEXO", "age_band"],
              "standardization": "Pesos comunes: D agrupado U+M+R por entidad-sexo-edad / D total del soporte común; D=SV+NV",
              "eligibility": {"minimum_known_denominator": 30, "minimum_known_coverage_pct": 80},
              "common_composition": common, "compositions_ln_pct": compositions,
              "limitations": LIMITATIONS}
    require(sha256(source) == source_metadata["sha256"], "La fuente cambió durante el diagnóstico")
    require(sha256(bundle / "table.csv") == fingerprints["table_sha256"]
            and sha256(bundle / "report.json") == fingerprints["report_sha256"], "T06 cambió durante el diagnóstico")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent, prefix=".section-types-") as temporary:
        staging = Path(temporary) / "bundle"
        staging.mkdir()
        write_csv(staging / "summary.csv", FIELDS, summaries)
        (staging / "README.md").write_text(
            "# Diagnóstico interno urbano–mixto–rural de 2024\n\n"
            + "\n".join("- " + limitation for limitation in LIMITATIONS)
            + "\n\nUna tasa vacía es indefinida, no cero. No se exportan microceldas ni asignaciones de perfiles.\n",
            encoding="utf-8")
        report["artifacts_sha256"] = {path.name: sha256(path) for path in sorted(staging.iterdir())}
        (staging / "report.json").write_text(json.dumps(report, sort_keys=True, indent=2, ensure_ascii=True,
                                                       allow_nan=False) + "\n", encoding="utf-8")
        require(not destination.exists(), "La salida ya existe")
        staging.rename(destination)
    return {"status": "internal_diagnostic", "directory": destination.relative_to(root).as_posix(),
            "source_rows": source_rows, "common_strata": common["strata"], "publication_authorized": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Raíz del proyecto o de pruebas aisladas")
    parser.add_argument("--run-name", default="section_types_2024", help="Directorio nuevo en outputs; no se sobrescribe")
    parser.add_argument("--chunk-size", type=int, default=200_000, help="Filas por bloque de lectura; debe ser positivo")
    arguments = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", arguments.run_name):
        parser.error("--run-name debe ser un nombre alfanumérico simple con guiones o guiones bajos opcionales")
    try:
        result = diagnose(arguments.root, arguments.run_name, arguments.chunk_size)
    except (ValueError, OSError, KeyError, TypeError, zipfile.BadZipFile) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
