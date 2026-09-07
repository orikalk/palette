import argparse
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

SLOTS = [
    "crust",
    "mantle",
    "base",
    "surface0",
    "surface1",
    "surface2",
    "overlay0",
    "overlay1",
    "overlay2",
    "subtext0",
    "subtext1",
    "text",
]

REFERENCE = {
    "dark": {
        "crust": "#0c0c18",
        "mantle": "#181825",
        "base": "#1e1e2e",
        "surface0": "#313244",
        "surface1": "#45475a",
        "surface2": "#585b70",
        "overlay0": "#6c7086",
        "overlay1": "#7f849c",
        "overlay2": "#9399b2",
        "subtext0": "#a6adc8",
        "subtext1": "#bac2de",
        "text": "#cdd6f4",
    },
    "light": {
        "crust": "#e1d8c2",
        "mantle": "#e9e1ca",
        "base": "#f1e9d2",
        "surface0": "#d2c8b3",
        "surface1": "#c3b9a4",
        "surface2": "#b4a995",
        "overlay0": "#a59a86",
        "overlay1": "#958976",
        "overlay2": "#867a68",
        "subtext0": "#766a59",
        "subtext1": "#675b4a",
        "text": "#584b3c",
    },
}

ANCHOR = {"dark": "crust", "light": "base"}

ANSI_MAP = {
    "red": "red",
    "green": "green",
    "yellow": "gold",
    "blue": "blue",
    "magenta": "purple",
    "cyan": "cyan",
}

ANSI_ALIASES = {
    "dark": {"black": ("surface1", "surface2"), "white": ("subtext0", "text")},
    "light": {"black": ("subtext1", "subtext0"), "white": ("surface2", "surface1")},
}

LIFT = 0.04


def to_oklch(*, hex_value: str) -> Color:
    return Color(hex_value).convert("oklch")


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


def flat_slots(*, mode: Mode) -> dict[str, ColorEntry]:
    out = dict(mode["colors"])
    for name, entry in mode["ansiColors"].items():
        out[f"ansi-{name}"] = entry["normal"]
    for name, entry in mode["ansiColors"].items():
        out[f"ansi-bright-{name}"] = entry["bright"]
    return out


def build_theme(*, src: dict) -> Theme:
    return {
        "name": src["name"],
        "stone": src["stone"],
        "dark": build_mode(src=src["dark"]),
        "light": build_mode(src=src["light"]),
    }


def gpl(*, name: str, mode: Mode) -> str:
    lines = ["GIMP Palette", f"Name: Orikalk {name}", "Columns: 8"]
    for colour in flat_slots(mode=mode).values():
        rgb_value = colour["rgb"]
        lines.append(f"{rgb_value['r']:3} {rgb_value['g']:3} {rgb_value['b']:3} {colour['name']}")
    return "\n".join(lines) + "\n"


def build(*, path: Path) -> None:
    src = json.loads(path.read_text())
    themes = {key: build_theme(src=theme) for key, theme in src.items() if key != "version"}

    shutil.rmtree(DIST, ignore_errors=True)
    (DIST / "gimp").mkdir(parents=True)
    for key, theme in themes.items():
        for mode in ("dark", "light"):
            (DIST / "gimp" / f"orikalk-{key}-{mode}.gpl").write_text(
                gpl(name=f"{theme['name']} {mode.capitalize()}", mode=theme[mode])
            )


def shifted(*, hex_value: str, delta: float) -> str:
    colour = to_oklch(hex_value=hex_value)
    colour["lightness"] += delta
    return colour.fit("srgb", method="oklch-chroma").convert("srgb").to_string(hex=True)


def ramp(*, reference: dict[str, str], anchor_slot: str, anchor_hex: str) -> dict[str, str]:
    anchor = to_oklch(hex_value=anchor_hex)
    origin = to_oklch(hex_value=reference[anchor_slot])
    out = {}
    for slot in SLOTS:
        step = to_oklch(hex_value=reference[slot])
        colour = Color(
            "oklch",
            [
                anchor["lightness"] + step["lightness"] - origin["lightness"],
                anchor["chroma"] + step["chroma"] - origin["chroma"],
                anchor["hue"] + step["hue"] - origin["hue"],
            ],
        ).fit("srgb")
        out[slot] = colour.convert("srgb").to_string(hex=True)
    return out


def derive_mode(*, mode: dict, mode_key: str) -> None:
    colors = mode["colors"]
    ansi = mode["ansiColors"]
    derived = ramp(
        reference=REFERENCE[mode_key],
        anchor_slot=ANCHOR[mode_key],
        anchor_hex=colors[ANCHOR[mode_key]]["hex"],
    )
    for slot, hex_value in derived.items():
        colors[slot]["hex"] = hex_value
    for name, (normal, bright) in ANSI_ALIASES[mode_key].items():
        ansi[name]["normal"]["hex"] = derived[normal]
        ansi[name]["bright"]["hex"] = derived[bright]
    for name, slot in ANSI_MAP.items():
        hex_value = colors[slot]["hex"]
        ansi[name]["normal"]["hex"] = hex_value
        ansi[name]["bright"]["hex"] = shifted(hex_value=hex_value, delta=LIFT)


def derive(*, path: Path) -> None:
    data = json.loads(path.read_text())
    for key, theme in data.items():
        if key == "version":
            continue
        for mode_key in ("dark", "light"):
            derive_mode(mode=theme[mode_key], mode_key=mode_key)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["build", "derive"], nargs="?", default="build")
    parser.add_argument("palette", nargs="?", type=Path, default=ROOT / "palette.json")
    args = parser.parse_args()
    {"build": build, "derive": derive}[args.command](path=args.palette)
