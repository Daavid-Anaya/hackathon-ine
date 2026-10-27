"""Generate internal T12 cards; export Letter PDF and 300 dpi PNG locally.

HTML generation uses only the standard library. Final export additionally needs
Chrome/Chromium/Edge and PyMuPDF; see docs/profile-cards.md.
"""

import argparse
import csv
import hashlib
from html import escape
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


BASE_DIR = Path(__file__).resolve().parents[1]
AGE_BANDS = ("18-24", "25-34", "35-44", "45-59", "60+")
NAMES = ("Menor participación observada", "Participación observada intermedia-baja",
         "Participación observada intermedia", "Participación observada intermedia-alta",
         "Mayor participación observada")
# Summaries preserve the scope of docs/institutional-proposals.md, not evaluated interventions.
STRATEGIES = (
    ("Flexibilidad operativa en credencialización y justificación cívico-laboral",
     "Horarios vespertinos y de fin de semana en MAC seleccionados; reimpresión exprés por robo o extravío; convenios de permiso laboral dominical para votar.",
     "Módulos móviles RFE, cartelería y avisos institucionales abiertos.",
     "TCHE = 100 × trámites en MAC seleccionados en sábado, domingo o turno vespertino / total de trámites en esos MAC.",
     "SIIRFE; campaña de credencialización (septiembre–febrero).",
     "Movilidad laboral o estudiantil, domicilio desactualizado y posibles restricciones de horario."),
    ("Información ejecutiva móvil y certidumbre logística",
     "Consulta móvil de casilla con afluencia estimada; síntesis neutras de candidaturas en Conóceles; información de transporte hacia centros de votación.",
     "Inés por acceso voluntario, cartelería QR y micrositio ligero.",
     "DRC = 100 × consultas de ubicación y candidaturas resueltas en ≤ 2.0 s / total de consultas entrantes.",
     "Telemetría UTSI; jornada electoral de 07:00 a 19:00.",
     "Posibles restricciones de tiempo por trabajo o cuidados e incertidumbre logística."),
    ("Facilitación territorial y corresponsabilidad comunitaria",
     "Casillas extraordinarias y especiales en localidades aisladas a más de 45 minutos de la cabecera seccional; espera sombreada para acompañantes; información bilingüe donde aplique.",
     "Asambleas comunitarias, módulos RFE, radio comunitaria y cartelería rural.",
     "PACE = 100 × casillas extraordinarias con reporte de instalación antes de las 08:30 / total de extraordinarias aprobadas.",
     "SIJE; primer corte de instalación de la jornada (08:30).",
     "Posibles costos de traslado, cargas de cuidado y necesidades de información oral o bilingüe."),
    ("Agilización de flujo y fortalecimiento del funcionariado",
     "Optimizar circuitos y canceles reglamentarios, incluido el portátil accesible; señalización y ergonomía; capacitación y apoyo integral al funcionariado de casilla.",
     "Talleres, comunicación CAE–funcionariado en su función institucional y módulos distritales.",
     "TAP = 100 × personas capacitadas que integraron efectivamente casilla / cargos requeridos de propietarios y suplentes en la demarcación.",
     "SICE; segunda etapa de capacitación (mayo–jornada electoral).",
     "Posible saturación de filas, tiempos de espera y desgaste del funcionariado."),
    ("Accesibilidad universal y trato preferencial",
     "Casillas en planta baja con acceso a nivel o rampas funcionales comprobadas; mamparas especiales, lupas y plantillas Braille; fila preferencial y sillas techadas.",
     "Verificación distrital de inmuebles e información en INAPAM, clínicas y plazas públicas.",
     "CEAF = 100 × casillas verificadas en planta baja sin desniveles o con rampa / total de casillas instaladas en el distrito.",
     "Cédula de Verificación de Inmuebles y SIJE; febrero–abril y apertura de casillas.",
     "Posibles barreras arquitectónicas, fatiga por espera o necesidad de apoyos visuales."),
)

