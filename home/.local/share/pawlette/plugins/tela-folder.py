"""pawlette plugin: tela-folder

Generates a derived icon theme that **inherits** from an installed
Tela icon theme and overrides only the folder icons, recoloring the
classic two-tone *default-folder* variant from the palette:
  * the folder **body**  (``class="ColorScheme-Highlight"``) -> ``color_bg_alt``
  * the top **outline / tab**  (``id="shadow"``)              -> ``color_primary``

The white "paper" top, the bottom gradient and any document glyph are
left untouched, so the result keeps the recognisable Tela folder shape
but in your pawlette palette. Every other icon (apps, devices, mime,
non-folder places, small 16/22/24 sizes, ...) falls back to the parent
Tela theme through ``Inherits=``.

Configuration (pawlette.toml)::
    [plugins.tela-folder]
    theme_name          = "Tela-pawlette"     # generated override theme name
    parent_theme        = ""                  # inherit from this Tela theme (auto)
    icons_dir           = "~/.local/share/icons"
    source_dir          = ""                  # SVG source (auto = parent theme)
    icons               = ""                  # csv default-* stems, or "all"
    set_gtk_theme       = "true"              # switch the active icon theme
    update_gtk_configs  = "true"              # also write gtk-2/3/4 + xsettingsd
"""

from __future__ import annotations

import logging
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

logging.basicConfig(format="%(levelname)-8s %(message)s", level=logging.INFO)
log = logging.getLogger("tela-folder")

SVG_NS = "{http://www.w3.org/2000/svg}"
_HEX_RE = re.compile(r"^#[0-9a-f]{3}$|^#[0-9a-f]{6}$", re.IGNORECASE)
_STYLE_COLOR_RE = re.compile(
    r"\.(ColorScheme-[A-Za-z]+)\s*\{[^}]*?color:\s*(#[0-9A-Fa-f]{6}|#[0-9A-Fa-f]{3})",
    re.IGNORECASE,
)

_INDEX_THEME = """\
[Icon Theme]
Name={name}
Comment=Tela folders recolored by pawlette (body=bg_alt, outline=accent)
Inherits={parent}
Example=folder
Directories=scalable/places

[scalable/places]
Context=Places
Size=64
MinSize=22
MaxSize=512
Type=Scalable
"""


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


def _expand(path: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(path)))


def _bool_env(key: str, default: bool) -> bool:
    v = _env(key).lower()
    return default if not v else v in ("1", "true", "yes", "on")


def _palette() -> dict[str, str]:
    return {
        k.removeprefix("PAWLETTE_").lower(): v
        for k, v in os.environ.items()
        if k.startswith("PAWLETTE_") and not k.startswith("PAWLETTE_PLUGIN_")
    }


def _replace_hex(text: str, old: str, new: str) -> str:
    """Case-insensitive literal replacement of a hex colour string."""
    if not old:
        return text
    return re.compile(re.escape(old), re.IGNORECASE).sub(new, text)


def _remove_shadow_opacity(text: str) -> str:
    """Drop ``opacity="..."`` from the ``id="shadow"`` <path> so the outline
    becomes a solid accent instead of a faint shadow."""
    def fix(m: re.Match[str]) -> str:
        return re.sub(r'\s+opacity="[^"]*"', "", m.group(0), flags=re.IGNORECASE)

    return re.compile(
        r'<path\b[^>]*?\bid="shadow"[^>]*?/?>', re.IGNORECASE
    ).sub(fix, text)


def _style_colors(text: str) -> dict[str, str]:
    return {m.group(1): m.group(2).strip().lower() for m in _STYLE_COLOR_RE.finditer(text)}


