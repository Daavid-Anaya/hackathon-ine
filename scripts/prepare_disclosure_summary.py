"""Prepara un borrador reducido para difusión; no autoriza ni realiza publicaciones."""

import argparse
import csv
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import json
from pathlib import Path
import re
import sys
import tempfile

from clean_ccpc import require
from compare_history import SERIES, write_csv
from download_ccpc import sha256
from export_profiles import confined


ROOT = Path(__file__).resolve().parents[1]
YEARS = sorted(year for _, years, _ in SERIES for year in years)
INTERNAL_FILES = {"profiles.csv", "assignments.csv", "historical_assignments.csv", "fixed_reference.csv",
                  "exclusions.csv", "annual_comparison.csv", "pairwise.csv", "t07_evidence.json"}
COLUMNS = {
    "profiles.csv": ["profile_id", "year", "participation_pct", "ln_share_pct"],
    "historical_reference.csv": ["series", "reference_year", "year", "reference_id", "participation_pct", "ln_share_pct"],
    "annual_metrics.csv": ["year", "method", "k", "silhouette"],
    "historical_comparison.csv": ["series", "reference_year", "from_year", "to_year", "mean_delta_pp",
                                  "spearman_rate_rank", "same_reference_band_group_pct", "annual_kmeans_ari"],
}
LIMITATIONS = [
    "Borrador pendiente de revisión final del paquete, sus canales, condiciones de uso y derechos; no autoriza publicación.",
    "La reducción de campos y el redondeo no certifican anonimato ni impiden inferencias con fuentes auxiliares o publicaciones anteriores.",
    "Se omiten conteos exactos, claves geográficas, asignaciones, exclusiones, extremos, composiciones demográficas y escenarios de sensibilidad.",
    "Los porcentajes se redondean a un decimal y los coeficientes a dos, sin ajustar sumas a 100%; no deben reconstruirse conteos desde ellos.",
    "La participación usa SV/(SV+NV); las proporciones de LN se refieren a la población elegible de cada elección, no a una suma entre elecciones.",
    "Solo se muestran cinco bandas históricas por serie como referencia comparable; no son la selección óptima de todos los años ni trayectorias de personas.",
    "Los umbrales de elegibilidad del análisis son exploratorios, no reglas oficiales de confidencialidad.",
    "Los datos originales son públicos en el INE; esta vista reduce detalle y evita amplificar celdas pequeñas, pero no vuelve secretos los originales.",
    "Los hashes aportan trazabilidad, no autenticidad firmada ni protección estadística; aquí no se recalculan los modelos.",
]
README = """# Borrador de resúmenes para difusión

**Pendiente de revisión. No autoriza publicación.** Esta carpeta es independiente
de la evidencia interna T08 y no debe incorporarse automáticamente a un envío,
repositorio público, fichas o presentación.

- `profiles.csv`: cinco perfiles centrales de 2024, con participación y proporción de LN.
- `historical_reference.csv`: cinco bandas fijas para cada una de las seis elecciones.
- `annual_metrics.csv`: silueta de los 36 candidatos anuales base, sin sensibilidades.
- `historical_comparison.csv`: seis comparaciones dentro de las dos series, para k=5.
- `manifest.json`: procedencia mediante hashes, precisión, limitaciones y revisión pendiente.

Los porcentajes y cambios en puntos porcentuales tienen un decimal; los
coeficientes, dos. Se usa ROUND_HALF_UP. Las sumas redondeadas pueden diferir de
100%. Una tasa vacía es indefinida, no cero. Se mantienen las definiciones fijas
de cada serie: referencia 2024 para 2012/2018/2024 y 2021 para 2009/2015/2021.
No se comparan etiquetas entre series ni se describen movimientos individuales.

Se excluyen claves geográficas, conteos exactos, asignaciones, exclusiones,
composiciones demográficas, extremos y escenarios alternativos. Las descripciones
demográficas que se propongan después requieren revisión propia; no se aprueban
por generar este paquete. No usar la evidencia interna como anexo externo sin revisión.

Esta reducción no garantiza anonimato frente a otras tablas o datos públicos.
Antes de difundir, revisar conjuntamente los materiales y resolver las condiciones
de uso, atribución, cesión de derechos y destinatarios. Los modelos y la evidencia
interna se conservan sin cambios para reproducibilidad; esta vista no los sustituye.

Fuente: INE, Conteos Censales de Participación Ciudadana 2009–2024.
https://portal.ine.mx/transparencia/datos-abiertos/visualizacion-datos/conteos-censales-participacion/
"""


