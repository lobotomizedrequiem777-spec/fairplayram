"""Comparación auxiliar de etiquetas RAM++ sobre portadas Steam (no altera Modelo A/B)."""
from __future__ import annotations

from functools import lru_cache
from html import escape
from io import BytesIO
import os
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

HTML_INICIAL = '<div class="fp-vacio">Pulsa «Analizar elementos de las portadas» para mostrar las etiquetas visuales.</div>'
_HOSTS = {"cdn.akamai.steamstatic.com", "shared.akamai.steamstatic.com", "shared.fastly.steamstatic.com", "steamcdn-a.akamaihd.net", "cdn.cloudflare.steamstatic.com"}


def separar(etiquetas_a: set[str], etiquetas_b: set[str]) -> tuple[list[str], list[str], list[str]]:
    """Solo juego 1, solo juego 2, etiquetas compartidas."""
    a = {x.strip().casefold() for x in etiquetas_a if x and x.strip()}
    b = {x.strip().casefold() for x in etiquetas_b if x and x.strip()}
    return sorted(a-b), sorted(b-a), sorted(a&b)


def _descargar_portada(url: str):
    from PIL import Image
    parsed = urlparse(url or "")
    if parsed.scheme != "https" or parsed.hostname not in _HOSTS:
        raise ValueError("La portada debe venir de un CDN de Steam permitido.")
    # Evita redirecciones a destinos externos.
    from urllib.request import build_opener, HTTPRedirectHandler
    class SinRedireccion(HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            raise ValueError("Redirección de portada no permitida")
    req = Request(url, headers={"User-Agent": "FairPlayAI/1.0"})
    with build_opener(SinRedireccion()).open(req, timeout=12) as response:
        data = response.read(8 * 1024 * 1024 + 1)
    if len(data) > 8 * 1024 * 1024:
        raise ValueError("Portada demasiado grande")
    with Image.open(BytesIO(data)) as img:
        img.load()
        return img.convert("RGB")


@lru_cache(maxsize=1)
def _modelo_ram():
    """Carga diferida: requiere instalación opcional de RAM++ y checkpoint local."""
    checkpoint = Path(os.environ.get("FAIRPLAY_RAM_CHECKPOINT", ""))
    if not checkpoint.is_file():
        raise RuntimeError("RAM++ no está configurado: define FAIRPLAY_RAM_CHECKPOINT con la ruta del checkpoint.")
    import torch
    from ram.models import ram_plus
    from ram import get_transform
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = ram_plus(pretrained=str(checkpoint), image_size=384, vit="swin_l")
    model.eval().to(device)
    return model, get_transform(image_size=384), device


@lru_cache(maxsize=256)
def etiquetas_portada(url: str) -> tuple[str, ...]:
    import torch
    from ram import inference_ram as inference
    model, transform, device = _modelo_ram()
    image = transform(_descargar_portada(url)).unsqueeze(0).to(device)
    with torch.inference_mode():
        etiquetas_en, _ = inference(image, model)
    # RAM++ devuelve etiquetas inglesas separadas por ' | '.
    return tuple(x.strip() for x in etiquetas_en.split(" | ") if x.strip())


def html_resultado(a: list[str], b: list[str], comunes: list[str], nombres: tuple[str, str]) -> str:
    def columna(titulo, tags):
        chips = "".join(f'<span style="display:inline-block;background:#344763;color:white;border-radius:6px;padding:5px 9px;margin:3px">{escape(tag)}</span>' for tag in tags)
        return f'<div style="flex:1;min-width:150px;background:#25334a;padding:14px;border-radius:10px"><b>{escape(titulo)}</b><div style="margin-top:10px">{chips or "<em>Sin elementos detectados</em>"}</div></div>'
    return ('<div style="display:flex;gap:10px;flex-wrap:wrap;color:#fff">'
            + columna(f"Solo {nombres[0]}", a) + columna(f"Solo {nombres[1]}", b)
            + columna("Similitudes", comunes) + '</div><p style="font-size:12px;color:#9eabc0">Etiquetas visuales automáticas (en inglés). Compartir objetos no demuestra copia.</p>')


def analizar_par(par: dict | None) -> str:
    if not par:
        return '<p>Primero carga un par de videojuegos.</p>'
    try:
        a, b = par["a"], par["b"]
        tags_a = set(etiquetas_portada(a["imagen"]))
        tags_b = set(etiquetas_portada(b["imagen"]))
        solo_a, solo_b, comunes = separar(tags_a, tags_b)
        return html_resultado(solo_a, solo_b, comunes, (a["nombre"], b["nombre"]))
    except Exception as exc:
        # Errores visibles para el operador, sin bloquear el etiquetado principal.
        return f'<p>El análisis RAM++ no está disponible: {escape(str(exc))}</p>'
