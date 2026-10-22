"""Valida la fuente CCPC 2024 y exporta los grupos analíticos observados sin conexión."""

import argparse
from collections import defaultdict
import csv
import io
import json
from pathlib import Path
import re
import sys
import tempfile
import warnings
import zipfile

import pandas as pd

from download_ccpc import sha256


ROOT = Path(__file__).resolve().parents[1]
COLUMNS = "AELEC FELECCION EDOCVE EDONOM MPIOCVE MPIONOM SECCION TIPOSEC DEF DEL SEXO EDAD LN SV NV NS".split()
COUNTS = ["LN", "SV", "NV", "NS"]
BANDS = ["18-24", "25-34", "35-44", "45-59", "60+"]
MAX_INTEGER = 2**63 - 1


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integers(values, field, minimum, maximum=MAX_INTEGER, district=False):
    """Acepta solo enteros exactos; los blancos distritales siguen como faltantes, nunca ceros."""
    text = values.str.strip()
    if field in COUNTS:
        require(not text.eq("").any(), f"{field}: conteo faltante")
        numeric = text.str.fullmatch(r"-?[0-9]+(?:\.[0-9]+)?")
        require(numeric.all(), f"{field}: token desconocido o supresión no documentada")
        require(text.str.fullmatch(r"[0-9]+").all(), f"{field}: conteo inválido")
    elif district:
        text = text.replace("", pd.NA).str.replace(r"\.0+$", "", regex=True)
    require(text.dropna().str.fullmatch(r"[0-9]+").all(), f"{field}: entero inválido")
    # Los enteros que admiten nulos evitan pérdida de precisión al convertir identificadores distritales.
    numbers = text.astype("Int64")
    require(numbers.dropna().between(minimum, maximum).all(), f"{field}: fuera de rango")
    return numbers if district else numbers.astype("int64")


def normalize(frame):
    require(list(frame.columns) == COLUMNS, "Cambió el esquema de columnas")
    for field in ("FELECCION", "EDONOM", "MPIONOM"):
        require(not frame[field].str.strip().eq("").any(), f"{field}: etiqueta faltante")
    limits = {"AELEC": (2024, 2024), "EDOCVE": (1, 32), "MPIOCVE": (1, 570),
              "SECCION": (1, MAX_INTEGER), "SEXO": (0, 2), "EDAD": (18, MAX_INTEGER)}
    for field, (low, high) in limits.items():
        frame[field] = integers(frame[field], field, low, high)
    for field, high in (("DEF", 40), ("DEL", 45)):
        frame[field] = integers(frame[field], field, 1, high, district=True)
    require(frame["TIPOSEC"].isin(["U", "M", "R"]).all(), "TIPOSEC: categoría inválida")
    for field in COUNTS:
        frame[field] = integers(frame[field], field, 1 if field == "LN" else 0)
    # La resta con residuos no negativos evita desbordamientos en la comprobación contable.
    remainder = frame["LN"] - frame["SV"]
    require((remainder >= 0).all() and (remainder >= frame["NV"]).all()
            and ((remainder - frame["NV"]) == frame["NS"]).all(), "No se cumple LN = SV + NV + NS")
    return frame


def consistent(mapping, key, value, label):
    require(key not in mapping or mapping[key] == value, f"Inconsistencia en {label}")
    mapping[key] = value


