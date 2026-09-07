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

# published slot order: 7 accents, then the neutral ramp from text down to crust
ORDER = [
    "gold",
    "red",
    "orange",
    "green",
    "cyan",
    "blue",
    "purple",
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


def swatch(*, hex_value: str) -> dict[str, Any]:
    colour = Color(hex_value)
    return {
        "hex": hex_value,
        "rgb": rgb(colour=colour),
        "hsl": hsl(colour=colour),
        "oklch": oklch(colour=colour),
    }


def color(*, name: str, hex_value: str, accent: bool, order: int) -> ColorEntry:
    return {"name": name, "order": order, **swatch(hex_value=hex_value), "accent": accent}


def build_mode(*, src: dict) -> Mode:
    colors = {}
    for index, slot in enumerate(ORDER):
        colors[slot] = color(
            name=src["colors"][slot]["name"],
            hex_value=src["colors"][slot]["hex"],
            accent=src["colors"][slot]["accent"],
            order=index,
        )

    ansi = {}
    for index, name in enumerate(ANSI):
        entry = src["ansiColors"][name]
        ansi[name] = {
            "name": entry["name"],
            "order": index,
            "normal": {
                "name": entry["normal"]["name"],
                "code": entry["normal"]["code"],
                **swatch(hex_value=entry["normal"]["hex"]),
            },
            "bright": {
                "name": entry["bright"]["name"],
                "code": entry["bright"]["code"],
                **swatch(hex_value=entry["bright"]["hex"]),
            },
        }

    return {"colors": colors, "ansiColors": ansi}


def build_theme(*, src: dict, order: int) -> Theme:
    return {
        "name": src["name"],
        "order": order,
        "dark": build_mode(src=src["dark"]),
        "light": build_mode(src=src["light"]),
    }


def flatten(*, themes: dict[str, Theme]) -> dict[str, Mode]:
    # one entry per theme and mode, keyed <theme>-<mode>, for the flat text formats
    return {
        f"{key}-{mode}": theme[mode] for key, theme in themes.items() for mode in ("dark", "light")
    }


def gpl(*, name: str, mode: Mode) -> str:
    # 7 columns puts the accents on the first row and the neutrals on the second
    lines = ["GIMP Palette", f"Name: Orikalk {name}", "Columns: 7"]
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
    (DIST / "gimp").mkdir(parents=True)
    (DIST / "palette.json").write_text(
        json.dumps({"version": src["version"], **themes}, indent=2) + "\n"
    )
    for key, theme in themes.items():
        for mode in ("dark", "light"):
            (DIST / "gimp" / f"orikalk-{key}-{mode}.gpl").write_text(
                gpl(name=f"{theme['name']} {mode.capitalize()}", mode=theme[mode])
            )


if __name__ == "__main__":
    main()
