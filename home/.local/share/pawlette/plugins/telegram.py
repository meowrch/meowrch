"""pawlette plugin: telegram

Generates a Telegram Desktop theme (.tdesktop-theme) from a rendered
colors.tdesktop-theme file + a background image.

Configuration (pawlette.toml):

    [plugins.telegram]
    template_dir      = "~/.config/tg-config/"
    output            = "~/.config/tg-config/pawlette.tdesktop-theme"
    background_image  = "~/Pictures/my-bg.jpg"   # optional
    background_max_px = 2560                      # optional, default 2560

Background resolution order:
  1. background_image from config (PAWLETTE_PLUGIN_BACKGROUND_IMAGE)
  2. background.png in template_dir
  3. Solid color from PAWLETTE_COLOR_BG

If the resulting theme exceeds 5 MB even after all optimizations,
the image is discarded and a solid-color fallback is used instead.

Performance notes:
  - ZIP is stored uncompressed (STORED) — Telegram re-compresses anyway
    and deflating PNGs buys nothing while wasting CPU time.
  - Image is saved as JPEG inside the zip (named background.png) when
    the source is a photo — JPEG is 5-10x smaller than PNG for photos.
  - Resize uses BILINEAR (fast) instead of LANCZOS.
  - colors file is read once and reused.
"""

from __future__ import annotations

import io
import logging
import os
import sys
import zipfile
from pathlib import Path

logging.basicConfig(format="%(levelname)-8s %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

_TG_THEME_SIZE_LIMIT = 5 * 1024 * 1024  # 5 MB hard limit in Telegram Desktop
_BG_JPEG_QUALITY     = 88               # good quality/size tradeoff
_RESIZE_STEPS        = [2560, 1920, 1280, 960]  # try each step until theme fits


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


def _expand(path: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(path)))


def _solid_color_png(hex_color: str, size: int = 8) -> bytes:
    """Minimal solid-color PNG (8x8 px — Telegram tiles it).  No Pillow needed."""
    import struct, zlib
    hex_color = hex_color.lstrip("#")[:6]
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

    try:
        from PIL import Image
        img = Image.new("RGB", (size, size), (r, g, b))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except ImportError:
        pass

    def chunk(name: bytes, data: bytes) -> bytes:
        c = struct.pack(">I", len(data)) + name + data
        return c + struct.pack(">I", zlib.crc32(name + data) & 0xFFFFFFFF)

    ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
    raw  = (b"\x00" + bytes([r, g, b] * size)) * size
    idat = chunk(b"IDAT", zlib.compress(raw, 1))  # level 1 = fast
    iend = chunk(b"IEND", b"")
    return b"\x89PNG\r\n\x1a\n" + ihdr + idat + iend


def _image_to_jpeg(path: Path, max_px: int, quality: int = _BG_JPEG_QUALITY) -> bytes:
    """Open *path*, resize to *max_px* on the longest side, return JPEG bytes."""
    from PIL import Image
    with Image.open(path) as img:
        img = img.convert("RGB")
        w, h = img.size
        if max(w, h) > max_px:
            scale = max_px / max(w, h)
            img = img.resize((int(w * scale), int(h * scale)), Image.BILINEAR)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality, optimize=False, subsampling=2)
        return buf.getvalue()


def _optimize_background(path: Path, max_px: int) -> bytes | None:
    """Try progressively smaller sizes until the packed theme would fit < 5 MB.

    Returns JPEG bytes on success, None if nothing worked.
    """
    try:
        from PIL import Image  # noqa: F401 — just check availability
    except ImportError:
        log.warning("Pillow not installed — cannot optimize image. Falling back to solid color.")
        return None

    # Build candidate list: requested max_px first, then smaller fallbacks
    candidates = [s for s in _RESIZE_STEPS if s <= max_px]
    if not candidates or candidates[0] != max_px:
        candidates = [max_px] + [s for s in _RESIZE_STEPS if s < max_px]

    for px in candidates:
        data = _image_to_jpeg(path, max_px=px)
        # Estimate theme size (colors file is tiny, zip overhead negligible)
        if len(data) < _TG_THEME_SIZE_LIMIT - 256 * 1024:  # leave 256 KB margin
            if px != max_px:
                log.info("Background resized to %dpx to fit theme size limit", px)
            return data
        log.debug("Size at %dpx: %.1f MB — trying smaller", px, len(data) / 1024 / 1024)

    log.warning(
        "Background image could not be shrunk below 5 MB (smallest attempt: %dpx). "
        "Falling back to solid color.",
        candidates[-1],
    )
    return None


def _pack_theme(colors: bytes, bg: bytes) -> bytes:
    """Pack colors + background into a .tdesktop-theme zip (STORED, no compression)."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_STORED) as zf:
        zf.writestr("colors.tdesktop-theme", colors)
        zf.writestr("background.png", bg)  # Telegram reads by name, format can be JPEG
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Read config from env
# ---------------------------------------------------------------------------

template_dir = _expand(_env("PAWLETTE_PLUGIN_TEMPLATE_DIR", "~/.config/tg-config/"))
output_path  = _expand(_env(
    "PAWLETTE_PLUGIN_OUTPUT",
    "~/.config/tg-config/pawlette.tdesktop-theme",
))

_bg_image_env   = _env("PAWLETTE_PLUGIN_BACKGROUND_IMAGE")
background_image: Path | None = _expand(_bg_image_env) if _bg_image_env else None

try:
    background_max_px = int(_env("PAWLETTE_PLUGIN_BACKGROUND_MAX_PX", "2560"))
except ValueError:
    background_max_px = 2560

palette: dict[str, str] = {
    k.removeprefix("PAWLETTE_").lower(): v
    for k, v in os.environ.items()
    if k.startswith("PAWLETTE_") and not k.startswith("PAWLETTE_PLUGIN_")
}
color_bg = palette.get("color_bg", "#000000")

# ---------------------------------------------------------------------------
# Read rendered colors file
# ---------------------------------------------------------------------------

colors_file = template_dir / "colors.tdesktop-theme"
if not colors_file.exists():
    log.error(
        "colors.tdesktop-theme not found at %s — "
        "make sure the template is registered and was rendered.",
        colors_file,
    )
    sys.exit(1)

colors_content: bytes = colors_file.read_bytes()

# ---------------------------------------------------------------------------
# Resolve background
# ---------------------------------------------------------------------------

bg_source: Path | None = None

if background_image is not None:
    if not background_image.exists():
        log.error("background_image not found: %s", background_image)
        sys.exit(1)
    bg_source = background_image
elif (template_dir / "background.png").exists():
    bg_source = template_dir / "background.png"

if bg_source is not None:
    log.info("Optimizing background: %s", bg_source)
    bg_bytes = _optimize_background(bg_source, background_max_px)
    if bg_bytes is None:
        log.warning("Using solid-color fallback (color_bg=%s)", color_bg)
        bg_bytes = _solid_color_png(color_bg)
else:
    log.info("Generating solid-color background (color_bg=%s)", color_bg)
    bg_bytes = _solid_color_png(color_bg)

# ---------------------------------------------------------------------------
# Pack & write
# ---------------------------------------------------------------------------

output_path.parent.mkdir(parents=True, exist_ok=True)
theme_data = _pack_theme(colors_content, bg_bytes)
output_path.write_bytes(theme_data)
log.info("Telegram theme written \u2192 %s (%.2f MB)", output_path, len(theme_data) / 1024 / 1024)
