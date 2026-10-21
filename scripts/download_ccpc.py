"""Descarga las fuentes oficiales CCPC de 2009–2024 sin extraerlas."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
from urllib.request import urlopen
import zipfile


ROOT = Path(__file__).resolve().parents[1]
LANDING = "https://portal.ine.mx/transparencia/datos-abiertos/visualizacion-datos/conteos-censales-participacion/"
UPLOADS = "https://portal.ine.mx/wp-content/uploads/"
SOURCES = [
    {"election_year": year, "url": UPLOADS + folder + f"DatosAbiertos_DECEyEC_ConteosCensales{year}.zip"}
    for year, folder in [
        (2009, "2022/04/"), (2012, "2022/04/"), (2015, "2022/04/"),
        (2018, "2022/04/"), (2021, "2022/04/"), (2024, "2025/08/"),
    ]
] + [{"election_year": None, "url": UPLOADS + "2025/06/Manual-Conteos-Censales-2009-2024.pdf"}]


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def acquire(url, destination):
    """Valida una descarga nueva antes de guardar sus bytes originales de forma local."""
    if destination.exists():
        raise FileExistsError(f"El archivo original ya existe: {destination.name}")
    # Conserva los archivos interrumpidos y crea un archivo parcial exclusivo para este intento.
    with tempfile.NamedTemporaryFile(
        dir=destination.parent, prefix=destination.name + ".", suffix=".part", delete=False,
    ) as output:
        partial = Path(output.name)
        try:
            with urlopen(url, timeout=90) as response:
                shutil.copyfileobj(response, output)
        except Exception:
            output.close()
            partial.unlink()
            raise
    try:
        members = []
        if destination.suffix == ".zip":
            with zipfile.ZipFile(partial) as archive:
                members = archive.namelist()
                bad_member = archive.testzip()
                if bad_member is not None:
                    raise zipfile.BadZipFile(f"Error de CRC: {bad_member}")
        else:
            with partial.open("rb") as stream:
                if not stream.read(5) == b"%PDF-":
                    raise ValueError("Se esperaba una firma PDF")
        receipt = {
            "url": url,
            "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
            "bytes": partial.stat().st_size,
            "sha256": sha256(partial),
            "members": members,
        }
        # En Windows, rename rechaza un destino existente; nunca reemplazar los datos originales.
        partial.rename(destination)
        return receipt
    finally:
        partial.unlink(missing_ok=True)


def main():
    raw = ROOT / "data" / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    manifest = ROOT / "data" / "sources.json"
    entries = json.loads(manifest.read_text(encoding="utf-8")) if manifest.exists() else []
    for source in SOURCES:
        filename = source["url"].rsplit("/", 1)[1]
        destination = raw / filename
        previous = next((entry for entry in entries if entry["url"] == source["url"]), None)
        if destination.exists():
            if previous is None or sha256(destination) != previous["sha256"]:
                raise ValueError(f"Archivo original sin registro o modificado; se requiere inspección manual: {filename}")
            print(f"Archivo original existente verificado: {filename}", flush=True)
            continue
        print(f"Descargando: {filename}", flush=True)
        receipt = acquire(source["url"], destination)
        receipt.update({
            "landing_url": LANDING,
            "election_year": source["election_year"],
            "local_path": destination.relative_to(ROOT).as_posix(),
            "publisher_version": "Not stated on the landing page",
            "declared_coverage": "Federal election, Mexico" if source["election_year"] else "Platform manual, 2009–2024",
        })
        # Guarda cada descarga completada para conservar sus registros si se interrumpe el lote.
        entries = [entry for entry in entries if entry["url"] != source["url"]] + [receipt]
        pending = manifest.with_suffix(".json.part")
        pending.write_text(json.dumps(entries, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
        pending.replace(manifest)
        print(f"Guardados {receipt['bytes']} bytes; SHA-256 {receipt['sha256']}", flush=True)


def decode_documentation(content):
    try:
        return content.decode("utf-8-sig"), "utf-8-sig"
    except UnicodeDecodeError:
        return content.decode("cp1252"), "cp1252 (fallback; confirm in T04)"


def inspect_sources():
    """Verifica las fuentes esperadas sin conexión e inspecciona documentación, no filas de datos."""
    entries = json.loads((ROOT / "data" / "sources.json").read_text(encoding="utf-8"))
    if {entry["url"] for entry in entries} != {source["url"] for source in SOURCES}:
        raise ValueError("El manifiesto no contiene las siete fuentes esperadas")
    report = []
    for entry in entries:
        original = ROOT / entry["local_path"]
        if original.stat().st_size != entry["bytes"] or sha256(original) != entry["sha256"]:
            raise ValueError(f"Falló la comprobación de integridad: {original.name}")
        item = {"election_year": entry["election_year"], "bytes": entry["bytes"], "sha256_verified": True}
        if original.suffix == ".zip":
            with zipfile.ZipFile(original) as archive:
                names = archive.namelist()
                if names != entry["members"]:
                    raise ValueError(f"Cambió el inventario del archivo ZIP: {original.name}")
                csvs = [name for name in names if name.lower().endswith(".csv")]
                docs = [name for name in names if name.lower().endswith(".txt")]
                item["csv_count"] = len(csvs)
                item["documentation"] = []
                for name in docs:
                    with archive.open(name) as stream:
                        content = stream.read(65537)
                    text, encoding = decode_documentation(content[:65536])
                    item["documentation"].append({
                        "member": name, "encoding_used": encoding, "text": text,
                        "truncated": len(content) > 65536,
                    })
                if csvs:
                    with archive.open(csvs[0]) as stream:
                        header = stream.readline(8192)
                    item["csv_header"] = decode_documentation(header)[0].strip()
        report.append(item)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inspect", action="store_true", help="Verifica los hashes sin conexión y muestra los diccionarios y el primer encabezado CSV de cada ZIP; no extrae archivos ni lee filas de registros")
    arguments = parser.parse_args()
    if arguments.inspect:
        print(json.dumps(inspect_sources(), indent=2, ensure_ascii=True))
    else:
        main()