CSS = """
@page { size: letter portrait; margin: 12mm; }
* { box-sizing: border-box; }
body { margin: 0; color: #243247; background: #edf0f4; font: 13.4px/1.38 Arial, sans-serif; }
.sheet { width: 192mm; margin: 20px auto; padding: 0; background: #fff; }
header { border-top: 6px solid #8f1434; border-bottom: 1px solid #b9c2d0; padding: 12px 0; }
.eyebrow { color: #8f1434; font-weight: bold; letter-spacing: .5px; font-size: 12px; }
h1 { font: bold 27px/1.1 Georgia, serif; margin: 6px 0; }
h2 { font-size: 14px; margin: 12px 0 6px; color: #8f1434; }
p { margin: 5px 0; }
.kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 14px 0; }
.kpi { border-left: 3px solid #8f1434; padding-left: 8px; font-size: 12px; }
.value { display: block; font-size: 23px; font-weight: bold; font-variant-numeric: tabular-nums; }
.charts { display: grid; grid-template-columns: 1.1fr 1fr; gap: 20px; }
.chart { margin: 0; }
svg { display: block; width: 100%; }
.strategy { background: #f0f5fa; padding: 10px 12px; border-left: 3px solid #235886; }
.limits { border-top: 1px solid #b9c2d0; margin-top: 10px; padding-top: 6px; font-size: 11.4px; }
footer { margin-top: 8px; color: #415269; font-size: 10.8px; overflow-wrap: anywhere; }
.small { font-size: 11.5px; }
@media print {
 body { background: #fff; print-color-adjust: exact; -webkit-print-color-adjust: exact; }
 .sheet { width: auto; margin: 0; break-after: page; }
 .sheet:last-child { break-after: auto; }
 header, .kpis, .charts, .strategy, .limits, footer { break-inside: avoid; }
}
"""


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def number(value):
    return f"{int(value):,}".replace(",", " ")


def read_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def numeric(value, label, maximum=None):
    result = float(value)
    if not math.isfinite(result) or result < 0 or (maximum is not None and result > maximum):
        raise ValueError(f"Invalid {label}")
    return result


def composition(text, allowed):
    values = json.loads(text)
    if not isinstance(values, dict) or not values or not set(values) <= set(allowed):
        raise ValueError("Invalid composition categories")
    result = {key: numeric(values.get(key, 0), "composition", 100) for key in allowed}
    if not math.isclose(sum(result.values()), 100, abs_tol=1e-6):
        raise ValueError("Composition must sum to 100")
    return result


def load_cards(profiles_path, cross_path):
    profiles, cross = read_rows(profiles_path), read_rows(cross_path)
    expected = {f"CCPC-2024-K5-P{i:02d}" for i in range(1, 6)}
    if len(profiles) != 5 or {r["profile_id"] for r in profiles} != expected:
        raise ValueError("Expected exactly five unique 2024 K5 profiles")
    if len(cross) != 15 or {r["profile_id"] for r in cross} != expected:
        raise ValueError("Expected fifteen matching profile/TIPOSEC rows")
    cards = []
    total_ln = sum(numeric(row["LN"], "LN") for row in profiles)
    if total_ln <= 0:
        raise ValueError("LN must be positive")
    for row in sorted(profiles, key=lambda r: r["profile_id"]):
        if row["year"] != "2024":
            raise ValueError("Only 2024 profiles are supported")
        for key in ("LN", "SV", "NV", "NS", "entities"):
            row[key] = numeric(row[key], key)
            if not row[key].is_integer():
                raise ValueError(f"{key} must be an integer")
        if not 1 <= row["entities"] <= 32 or row["LN"] <= 0 or row["SV"] + row["NV"] <= 0:
            raise ValueError("Invalid profile counts")
        if row["LN"] != row["SV"] + row["NV"] + row["NS"]:
            raise ValueError("Profile counts do not reconcile")
        for key, calculated in (
            ("participation_pct", 100 * row["SV"] / (row["SV"] + row["NV"])),
            ("unspecified_pct", 100 * row["NS"] / row["LN"]),
            ("ln_share_pct", 100 * row["LN"] / total_ln),
        ):
            row[key] = numeric(row[key], key, 100)
            if not math.isclose(row[key], calculated, abs_tol=1e-6):
                raise ValueError(f"Inconsistent {key}")
        age = composition(row["age_ln_share_pct"], AGE_BANDS)
        sex = composition(row["sex_ln_share_pct"], ("0", "1"))
        rows = [r for r in cross if r["profile_id"] == row["profile_id"]]
        if len(rows) != 3 or {r["TIPOSEC"] for r in rows} != {"U", "M", "R"}:
            raise ValueError("Each profile requires U/M/R exactly once")
        for key in ("LN", "SV", "NV", "NS"):
            values = [numeric(r[key], key) for r in rows]
            if any(not v.is_integer() for v in values) or sum(values) != row[key]:
                raise ValueError(f"TIPOSEC {key} does not reconcile with profile")
        shares = {}
        for item in rows:
            if float(item["LN"]) != sum(float(item[k]) for k in ("SV", "NV", "NS")):
                raise ValueError("TIPOSEC counts do not reconcile")
            share = numeric(item["within_profile_ln_share_pct"], "section share", 100)
            if not math.isclose(share, 100 * float(item["LN"]) / row["LN"], abs_tol=1e-6):
                raise ValueError("Inconsistent section share")
            shares[item["TIPOSEC"]] = share
        cards.append((row, age, sex, shares))
    return cards