def aggregate_member(archive, member, chunk_size, groups, report, entities):
    """La fuente tiene un CSV por entidad: limita el almacenamiento de claves exactas a una entidad."""
    keys, sections, municipalities, names = set(), {}, {}, {}
    entity = None
    row_count = 0
    with archive.open(member) as binary, io.TextIOWrapper(binary, encoding="utf-8-sig", newline="") as stream:
        require(next(csv.reader(stream), None) == COLUMNS, f"{member}: cambió el esquema")
        stream.seek(0)
        with warnings.catch_warnings():
            warnings.simplefilter("error", pd.errors.ParserWarning)
            chunks = pd.read_csv(stream, dtype=str, keep_default_na=False, chunksize=chunk_size,
                                 index_col=False, skip_blank_lines=False)
            for frame in chunks:
                frame = normalize(frame)
                states = frame["EDOCVE"].unique()
                require(len(states) == 1, f"{member}: se esperaba una entidad por CSV")
                current = int(states[0])
                if entity is None:
                    require(current not in entities, "Hay una entidad repetida entre CSV")
                    entity = current
                    entities.add(current)
                require(current == entity, f"{member}: cambió la entidad dentro del CSV")
                new_keys = set(frame[["SECCION", "SEXO", "EDAD"]].itertuples(index=False, name=None))
                require(len(new_keys) == len(frame) and keys.isdisjoint(new_keys), "Se encontró una clave duplicada")
                keys.update(new_keys)
                for state, name in frame[["EDOCVE", "EDONOM"]].drop_duplicates().itertuples(index=False, name=None):
                    consistent(names, state, name, "nombre de entidad")
                for municipality, name in frame[["MPIOCVE", "MPIONOM"]].drop_duplicates().itertuples(index=False, name=None):
                    consistent(municipalities, municipality, name, "nombre municipal")
                geography = frame[["SECCION", "MPIOCVE", "TIPOSEC", "DEF", "DEL"]].drop_duplicates()
                for section, municipality, kind, federal, local in geography.itertuples(index=False, name=None):
                    attributes = (municipality, kind, None if pd.isna(federal) else int(federal),
                                  None if pd.isna(local) else int(local))
                    consistent(sections, section, attributes, "atributos de sección")
                report["election_date_literals"].update(frame["FELECCION"].unique())
                extreme = frame["EDAD"] > 110
                unknown = frame["SV"].eq(0) & frame["NV"].eq(0)
                report["age_over_110_rows"] += int(extreme.sum())
                report["zero_known_denominator_rows"] += int(unknown.sum())
                for field in ("DEF", "DEL"):
                    report["missing_district_rows"][field] += int(frame[field].isna().sum())
                for field in COUNTS:
                    report["source_totals"][field] += sum(map(int, frame[field]))
                    report["zero_count_rows"][field] += int(frame[field].eq(0).sum())
                    frame[f"age_over_110_{field}"] = frame[field].where(extreme, 0)
                frame["age_band"] = pd.cut(frame["EDAD"], [17, 24, 34, 44, 59, float("inf")], labels=BANDS)
                frame["source_rows"] = 1
                frame["age_over_110_rows"] = extreme.astype(int)
                measures = COUNTS + [f"age_over_110_{field}" for field in COUNTS] + ["source_rows", "age_over_110_rows"]
                # Las sumas de enteros de Python mantienen los totales exactos, sin desbordamientos de int64.
                frame[measures] = frame[measures].astype(object)
                summed = frame.groupby(["EDOCVE", "SEXO", "age_band"], observed=True)[measures].sum()
                for key, values in summed.iterrows():
                    for measure in measures:
                        groups[key][measure] += int(values[measure])
                row_count += len(frame)
    require(row_count > 0, f"{member}: CSV vacío")
    report["members"].append({"member": member, "entity": f"{entity:02d}", "rows": row_count})
    report["source_rows"] += row_count


def analytical_rows(groups):
    rows = []
    for (state, sex, band), counts in sorted(groups.items(), key=lambda pair: (pair[0][0], pair[0][1], BANDS.index(pair[0][2]))):
        known = counts["SV"] + counts["NV"]
        rows.append({
            "AELEC": 2024, "EDOCVE": f"{state:02d}", "SEXO": str(sex), "age_band": band,
            **counts, "known_denominator": known,
            "participation_pct": f"{100 * counts['SV'] / known:.8f}" if known else "",
            "abstention_pct": f"{100 * counts['NV'] / known:.8f}" if known else "",
            "unspecified_pct": f"{100 * counts['NS'] / counts['LN']:.8f}",
            "known_coverage_pct": f"{100 * known / counts['LN']:.8f}",
        })
    return rows


