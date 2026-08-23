import json
import shutil
from pathlib import Path
from typing import Any

from coloraide import Color

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"

type ColorEntry = dict[str, Any]
type Mode = dict[str, Any]
type Theme = dict[str, Any]

# published slot order: 14 accents, then the neutral ramp from text down to crust
ORDER = [
    "salmon",
    "coral",
    "pink",
    "purple",
    "red",
    "maroon",
    "orange",
    "yellow",
    "green",
    "teal",
    "cyan",
    "sky",
    "blue",
    "lavender",
    "text",
    "subtext1",
    "subtext0",
    "overlay2",
    "overlay1",
    "overlay0",
    "surface2",
    "surface1",
    "surface0",
    "base",
    "mantle",
    "crust",
]

# wcag 2.1 ratios against base, the readability floor every flavour has to clear
CONTRAST = {"accent": 3.0, "text": 7.0}

ANSI = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
ANSI_SLOTS = {
    "red": "red",
    "green": "green",
    "yellow": "yellow",
    "blue": "blue",
    "magenta": "pink",
    "cyan": "teal",
}


def rgb(*, colour: Color) -> dict[str, int]:
    out = {}
    for channel in "rgb":
        out[channel] = round(colour[channel] * 255)
    return out


def hsl(*, colour: Color) -> dict[str, float]:
    converted = colour.convert("hsl")
    return {
        "h": round(converted["hue"], 3),
        "s": round(converted["saturation"], 3),
        "l": round(converted["lightness"], 3),
    }


def oklch(*, colour: Color) -> dict[str, float]:
    converted = colour.convert("oklch")
    return {
        "l": round(converted["lightness"], 4),
        "c": round(converted["chroma"], 4),
        "h": round(converted["hue"], 4),
    }


def color(*, name: str, hex_value: str, accent: bool, order: int) -> ColorEntry:
    colour = Color(hex_value)
    return {
        "name": name,
        "order": order,
        "hex": hex_value,
        "rgb": rgb(colour=colour),
        "hsl": hsl(colour=colour),
        "oklch": oklch(colour=colour),
        "accent": accent,
    }


def build_mode(*, src: dict, dark: bool) -> Mode:
    colors = {}
    for index, slot in enumerate(ORDER):
        colors[slot] = color(
            name=src["colors"][slot]["name"],
            hex_value=src["colors"][slot]["hex"],
            accent=src["colors"][slot]["accent"],
            order=index,
        )

    # terminal black and white sit one step in from text and base so they stay readable,
    # bright is one step further out
    if dark:
        neutral = {
            "black": ("surface1", "surface2"),
            "white": ("subtext0", "subtext1"),
        }
    else:
        neutral = {
            "black": ("subtext1", "subtext0"),
            "white": ("surface2", "surface1"),
        }

    ansi = {}
    for index, name in enumerate(ANSI):
        # accents have no lightened bright variant, bright reuses normal on purpose
        normal, bright = neutral.get(name) or (ANSI_SLOTS[name],) * 2
        normal_color = {"code": index}
        bright_color = {"code": index + 8}
        for field in ("hex", "rgb", "hsl", "oklch"):
            normal_color[field] = colors[normal][field]
            bright_color[field] = colors[bright][field]

        ansi[name] = {
            "name": name.capitalize(),
            "order": index,
            "normal": normal_color,
            "bright": bright_color,
        }

    return {"colors": colors, "ansiColors": ansi}


def build_theme(*, src: dict, order: int) -> Theme:
    return {
        "name": src["name"],
        "order": order,
        "dark": build_mode(src=src["dark"], dark=True),
        "light": build_mode(src=src["light"], dark=False),
    }


def flatten(*, themes: dict[str, Theme]) -> dict[str, Mode]:
    # one entry per theme and mode, keyed <theme>-<mode>, for the flat text formats
    return {
        f"{key}-{mode}": theme[mode] for key, theme in themes.items() for mode in ("dark", "light")
    }