def digest(value):
    require(isinstance(value, str) and re.fullmatch(r"[a-f0-9]{64}", value) is not None,
            "Huella SHA-256 no válida")
    return value


def rounded(value, decimals, lower=0, upper=100, nullable=False):
    if value == "" and nullable:
        return ""
    number = Decimal(value)
    require(number.is_finite() and lower <= number <= upper, "Indicador no finito o fuera de rango")
    return str(number.quantize(Decimal(1).scaleb(-decimals), rounding=ROUND_HALF_UP))


def read_rows(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def indexed(rows, fields, expected):
    result = {tuple(row[field] for field in fields): row for row in rows}
    require(len(result) == len(rows) and set(result) == set(expected), "Filas incompletas, duplicadas o identificadores no válidos")
    return result


def load_bundle(root, source):
    report_path = confined(root, source / "report.json", "outputs")
    report_hash = sha256(report_path)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    require(report["contract"] == "t08-profiles/v1" and report["internal_only"] is True,
            "Se requiere un paquete interno T08")
    selection = report["selection"]
    require(selection["year"] == 2024 and selection["method"] == "kmeans"
            and selection["k"] == 5 and selection["scenario"] == "baseline", "Selección T08 no compatible")
    require(report["series"] == [{"name": name, "years": list(years), "reference_year": reference}
                                 for name, years, reference in SERIES], "Series T08 no compatibles")
    require(set(report["inputs"]) == set(map(str, YEARS)), "Faltan elecciones en la procedencia T08")
    hashes = report["artifacts_sha256"]
    require(set(hashes) == INTERNAL_FILES, "Inventario interno no compatible")
    fingerprints = {"report.json": report_hash, **hashes}
    for name, expected in fingerprints.items():
        path = confined(root, source / name, "outputs")
        require(sha256(path) == digest(expected), f"La huella del archivo interno {name} no coincide")
    sources = []
    for year in YEARS:
        item = report["inputs"][str(year)]
        require(type(item["election_year"]) is int and item["election_year"] == year, "Año de procedencia no válido")
        sources.append({"year": year, "table_sha256": digest(item["table_sha256"]),
                        "report_sha256": digest(item["report_sha256"]),
                        "manifest_sha256": digest(item["manifest_sha256"]) if item["manifest_sha256"] is not None else None})
    return sources, fingerprints


def reduced_rows(source):
    # Solo se construyen campos conocidos; nunca se copian filas, textos ni JSON del paquete interno.
    profiles = indexed(read_rows(source / "profiles.csv"), ("profile_id", "year"),
                       {(f"CCPC-2024-K5-P{rank:02d}", "2024") for rank in range(1, 6)})
    result = {"profiles.csv": [{"profile_id": identity, "year": year,
                                "participation_pct": rounded(row["participation_pct"], 1),
                                "ln_share_pct": rounded(row["ln_share_pct"], 1)}
                               for (identity, year), row in sorted(profiles.items())]}
    references = indexed([row for row in read_rows(source / "fixed_reference.csv") if row["k"] == "5"],
                         ("series", "reference_year", "year", "reference_id"),
                         {(name, str(reference), str(year), f"CCPC-REF-{reference}-K5-R{rank:02d}")
                          for name, years, reference in SERIES for year in years for rank in range(1, 6)})
    result["historical_reference.csv"] = [
        {"series": name, "reference_year": reference, "year": year, "reference_id": identity,
         "participation_pct": rounded(row["participation_pct"], 1, nullable=True),
         "ln_share_pct": rounded(row["ln_share_pct"], 1)}
        for (name, reference, year, identity), row in sorted(references.items())]
    annual = indexed([row for row in read_rows(source / "annual_comparison.csv") if row["scenario"] == "baseline"],
                     ("year", "method", "k"), {(str(year), method, str(k)) for year in YEARS
                                              for method in ("kmeans", "ward") for k in (4, 5, 6)})
    result["annual_metrics.csv"] = [{"year": year, "method": method, "k": k,
                                    "silhouette": rounded(row["silhouette"], 2, -1, 1)}
                                   for (year, method, k), row in sorted(annual.items())]
    pairs = indexed([row for row in read_rows(source / "pairwise.csv") if row["k"] == "5"],
                    ("series", "reference_year", "from_year", "to_year"),
                    {(name, str(reference), str(years[start]), str(years[end]))
                     for name, years, reference in SERIES for start, end in ((0, 1), (0, 2), (1, 2))})
    result["historical_comparison.csv"] = [
        {"series": name, "reference_year": reference, "from_year": start, "to_year": end,
         "mean_delta_pp": rounded(row["mean_delta_pp"], 1, -100, 100),
         "spearman_rate_rank": rounded(row["spearman_rate_rank"], 2, -1, 1, nullable=True),
         "same_reference_band_group_pct": rounded(row["same_reference_band_group_pct"], 1),
         "annual_kmeans_ari": rounded(row["annual_kmeans_ari"], 2, -1, 1)}
        for (name, reference, start, end), row in sorted(pairs.items())]
    return result


def prepare(root, input_path, run_name):
    root = root.resolve()
    source = confined(root, input_path, "outputs")
    destination = confined(root, Path("outputs") / run_name, "outputs")
    require(not destination.exists(), "La salida ya existe; elija otro --run-name")
    sources, fingerprints = load_bundle(root, source)
    rows = reduced_rows(source)
    manifest = {"contract": "disclosure-summary/v1", "status": "draft_pending_review",
                "publication_authorized": False, "source_report_sha256": fingerprints["report.json"],
                "pipeline_sha256": sha256(Path(__file__)), "sources": sources,
                "rounding": {"percent_decimals": 1, "coefficient_decimals": 2, "mode": "ROUND_HALF_UP"},
                "limitations": LIMITATIONS}
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent, prefix=".disclosure-") as temporary:
        staging = Path(temporary) / "bundle"
        staging.mkdir()
        for name, fields in COLUMNS.items():
            write_csv(staging / name, fields, rows[name])
        (staging / "README.md").write_text(README, encoding="utf-8")
        manifest["artifacts_sha256"] = {path.name: sha256(path) for path in sorted(staging.iterdir())}
        (staging / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False) + "\n", encoding="utf-8")
        require(all(sha256(confined(root, source / name, "outputs")) == value for name, value in fingerprints.items()),
                "El paquete interno cambió durante la preparación")
        require(not destination.exists(), "La salida ya existe")
        staging.rename(destination)
    return {"status": "draft_pending_review", "directory": destination.relative_to(root).as_posix(),
            "publication_authorized": False, "profiles": 5, "years": YEARS,
            "historical_reference_rows": 30, "annual_candidates": 36, "comparisons": 6}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Raíz del proyecto o de datos de prueba aislados")
    parser.add_argument("--input", default="outputs/t08_profiles_final", help="Paquete interno T08 dentro de outputs; no se modifica")
    parser.add_argument("--run-name", default="t08_disclosure_summary", help="Directorio nuevo dentro de outputs; no se sobrescribe ni se publica")
    arguments = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", arguments.run_name):
        parser.error("--run-name debe ser un nombre alfanumérico simple con guiones o guiones bajos opcionales")
    try:
        result = prepare(arguments.root, arguments.input, arguments.run_name)
    except (ValueError, OSError, KeyError, TypeError, InvalidOperation) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
