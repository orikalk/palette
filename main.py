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

ANSI = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]


def rgb(*, colour: Color) -> dict[str, int]:
    out = {}
    for channel in "rgb":
        out[channel] = round(colour[channel] * 255)
    return out


def swatch(*, hex_value: str) -> dict[str, Any]:
    return {"hex": hex_value, "rgb": rgb(colour=Color(hex_value))}


def color(*, name: str, hex_value: str) -> ColorEntry:
    return {"name": name, **swatch(hex_value=hex_value)}


def build_mode(*, src: dict) -> Mode:
    colors = {}
    for slot, entry in src["colors"].items():
        colors[slot] = color(name=entry["name"], hex_value=entry["hex"])

    ansi = {}
    for name in ANSI:
        entry = src["ansiColors"][name]
        ansi[name] = {
            "name": entry["name"],
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

    return {"name": src["name"], "colors": colors, "ansiColors": ansi}


def build_theme(*, src: dict) -> Theme:
    return {
        "name": src["name"],
        "stone": src["stone"],
        "dark": build_mode(src=src["dark"]),
        "light": build_mode(src=src["light"]),
    }


def gpl(*, name: str, mode: Mode) -> str:
    # 7 columns puts the accents on the first row and the neutrals on the second
    lines = ["GIMP Palette", f"Name: Orikalk {name}", "Columns: 7"]
    for colour in mode["colors"].values():
        rgb_value = colour["rgb"]
        lines.append(f"{rgb_value['r']:3} {rgb_value['g']:3} {rgb_value['b']:3} {colour['name']}")
    return "\n".join(lines) + "\n"


def main() -> None:
    src = json.loads((ROOT / "palette.json").read_text())
    themes = {key: build_theme(src=theme) for key, theme in src.items() if key != "version"}

    shutil.rmtree(DIST, ignore_errors=True)
    (DIST / "gimp").mkdir(parents=True)
    for key, theme in themes.items():
        for mode in ("dark", "light"):
            (DIST / "gimp" / f"orikalk-{key}-{mode}.gpl").write_text(
                gpl(name=f"{theme['name']} {mode.capitalize()}", mode=theme[mode])
            )


if __name__ == "__main__":
    main()
