"""Cruza P01–P05 de T08 con U/M/R en 2024, sin reajustar ni reemplazar perfiles."""

import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
import re
import sys
import tempfile
import zipfile

from clean_ccpc import COUNTS, require, sha256
from compare_history import write_csv
from compare_segments import KEYS, load_input, prepare_scenarios
from diagnose_section_types import aggregate, compare, counts, known, ratio
from export_profiles import confined
from prepare_disclosure_summary import INTERNAL_FILES, read_rows


ROOT = Path(__file__).resolve().parents[1]
PROFILE_IDS = [f"CCPC-2024-K5-P{number:02d}" for number in range(1, 6)]
FIELDS = ["profile_id", "TIPOSEC", *COUNTS, "participation_pct", "unspecified_pct",
          "within_profile_ln_share_pct", "eligible_strata", "common_known_share_pct",
          "common_participation_pct", "standardized_participation_pct"]
LIMITATIONS = [
    "Cruce interno pendiente de revisión de divulgación; no autoriza publicación ni envío externo.",
    "Cada subgrupo U/M/R hereda el perfil T08 de su entidad-sexo-edad; no es una nueva asignación por su propia tasa.",
    "Una tasa del subgrupo puede estar fuera del rango agregado del perfil sin demostrar un error de asignación.",
    "Los porcentajes de LN por tipo usan la LN del perfil; no son proporciones del perfil dentro de cada tipo.",
    "NS es participación desconocida, no abstención. Las tasas vacías son indefinidas, no cero.",
    "La composición común se calcula separadamente dentro de cada perfil; sus tasas no tienen una referencia común entre perfiles.",
    "La estandarización exige soporte U/M/R común elegible por entidad-sexo-edad y no imputa combinaciones ausentes.",
    "D>=30 y cobertura conocida>=80% son heurísticas exploratorias, no reglas de divulgación.",
    "Las diferencias son descriptivas, no causas, preferencias, barreras ni estrategias dirigidas a personas o grupos.",
    "El cruce no estudia municipios ni decide reemplazar el clustering; T08 y sus identificadores permanecen intactos.",
]


def load_profiles(root, frame, fingerprints):
    folder = confined(root, Path("outputs/t08_profiles_final"), "outputs")
    report_path = folder / "report.json"
    protected = {report_path: sha256(report_path)}
    report = json.loads(report_path.read_text(encoding="utf-8"))
    require(report["contract"] == "t08-profiles/v1" and report["internal_only"] is True, "Se requiere T08 interno")
    selection = report["selection"]
    require(all(selection[key] == value for key, value in {
        "year": 2024, "method": "kmeans", "k": 5, "scenario": "baseline", "features": ["participation_pct"]
    }.items()), "Selección T08 no compatible con los perfiles fijos")
    require(all(report["inputs"]["2024"][key] == value for key, value in fingerprints.items()),
            "T08 y el diagnóstico no comparten la misma evidencia T06")
    require(set(report["artifacts_sha256"]) == INTERNAL_FILES, "Inventario T08 incompatible")
    for name, expected in report["artifacts_sha256"].items():
        path = folder / name
        require(sha256(path) == expected, f"El artefacto T08 {name} cambió")
        protected[path] = expected
    profiles = read_rows(folder / "profiles.csv")
    require(len(profiles) == 5 and {row["profile_id"] for row in profiles} == set(PROFILE_IDS),
            "Se requieren los cinco perfiles T08 de 2024")
    indexed_profiles = {row["profile_id"]: row for row in profiles}
    assignments = read_rows(folder / "assignments.csv")
    indexed = {tuple(row[key] for key in KEYS): row for row in assignments}
    baseline = prepare_scenarios(frame)[0]["baseline"]
    expected = {tuple(row[key] for key in KEYS): row for row in baseline.to_dict("records")}
    require(len(indexed) == len(assignments) and set(indexed) == set(expected),
            "Asignaciones T08 incompletas o duplicadas")
    for key, row in indexed.items():
        require(row["year"] == "2024" and row["profile_id"] in PROFILE_IDS
                and all(int(row[name]) == int(expected[key][name]) for name in COUNTS),
                "Asignación T08 incompatible con los conteos de T06")
    total_ln = sum(int(row["LN"]) for row in assignments)
    for identity, profile in indexed_profiles.items():
        selected = [row for row in assignments if row["profile_id"] == identity]
        totals = counts(selected)
        require(profile["year"] == "2024" and selected
                and all(int(profile[name]) == totals[name] for name in COUNTS)
                and int(profile["groups"]) == len(selected)
                and int(profile["entities"]) == len({row["EDOCVE"] for row in selected})
                and math.isclose(float(profile["participation_pct"]), ratio(totals["SV"], known(totals)), abs_tol=1e-9)
                and math.isclose(float(profile["ln_share_pct"]), ratio(totals["LN"], total_ln), abs_tol=1e-9),
                "El resumen del perfil no reconcilia con sus asignaciones")
    return indexed_profiles, indexed, protected