def recolor_folder_svg(svg_text: str, body_hex: str, accent_hex: str) -> str | None:
    """Recolor a Tela ``default-*.svg`` folder icon.

    Returns recolored text, or None if *svg_text* is not a recolorable
    Tela folder (no ``ColorScheme-Highlight`` body) and should be skipped.
    """
    try:
        root = ET.fromstring(svg_text)
    except ET.ParseError as exc:
        log.debug("skip: not valid XML (%s)", exc)
        return None

    body_old: str | None = None
    accent_old: str | None = None
    has_shadow = False
    for el in root.iter():
        if el.tag.split("}", 1)[-1] != "path":
            continue
        cls = el.get("class", "")
        pid = el.get("id", "")
        if "ColorScheme-Highlight" in cls and body_old is None:
            body_old = (el.get("fill") or "").strip() or None
        if pid == "shadow":
            has_shadow = True
            accent_old = (el.get("fill") or "").strip() or None

    # Fallback: body uses currentColor -> take the concrete colour from <style>.
    if not body_old or body_old.lower() in ("currentcolor", "none"):
        body_old = _style_colors(svg_text).get("ColorScheme-Highlight") or body_old

    if not body_old or not _HEX_RE.match(body_old):
        return None  # not a recolorable Tela folder

    out = _replace_hex(svg_text, body_old, body_hex)
    if accent_old and _HEX_RE.match(accent_old) and accent_old.lower() != body_old.lower():
        out = _replace_hex(out, accent_old, accent_hex)
    if has_shadow:
        out = _remove_shadow_opacity(out)
    return out


# --------------------------------------------------------------------------- #
# Tela theme discovery
# --------------------------------------------------------------------------- #

def _icon_search_dirs() -> list[Path]:
    dirs: list[Path] = []
    user = os.environ.get("XDG_DATA_HOME") or "~/.local/share"
    dirs.append(_expand(user) / "icons")
    for d in (os.environ.get("XDG_DATA_DIRS") or "/usr/share:/usr/local/share").split(":"):
        d = d.strip()
        if d:
            dirs.append(Path(d) / "icons")
    return dirs


def _find_tela_parents() -> list[Path]:
    seen: set[str] = set()
    out: list[Path] = []
    for base in _icon_search_dirs():
        if not base.is_dir():
            continue
        for d in sorted(base.iterdir()):
            if not d.is_dir() or d.name in seen:
                continue
            if d.name.startswith("Tela") and (d / "index.theme").is_file():
                # Must expose a classic default-folder source we can recolor.
                if (d / "scalable" / "places" / "default-folder.svg").is_file():
                    seen.add(d.name)
                    out.append(d)
    return out