def bars(title, values):
    """Use one labelled horizontal scale; text conveys values without colour."""
    height = len(values) * 26 + 10
    parts = [f'<svg role="img" aria-label="{escape(title)}" viewBox="0 0 340 {height}" xmlns="http://www.w3.org/2000/svg">',
             f'<title>{escape(title)}</title>']
    for index, (label, value) in enumerate(values):
        y = index * 26 + 5
        parts.extend((
            f'<text x="0" y="{y + 14}" font-size="13" fill="#243247">{escape(label)}</text>',
            f'<rect x="85" y="{y}" width="190" height="18" fill="#e6eaf0"/>',
            f'<rect x="85" y="{y}" width="{1.9 * value:.3f}" height="18" fill="#8f1434"/>',
            f'<text x="284" y="{y + 14}" font-size="13" fill="#243247">{value:.1f}%</text>',
        ))
    return "\n".join(parts) + "</svg>"


def card_body(card, profiles_name, cross_name):
    row, age, sex, shares = card
    index = int(row["profile_id"][-2:]) - 1
    title, action, channels, indicator, source, hypothesis = STRATEGIES[index]
    pid = escape(row["profile_id"])
    age_text = "; ".join(f"{band} años: {value:.1f}%" for band, value in age.items())
    # Narrative values and all chart values derive from the same validated rows.
    narrative = (f"En 2024, la participación conocida es {row['participation_pct']:.1f}%; "
                 f"el perfil reúne {row['ln_share_pct']:.1f}% de la LN elegible y tiene presencia "
                 f"en {int(row['entities'])} entidades. Composición de LN por edad: {age_text}. "
                 f"Mujeres: {sex['1']:.1f}%; hombres: {sex['0']:.1f}%. "
                 f"Secciones urbanas: {shares['U']:.1f}%; mixtas: {shares['M']:.1f}%; rurales: {shares['R']:.1f}%.")
    return f'''<article class="sheet">
<header><div class="eyebrow">T12 · P{index + 1:02d} · CCPC 2024 · Borrador interno</div>
<h1>{NAMES[index]}</h1><p>{pid} · Estrato agregado, no clasificación de personas</p></header>
<div class="kpis">
<div class="kpi">Participación conocida<strong class="value">{row['participation_pct']:.1f}%</strong>SV / (SV + NV)</div>
<div class="kpi">Peso en LN elegible<strong class="value">{row['ln_share_pct']:.1f}%</strong>{number(row['LN'])} registros LN</div>
<div class="kpi">Presencia territorial<strong class="value">{int(row['entities'])}</strong>entidades federativas</div>
<div class="kpi">No especificado (NS)<strong class="value">{row['unspecified_pct']:.1f}%</strong>NS / LN</div></div>
<div class="charts"><section><h2>Edad · proporción de LN</h2>
{bars('Edad en la lista nominal', list(age.items()))}</section><section><h2>Sexo · proporción de LN</h2>
{bars('Sexo en la lista nominal', [('Mujeres', sex['1']), ('Hombres', sex['0'])])}
<h2>Tipo de sección · proporción de LN</h2>
{bars('Tipo de sección', [('Urbana', shares['U']), ('Mixta', shares['M']), ('Rural', shares['R'])])}</section></div>
<section><h2>Síntesis descriptiva · T09</h2><p>{narrative}</p></section>
<section><h2>E{index + 1:02d} · Propuesta T10: {title}</h2><div class="strategy">
<p>{action}</p><p><strong>Canales:</strong> {channels}</p>
<p><strong>Indicador de servicio propuesto:</strong> {escape(indicator)}</p>
<p class="small"><strong>Fuente operativa propuesta:</strong> {source} Disponibilidad sujeta a factibilidad técnica.
Denominador cero: «No aplica»; no equivale a cero desempeño.</p></div></section>
<aside class="limits"><strong>Límites y uso interno.</strong> Barreras como hipótesis externas no medidas por CCPC: {hypothesis}
No son atributos individuales ni explicaciones causales. El modelo agrupa únicamente por participación conocida; edad, sexo y TIPOSEC son descriptores.
Sin contacto individualizado ni rastreo por perfil; canales abiertos y voluntarios. Las propuestas no certifican viabilidad jurídica ni operativa.
Pendiente de revisión de divulgación conjunta T14–T15 antes de compartir o entregar al concurso.</aside>
<footer>Fuentes: INE, CCPC 2024; T08: {escape(profiles_name)}; cruce TIPOSEC: {escape(cross_name)}.
Referencias: docs/profile-interpretation.md y docs/institutional-proposals.md. Exportación: carta 216 × 279 mm, PDF vectorial y PNG a 300 dpi; hashes y versiones en report.json.</footer>
</article>'''