def clean(root, chunk_size, run_name):
    root = root.resolve()
    parent = root / "data" / "processed"
    destination = parent / run_name
    require(not destination.exists(), "La salida ya existe; usa otro --run-name para conservarla")
    manifest = root / "data" / "sources.json"
    manifest_hash = sha256(manifest)
    entries = json.loads(manifest.read_text(encoding="utf-8"))
    selected = [entry for entry in entries if entry["election_year"] == 2024]
    require(len(selected) == 1, "Se requiere una única fuente 2024 en el manifiesto")
    entry = selected[0]
    source = (root / entry["local_path"]).resolve()
    require(source.is_relative_to((root / "data" / "raw").resolve()), "La fuente debe estar en data/raw")
    require(source.stat().st_size == entry["bytes"] and sha256(source) == entry["sha256"],
            "Falló la comprobación de integridad de la fuente")
    report = {
        "election_year": 2024, "unit": ["EDOCVE", "SEXO", "age_band"],
        "manifest_sha256": manifest_hash, "pipeline_sha256": sha256(Path(__file__)),
        "python": sys.version.split()[0], "pandas": pd.__version__,
        "source": {key: entry[key] for key in ("local_path", "sha256", "bytes")},
        "source_rows": 0, "excluded_rows": 0, "exclusions": [],
        "source_totals": dict.fromkeys(COUNTS, 0), "zero_count_rows": dict.fromkeys(COUNTS, 0),
        "missing_district_rows": {"DEF": 0, "DEL": 0}, "age_over_110_rows": 0,
        "zero_known_denominator_rows": 0, "election_date_literals": set(), "members": [],
        "suppression_policy": "undocumented; unknown count tokens are rejected, never imputed",
        "transformations": [
            "Select the 2024 manifest entry; leave other elections untouched.",
            "Normalize integer identifiers; export EDOCVE as two digits and SEXO as a category.",
            "Normalize blank districts to missing; preserve literal election dates.",
            "Preserve valid zero counts and nonbinary sex code 2; never create unobserved combinations.",
            "Band ages as 18-24, 25-34, 35-44, 45-59, 60+; retain and flag ages over 110.",
            "Sum counts before rates; retain rows without known participation; undefined rates are blank.",
        ],
        "limitations": [
            "Identifier ranges do not validate external geographic catalogs or exhaustive population coverage.",
            "NS is unknown participation, not abstention or documented statistical suppression.",
            "Review small-group disclosure before publication; outputs are for internal analysis.",
            "No coverage exclusion threshold or clustering decision is imposed in T06.",
        ],
    }
    groups, entities = defaultdict(lambda: defaultdict(int)), set()
    with zipfile.ZipFile(source) as archive:
        members = archive.namelist()
        require(members == entry["members"] and len(members) == len(set(members)), "Cambió el inventario del ZIP")
        csvs = sorted(member for member in members if member.lower().endswith(".csv"))
        require(len(csvs) == 32, "Se requieren 32 CSV de entidades para 2024")
        for member in csvs:
            aggregate_member(archive, member, chunk_size, groups, report, entities)
    require(entities == set(range(1, 33)), "La cobertura debe incluir las 32 entidades")
    rows = analytical_rows(groups)
    report["election_date_literals"] = sorted(report["election_date_literals"])
    report["analytical_rows"] = len(rows)
    report["analytical_totals"] = {field: sum(row[field] for row in rows) for field in COUNTS}
    require(report["source_totals"] == report["analytical_totals"], "No coinciden los totales analíticos")
    require(sha256(source) == entry["sha256"] and sha256(manifest) == manifest_hash, "Cambió la integridad durante el análisis")
    report["checks"] = dict.fromkeys([
        "source_integrity_before_after", "schema", "key_uniqueness_exact", "domains",
        "geographic_consistency", "accounting_identity", "entity_coverage", "totals_reconciled",
    ], True)
    # Publica el paquete completo solo si todas las comprobaciones pasan. Nunca reemplaza una ejecución previa.
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=parent, prefix=".clean-") as temporary:
        staging = Path(temporary) / "bundle"
        staging.mkdir()
        with (staging / "table.csv").open("w", encoding="utf-8", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=list(rows[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        report["table_sha256"] = sha256(staging / "table.csv")
        (staging / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
        require(not destination.exists(), "La salida ya existe")
        staging.rename(destination)
    return {"status": "ok", "directory": destination.relative_to(root).as_posix(),
            "source_rows": report["source_rows"], "analytical_rows": len(rows),
            "totals": report["analytical_totals"]}


def positive_integer(value):
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("El tamaño de bloque debe ser positivo")
    return parsed


def run_label(value):
    if not re.fullmatch(r"[A-Za-z0-9_-]+", value):
        raise argparse.ArgumentTypeError("Usa solo letras ASCII, números, guion o guion bajo")
    return value


def main():
    parser = argparse.ArgumentParser(description="Limpia y valida CCPC 2024 sin modificar originales ni usar la red.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Raíz local con data/sources.json y data/raw")
    parser.add_argument("--chunk-size", type=positive_integer, default=150000, help="Filas por bloque (predeterminado: 150000)")
    parser.add_argument("--run-name", type=run_label, default="ccpc_2024", help="Carpeta nueva en data/processed (predeterminada: ccpc_2024)")
    args = parser.parse_args()
    try:
        print(json.dumps(clean(args.root, args.chunk_size, args.run_name), ensure_ascii=True))
    except (OSError, ValueError, TypeError, KeyError, OverflowError, zipfile.BadZipFile, pd.errors.ParserWarning) as error:
        print(f"Error de limpieza: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