def _current_gtk_icon_theme() -> str | None:
    if not shutil.which("gsettings"):
        return None
    try:
        r = subprocess.run(
            ["gsettings", "get", "org.gnome.desktop.interface", "icon-theme"],
            capture_output=True, text=True, timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    return r.stdout.strip().strip("'\"")


def _resolve_parent(cfg_parent: str) -> Path | None:
    parents = _find_tela_parents()
    if not parents:
        return None
    if cfg_parent:
        for p in parents:
            if p.name == cfg_parent:
                return p
    current = _current_gtk_icon_theme()
    if current:
        for p in parents:
            if p.name == current:
                return p
    # Prefer the plain (non -light/-dark) variant of whatever was installed.
    plain = [p for p in parents if not p.name.endswith(("-light", "-dark"))]
    return (plain or parents)[0]


def _resolve_source(cfg_source: str, parent: Path | None) -> Path | None:
    if cfg_source:
        p = _expand(cfg_source)
        return p if p.is_dir() else None
    if parent is not None:
        p = parent / "scalable" / "places"
        return p if p.is_dir() else None
    return None


def _resolves_to_default(name: str, src_dir: Path) -> bool:
    """True if symlink chain *name* -> ... ends at a real ``default-*.svg``."""
    seen: set[str] = set()
    cur = name
    while cur not in seen:
        seen.add(cur)
        p = src_dir / cur
        if p.is_symlink():
            target = os.readlink(p)
            if os.path.isabs(target):
                return False
            cur = os.path.normpath(target)
        elif p.is_file():
            return cur.startswith("default-") and cur.endswith(".svg")
        else:
            return False
    return False


def _default_stems(cfg_icons: str, source_dir: Path) -> list[str]:
    raw = cfg_icons.strip().lower()
    if raw in ("", "all"):
        return [
            f.name[: -len(".svg")]
            for f in sorted(source_dir.glob("default-*.svg"))
            if f.is_file()
        ]
    return [n.removeprefix("default-").strip() for n in raw.split(",") if n.strip()]


def _update_icon_cache(theme_dir: Path) -> None:
    for tool in ("gtk-update-icon-cache", "gtk4-update-icon-cache"):
        exe = shutil.which(tool)
        if not exe:
            continue
        try:
            subprocess.run([exe, "-f", str(theme_dir)], capture_output=True, timeout=20)
        except subprocess.SubprocessError:
            pass


def _set_gsettings_icon_theme(name: str) -> bool:
    """Switch the icon theme via gsettings (GTK3/GTK4 GNOME-stack).

    Returns True if set (or already set). Refuses to override a non-Tela
    current theme so we don't clobber an unrelated user choice.
    """
    if not shutil.which("gsettings"):
        return False
    current = _current_gtk_icon_theme()
    if current and not current.startswith("Tela"):
        log.info("Current icon theme is %r (not Tela) — not switching.", current)
        return False
    if current == name:
        return True
    try:
        subprocess.run(
            ["gsettings", "set", "org.gnome.desktop.interface", "icon-theme", name],
            capture_output=True, timeout=5, check=True,
        )
        log.info("gsettings icon-theme -> %s", name)
        return True
    except (subprocess.SubprocessError, OSError) as exc:
        log.warning("Could not set gsettings icon-theme: %s", exc)
        return False


def _replace_key(path: Path, pattern: re.Pattern[str], line: str) -> bool:
    """In-place replace the first line matching *pattern* with *line*.

    Adds *line* at the end if the key is absent. Returns True if the file
    was changed. Preserves every other line and original permissions.
    """
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    if pattern.search(text):
        new = pattern.sub(line, text, count=1)
    else:
        sep = "\n" if text and not text.endswith("\n") else ""
        new = text + sep + line + "\n"
    if new == text:
        return False
    path.write_text(new, encoding="utf-8")
    return True


# gtkrc / settings.ini icon-theme key matchers (quoted vs unquoted).
_GTKRC_KEY = re.compile(r'^\s*gtk-icon-theme-name="[^"]*"', re.MULTILINE)
_SETTINGS_KEY = re.compile(r'^\s*gtk-icon-theme-name=.*$', re.MULTILINE)
_XSETTINGS_KEY = re.compile(r'^\s*Net/IconThemeName\s+"[^"]*"', re.MULTILINE)


def _update_gtk_config_files(name: str) -> None:
    """Write the icon theme into the GTK2/3/4 config files.

    gsettings covers GTK3/4 on GNOME-like DEs, but on wlroots/sway/Hyprland
    GTK reads ~/.config/gtk-3.0/settings.ini and ~/.config/gtk-4.0/settings.ini
    (often managed by nwg-look), and GTK2 reads ~/.config/gtk-2.0/gtkrc.
    Without these, file managers and legacy apps keep the old icon theme.
    """
    config = Path(os.environ.get("XDG_CONFIG_HOME") or "~/.config").expanduser()
    targets = (
        (config / "gtk-2.0" / "gtkrc", _GTKRC_KEY, f'gtk-icon-theme-name="{name}"'),
        (config / "gtk-3.0" / "settings.ini", _SETTINGS_KEY, f"gtk-icon-theme-name={name}"),
        (config / "gtk-4.0" / "settings.ini", _SETTINGS_KEY, f"gtk-icon-theme-name={name}"),
    )
    for path, pat, line in targets:
        if _replace_key(path, pat, line):
            log.info("%s: gtk-icon-theme-name -> %s", path, name)
        elif path.is_file():
            log.debug("%s already references %s", path, name)


def _update_xsettingsd(name: str) -> None:
    """Update xsettingsd.conf and reload xsettingsd if it is running."""
    config = Path(os.environ.get("XDG_CONFIG_HOME") or "~/.config").expanduser()
    conf = config / "xsettingsd" / "xsettingsd.conf"
    if not conf.is_file():
        return
    if _replace_key(conf, _XSETTINGS_KEY, f'Net/IconThemeName "{name}"'):
        log.info("%s: Net/IconThemeName -> %s", conf, name)
    # xsettingsd has no SIGHUP reload — restart it so live X11 apps pick up
    # the new theme. Only touch it if the user is actually running it.
    try:
        out = subprocess.run(
            ["pgrep", "-x", "xsettingsd"], capture_output=True, text=True, timeout=3,
        )
    except (OSError, subprocess.SubprocessError):
        return
    if out.returncode != 0 or not out.stdout.strip():
        return  # not running — file updated, takes effect on next start
    exe = shutil.which("xsettingsd")
    if not exe:
        log.warning("xsettingsd is running but its binary is not on PATH — "
                    "restart it manually to apply the new icon theme.")
        return
    try:
        subprocess.run(["pkill", "-x", "xsettingsd"], timeout=3)
        subprocess.Popen(
            [exe, "-f", str(conf)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        log.info("xsettingsd restarted")
    except (OSError, subprocess.SubprocessError) as exc:
        log.warning("Could not restart xsettingsd: %s", exc)


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main() -> int:
    pal = _palette()
    body_hex = (pal.get("color_bg_alt") or "#181825").strip().lower()
    accent_hex = (
        pal.get("color_primary") or pal.get("color_secondary") or "#cba6f7"
    ).strip().lower()

    theme_name = _env("PAWLETTE_PLUGIN_THEME_NAME", "Tela-pawlette") or "Tela-pawlette"
    icons_dir = _expand(_env("PAWLETTE_PLUGIN_ICONS_DIR", "~/.local/share/icons"))
    cfg_parent = _env("PAWLETTE_PLUGIN_PARENT_THEME")
    cfg_source = _env("PAWLETTE_PLUGIN_SOURCE_DIR")
    cfg_icons = _env("PAWLETTE_PLUGIN_ICONS").lower()
    do_set = _bool_env("PAWLETTE_PLUGIN_SET_GTK_THEME", True)
    do_configs = _bool_env("PAWLETTE_PLUGIN_UPDATE_GTK_CONFIGS", True)

    parent = _resolve_parent(cfg_parent)
    parent_name = (parent.name if parent else cfg_parent) or "Tela-circle"

    source_dir = _resolve_source(cfg_source, parent)
    if source_dir is None or not source_dir.is_dir():
        log.warning(
            "No Tela source found. Install a Tela icon theme "
            "(e.g. ./Tela-circle-icon-theme/install.sh dracula) or set "
            "'source_dir' in [plugins.tela-folder]. Skipping."
        )
        return 0

    stems = _default_stems(cfg_icons, source_dir)
    if not stems:
        log.warning("No default-*.svg folder icons found in %s. Skipping.", source_dir)
        return 0

    theme_dir = icons_dir / theme_name
    places_dir = theme_dir / "scalable" / "places"
    if theme_dir.exists():
        shutil.rmtree(theme_dir)
    places_dir.mkdir(parents=True, exist_ok=True)

    # 1) Recolored real default-*.svg files.
    written = 0
    skipped = 0
    for stem in stems:
        src = source_dir / f"{stem}.svg"
        if not src.is_file() or src.is_symlink():
            skipped += 1
            continue
        out = recolor_folder_svg(src.read_text(encoding="utf-8"), body_hex, accent_hex)
        if out is None:
            skipped += 1
            log.debug("skip (not a two-tone Tela folder): %s", src.name)
            continue
        (places_dir / f"{stem}.svg").write_text(out, encoding="utf-8")
        written += 1

    # 2) Copy alias symlinks whose chain resolves to one of our default-*.svg
    #    (e.g. folder.svg -> default-folder.svg, folder-home.svg -> user-home.svg
    #     -> default-user-home.svg). Kept as relative symlinks so chains work
    #    locally inside the override theme.
    aliases = 0
    for entry in sorted(source_dir.iterdir()):
        if not entry.is_symlink():
            continue
        if not _resolves_to_default(entry.name, source_dir):
            continue
        target = os.readlink(entry)
        dst = places_dir / entry.name
        if dst.exists() or dst.is_symlink():
            continue
        try:
            os.symlink(target, dst)
            aliases += 1
        except OSError as exc:
            log.debug("could not symlink %s -> %s: %s", entry.name, target, exc)

    (theme_dir / "index.theme").write_text(
        _INDEX_THEME.format(name=theme_name, parent=parent_name), encoding="utf-8"
    )
    _update_icon_cache(theme_dir)

    log.info(
        "Recolored %d folder icon(s), %d alias(es) -> %s "
        "(inherit %s, body=%s, outline=%s)",
        written, aliases, theme_dir, parent_name, body_hex, accent_hex,
    )
    if skipped:
        log.debug("Skipped %d source icon(s) (missing or not recolorable).", skipped)

    if written == 0:
        log.warning("No icons were recolored — override theme is empty.")
        return 0
    if do_set:
        _set_gsettings_icon_theme(theme_name)
    if do_configs:
        _update_gtk_config_files(theme_name)
        _update_xsettingsd(theme_name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