def document(body):
    return ('<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<title>T12 · Fichas internas CCPC 2024</title><style>' + CSS +
            '</style></head><body><main>' + body + '</main></body></html>')


def export_cards(stage, browser):
    try:
        import pymupdf
    except ImportError as exc:
        raise ValueError("PDF/PNG export requires PyMuPDF; see docs/profile-cards.md") from exc
    browser = Path(browser).resolve()
    if not browser.is_file():
        raise ValueError("Browser executable not found; pass --browser (see docs/profile-cards.md)")
    checks = []
    with pymupdf.open() as combined:
        for index in range(1, 6):
            stem = f"ficha_P{index:02d}"
            raw = stage / f"{stem}.raw.pdf"
            with tempfile.TemporaryDirectory(prefix="t12-browser-") as profile:
                result = subprocess.run([
                    str(browser), "--headless=new", "--disable-gpu", "--no-first-run",
                    "--no-default-browser-check", "--disable-extensions", "--disable-background-networking",
                    "--host-resolver-rules=MAP * ~NOTFOUND", f"--user-data-dir={profile}",
                    "--no-pdf-header-footer", f"--print-to-pdf={raw}",
                    (stage / f"{stem}.html").as_uri(),
                ], capture_output=True, timeout=90, check=False)
            if result.returncode or not raw.is_file():
                raise ValueError(f"Browser PDF export failed for {stem}")
            with pymupdf.open(raw) as pdf:
                if len(pdf) != 1:
                    raise ValueError(f"{stem} must fit exactly one page; got {len(pdf)}")
                page = pdf[0]
                if abs(page.rect.width - 612) > 1 or abs(page.rect.height - 792) > 1:
                    raise ValueError("Expected Letter portrait PDF")
                spans = [span for block in page.get_text("dict")["blocks"] if block["type"] == 0
                         for line in block["lines"] for span in line["spans"] if span["text"].strip()]
                minimum = min(s["size"] for s in spans)
                if minimum < 8 or any(not page.rect.contains(pymupdf.Rect(s["bbox"])) for s in spans):
                    raise ValueError(f"{stem} has undersized or out-of-page text")
                if "Borrador interno" not in page.get_text() or "T14" not in page.get_text():
                    raise ValueError("Missing rendered internal/disclosure notice")
                pdf.set_metadata({"title": f"T12 {stem} — Borrador interno", "author": "",
                                  "subject": "Pendiente de revisión de divulgación T14–T15"})
                pdf.save(stage / f"{stem}.pdf", garbage=4, deflate=True, no_new_id=True)
                pix = page.get_pixmap(dpi=300, alpha=False)
                pix.save(stage / f"{stem}.png")
                combined.insert_pdf(pdf)
                checks.append(dict(profile=f"P{index:02d}", pages=1, min_font_pt=round(minimum, 2),
                                   png_width=pix.width, png_height=pix.height, dpi=300))
            raw.unlink()
        combined.set_metadata({"title": "T12 — Borrador interno P01–P05"})
        combined.save(stage / "cuaderno_fichas_todas.pdf", garbage=4, deflate=True, no_new_id=True)
    return {"pymupdf": pymupdf.VersionBind, "mupdf": pymupdf.VersionFitz,
            "browser_sha256": sha256(browser)}, checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profiles", type=Path, default=BASE_DIR / "outputs/t08_profiles_final/profiles.csv",
                        help="T08 profiles.csv input (five 2024 K5 profiles)")
    parser.add_argument("--cross", type=Path, default=BASE_DIR / "outputs/profile_section_types_2024/cross.csv",
                        help="TIPOSEC cross.csv for the same profiles")
    parser.add_argument("--output", type=Path, default=BASE_DIR / "outputs/t12_profile_cards",
                        help="New output directory; existing paths are never overwritten")
    parser.add_argument("--browser", type=Path, help="Local Chrome/Chromium/Edge executable for PDF export")
    parser.add_argument("--html-only", action="store_true", help="Prepare HTML only; does not complete T12")
    args = parser.parse_args()
    try:
        output = args.output.resolve()
        if output.exists():
            raise ValueError("Output already exists; choose another --output")
        if not output.parent.is_dir():
            raise ValueError("Output parent must already exist")
        if not args.html_only and args.browser is None:
            raise ValueError("PDF/PNG export needs --browser; --html-only prepares a draft only")
        if args.html_only and args.browser is not None:
            raise ValueError("--browser cannot be combined with --html-only")
        inputs = {"profiles.csv": sha256(args.profiles), "cross.csv": sha256(args.cross)}
        cards = load_cards(args.profiles, args.cross)
        # Work outside the repository. Only a fully validated bundle is copied to outputs.
        with tempfile.TemporaryDirectory(prefix="t12-cards-") as temporary:
            stage = Path(temporary)
            bodies = []
            for card in cards:
                stem = "ficha_" + card[0]["profile_id"][-3:]
                body = card_body(card, args.profiles.name, args.cross.name)
                bodies.append(body)
                (stage / f"{stem}.html").write_text(document(body), encoding="utf-8")
            (stage / "cuaderno_fichas_todas.html").write_text(document("\n".join(bodies)), encoding="utf-8")
            renderer, checks = ({}, []) if args.html_only else export_cards(stage, args.browser)
            report = dict(contract="t12-profile-cards/v1", internal_only=True, profiles=5,
                          exported=not args.html_only, inputs_sha256=inputs,
                          renderer=renderer, render_checks=checks,
                          export=dict(paper="Letter", width_pt=612, height_pt=792, dpi=300),
                          artifacts_sha256={p.name: sha256(p) for p in sorted(stage.iterdir())})
            (stage / "report.json").write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            (stage / "README.md").write_text(
                "# T12 — Borrador interno\n\nNo compartir antes de revisión de divulgación T14–T15.\n"
                "PDF vectorial carta (612 × 792 pt), márgenes 12 mm; PNG 2550 × 3300 px a 300 dpi.\n"
                "HTML sin recursos remotos. Cinco fichas y cuaderno en orden P01–P05.\n"
                "report.json registra hashes de entradas/salidas, motor y comprobaciones geométricas.\n"
                "Guía reproducible y límites: docs/profile-cards.md.\n" +
                ("Exportación PDF/PNG realizada.\n" if checks else "HTML únicamente: T12 no está completada.\n"), encoding="utf-8")
            if inputs != {"profiles.csv": sha256(args.profiles), "cross.csv": sha256(args.cross)}:
                raise ValueError("Inputs changed during export")
            # Reserve a new directory, never merge into an existing bundle.
            output.mkdir()
            try:
                for path in stage.iterdir():
                    shutil.copyfile(path, output / path.name)
            except BaseException:
                shutil.rmtree(output)
                raise
        print(json.dumps({"profiles": 5, "exported": not args.html_only, "output": str(output)}, ensure_ascii=False))
        return 0
    except (ValueError, KeyError, TypeError, OSError, csv.Error, subprocess.TimeoutExpired) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