def css(*, modes: dict[str, Mode]) -> str:
    out = []
    for key, mode in modes.items():
        lines = []
        for slot, colour in mode["colors"].items():
            rgb_value, hsl_value, oklch_value = colour["rgb"], colour["hsl"], colour["oklch"]
            lines.append(f"  --{key}-{slot}: {colour['hex']};")
            lines.append(
                f"  --{key}-{slot}-rgb: {rgb_value['r']} {rgb_value['g']} {rgb_value['b']};"
            )
            lines.append(
                f"  --{key}-{slot}-hsl: {hsl_value['h']} "
                f"{hsl_value['s'] * 100:.1f}% {hsl_value['l'] * 100:.1f}%;"
            )
            lines.append(
                f"  --{key}-{slot}-oklch: {oklch_value['l']} {oklch_value['c']} {oklch_value['h']};"
            )

        out.append(":root {\n" + "\n".join(lines) + "\n}")
    return "\n\n".join(out) + "\n"


def scss_mode(*, mode: Mode) -> str:
    lines = []
    for slot, colour in mode["colors"].items():
        lines.append(f"${slot}: {colour['hex']};")
    return "\n".join(lines) + "\n"


def scss_map(*, modes: dict[str, Mode]) -> str:
    blocks = []
    for key, mode in modes.items():
        colors = []
        for slot, colour in mode["colors"].items():
            colors.append(f'    "{slot}": {colour["hex"]}')
        blocks.append(f'  "{key}": (\n' + ",\n".join(colors) + "\n  )")
    return "$palette: (\n" + ",\n".join(blocks) + "\n);\n"


def gpl(*, name: str, mode: Mode) -> str:
    # 14 columns puts the accents on the first row and the neutrals on the second
    lines = ["GIMP Palette", f"Name: Orikalk {name}", "Columns: 14"]
    for colour in mode["colors"].values():
        rgb_value = colour["rgb"]
        lines.append(f"{rgb_value['r']:3} {rgb_value['g']:3} {rgb_value['b']:3} {colour['name']}")
    return "\n".join(lines) + "\n"


def contrast_failures(*, modes: dict[str, Mode]) -> list[str]:
    failures = []
    for key, mode in modes.items():
        base = Color(mode["colors"]["base"]["hex"])
        for slot, colour in mode["colors"].items():
            if colour["accent"]:
                floor = CONTRAST["accent"]
            elif slot == "text":
                floor = CONTRAST["text"]
            else:
                continue
            ratio = Color(colour["hex"]).contrast(base, method="wcag21")
            if ratio < floor:
                failures.append(
                    f"{key} {slot} {colour['hex']} is {ratio:.2f}:1 on base, needs {floor}:1"
                )
    return failures


def main() -> None:
    src = json.loads((ROOT / "palette.json").read_text())
    themes = {}
    for key in src:
        if key != "version":
            themes[key] = build_theme(src=src[key], order=len(themes))
    modes = flatten(themes=themes)

    failures = contrast_failures(modes=modes)
    if failures:
        raise SystemExit("\n".join(failures))

    shutil.rmtree(DIST, ignore_errors=True)
    for sub in ("css", "scss", "gimp"):
        (DIST / sub).mkdir(parents=True)
    (DIST / "palette.json").write_text(
        json.dumps({"version": src["version"], **themes}, indent=2) + "\n"
    )
    (DIST / "css" / "orikalk.css").write_text(css(modes=modes))
    (DIST / "scss" / "_orikalk.scss").write_text(scss_map(modes=modes))
    for key, theme in themes.items():
        for mode in ("dark", "light"):
            (DIST / "scss" / f"_{key}-{mode}.scss").write_text(scss_mode(mode=theme[mode]))
            (DIST / "gimp" / f"orikalk-{key}-{mode}.gpl").write_text(
                gpl(name=f"{theme['name']} {mode.capitalize()}", mode=theme[mode])
            )


if __name__ == "__main__":
    main()