def span(rows, field):
    values = [row[field] for row in rows if row[field] is not None]
    return max(values) - min(values) if len(values) > 1 else None


def cross(root, run_name, chunk_size):
    root = root.resolve()
    require(chunk_size > 0, "--chunk-size debe ser positivo")
    destination = confined(root, Path("outputs") / run_name, "outputs")
    require(not destination.exists(), "La salida ya existe; elija otro --run-name")
    bundle = confined(root, Path("data/processed/ccpc_all/2024"), "data/processed")
    frame, source_report, fingerprints = load_input(bundle, year=2024)
    profiles, assignments, protected = load_profiles(root, frame, fingerprints)
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
    require(dict(collapsed) == expected, "El desglose U/M/R no reconcilia cada grupo T06")
    joined = [{**row, "profile_id": assignments[tuple(row[key] for key in KEYS)]["profile_id"]}
              for row in rows if tuple(row[key] for key in KEYS) in assignments]
    table, evidence = [], {}
    for identity in PROFILE_IDS:
        selected = [row for row in joined if row["profile_id"] == identity]
        totals = counts(selected)
        require(all(totals[name] == int(profiles[identity][name]) for name in COUNTS),
                "El cruce no conserva los conteos del perfil")
        summaries, _, common = compare(selected)
        evidence[identity] = {"parent_participation_pct": ratio(totals["SV"], known(totals)),
                              "totals": totals, "common_composition": common,
                              "raw_type_span_pp": span(summaries, "participation_pct"),
                              "standardized_type_span_pp": span(summaries, "standardized_participation_pct")}
        for summary in summaries:
            row = {"profile_id": identity, **summary}
            row["within_profile_ln_share_pct"] = row.pop("ln_share_pct")
            table.append(row)
    unassigned = [row for row in rows if tuple(row[key] for key in KEYS) not in assignments]
    report = {"contract": "fixed-profile-section-cross/v1", "year": 2024, "internal_only": True,
              "publication_authorized": False, "models_refitted": False, "source_rows": source_rows,
              "source_totals": counts(rows), "assigned_totals": counts(joined),
              "unassigned_totals": counts(unassigned), "profiles": evidence,
              "input": {**fingerprints, "source_sha256": source_metadata["sha256"],
                        "t08_report_sha256": protected[root / "outputs/t08_profiles_final/report.json"]},
              "pipeline_sha256": sha256(Path(__file__)),
              "section_type_helper_sha256": sha256(Path(__file__).with_name("diagnose_section_types.py")),
              "normalizer_sha256": sha256(Path(__file__).with_name("clean_ccpc.py")),
              "limitations": LIMITATIONS}
    require(sha256(source) == source_metadata["sha256"], "La fuente cambió durante el cruce")
    require(sha256(bundle / "table.csv") == fingerprints["table_sha256"]
            and sha256(bundle / "report.json") == fingerprints["report_sha256"], "T06 cambió durante el cruce")
    require(all(sha256(path) == expected for path, expected in protected.items()), "T08 cambió durante el cruce")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent, prefix=".profile-types-") as temporary:
        staging = Path(temporary) / "bundle"
        staging.mkdir()
        write_csv(staging / "cross.csv", FIELDS, table)
        (staging / "README.md").write_text("# Cruce interno de perfiles fijos con tipo de sección\n\n"
                                          + "\n".join("- " + item for item in LIMITATIONS) + "\n", encoding="utf-8")
        report["artifacts_sha256"] = {path.name: sha256(path) for path in sorted(staging.iterdir())}
        (staging / "report.json").write_text(json.dumps(report, sort_keys=True, indent=2, ensure_ascii=True,
                                                       allow_nan=False) + "\n", encoding="utf-8")
        require(not destination.exists(), "La salida ya existe")
        staging.rename(destination)
    return {"status": "internal_fixed_profile_cross", "directory": destination.relative_to(root).as_posix(),
            "profiles": 5, "rows": len(table), "models_refitted": False, "publication_authorized": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Raíz del proyecto o de pruebas aisladas")
    parser.add_argument("--run-name", default="profile_section_types_2024", help="Directorio nuevo en outputs; no se sobrescribe")
    parser.add_argument("--chunk-size", type=int, default=200_000, help="Filas por bloque; debe ser positivo")
    arguments = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", arguments.run_name):
        parser.error("--run-name debe ser un nombre alfanumérico simple con guiones o guiones bajos opcionales")
    try:
        result = cross(arguments.root, arguments.run_name, arguments.chunk_size)
    except (ValueError, OSError, KeyError, TypeError, zipfile.BadZipFile) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
