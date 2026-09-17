import argparse
import json
import shutil
import sys
from pathlib import Path

from coloraide import Color

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
PALETTE = ROOT / "palette.json"

ANCHOR = {"dark": "crust", "light": "base"}

RAMP = {
    "dark": {
        "crust": (0.0, 0.0, 0.0),
        "mantle": (0.0543, 0.0002, 0.8544),
        "base": (0.0817, 0.0052, 0.7007),
        "surface0": (0.1628, 0.0067, -1.2318),
        "surface1": (0.2425, 0.0068, -3.0583),
        "surface2": (0.3153, 0.0088, -4.5672),
        "overlay0": (0.3885, 0.0093, -6.1152),
        "overlay1": (0.4564, 0.0115, -7.2056),
        "overlay2": (0.5253, 0.0122, -8.485),
        "subtext0": (0.5898, 0.0144, -9.2783),
        "subtext1": (0.6556, 0.0152, -10.3481),
        "text": (0.7175, 0.0174, -10.9335),
    },
    "light": {
        "crust": (-0.0507, -0.0005, -2.6467),
        "mantle": (-0.0243, 0.0002, 0.006),
        "base": (0.0, 0.0, 0.0),
        "surface0": (-0.099, -0.001, -5.4643),
        "surface1": (-0.1459, -0.0006, -5.4651),
        "surface2": (-0.1956, -0.0009, -8.4645),
        "overlay0": (-0.2441, -0.0004, -8.4786),
        "overlay1": (-0.2989, -0.0006, -11.6707),
        "overlay2": (-0.349, -0.0013, -13.0093),
        "subtext0": (-0.4036, -0.0018, -14.4842),
        "subtext1": (-0.4564, -0.0012, -14.573),
        "text": (-0.5127, -0.0021, -20.1404),
    },
}

ANSI_ALIASES = {
    "dark": {"black": ("surface1", "surface2"), "white": ("subtext0", "text")},
    "light": {"black": ("subtext1", "subtext0"), "white": ("surface2", "surface1")},
}

ANSI_MAP = {
    "red": "red",
    "green": "green",
    "yellow": "gold",
    "blue": "blue",
    "magenta": "purple",
    "cyan": "cyan",
}

LIFT = 0.04


def build() -> None:
    src = json.loads(PALETTE.read_bytes())
    out = DIST / "gimp"
    shutil.rmtree(DIST, ignore_errors=True)
    out.mkdir(parents=True)
    for key, theme in src.items():
        if key == "version":
            continue
        for mode_key in ("dark", "light"):
            mode = theme[mode_key]
            entries = list(mode["colors"].values())
            for variant in ("normal", "bright"):
                entries.extend(ansi[variant] for ansi in mode["ansiColors"].values())
            lines = [
                "GIMP Palette",
                f"Name: Orikalk {theme['name']} {mode_key.capitalize()}",
                "Columns: 8",
            ]
            for entry in entries:
                r, g, b = bytes.fromhex(entry["hex"].removeprefix("#"))
                lines.append(f"{r:3} {g:3} {b:3} {entry['name']}")
            content = "\n".join(lines) + "\n"
            target = out / f"orikalk-{key}-{mode_key}.gpl"
            target.write_text(content, encoding="utf-8", newline="\n")


def ramp(*, mode_key: str, anchor_hex: str) -> dict[str, str]:
    anchor = Color(anchor_hex).convert("oklch")
    channels = ("lightness", "chroma", "hue")
    out = {}
    for slot, deltas in RAMP[mode_key].items():
        coords = [anchor[c] + d for c, d in zip(channels, deltas, strict=True)]
        out[slot] = Color("oklch", coords).fit("srgb").convert("srgb").to_string(hex=True)
    return out


def lifted(*, hex_value: str) -> str:
    colour = Color(hex_value).convert("oklch")
    colour["lightness"] += LIFT
    return colour.fit("srgb", method="oklch-chroma").convert("srgb").to_string(hex=True)


def expected(*, mode: dict, mode_key: str) -> dict[str, str]:
    colors = mode["colors"]
    out = ramp(mode_key=mode_key, anchor_hex=colors[ANCHOR[mode_key]]["hex"])
    for name, (normal, bright) in ANSI_ALIASES[mode_key].items():
        out[f"ansi {name} normal"] = colors[normal]["hex"]
        out[f"ansi {name} bright"] = colors[bright]["hex"]
    for name, slot in ANSI_MAP.items():
        out[f"ansi {name} normal"] = colors[slot]["hex"]
        out[f"ansi {name} bright"] = lifted(hex_value=colors[slot]["hex"])
    return out


def actual(*, mode: dict) -> dict[str, str]:
    out = {slot: entry["hex"] for slot, entry in mode["colors"].items()}
    for name, entry in mode["ansiColors"].items():
        out[f"ansi {name} normal"] = entry["normal"]["hex"]
        out[f"ansi {name} bright"] = entry["bright"]["hex"]
    return out


def check() -> None:
    src = json.loads(PALETTE.read_bytes())
    errors = []
    for key, theme in src.items():
        if key == "version":
            continue
        for mode_key in ("dark", "light"):
            mode = theme[mode_key]
            found = actual(mode=mode)
            for label, hex_value in expected(mode=mode, mode_key=mode_key).items():
                if found[label] != hex_value:
                    errors.append(f"{key} {mode_key} {label}: {found[label]}, expected {hex_value}")
    if errors:
        sys.exit("\n".join(errors))


def main() -> None:
    parser = argparse.ArgumentParser(prog="orikalk")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("build")
    sub.add_parser("check")
    args = parser.parse_args()
    if args.command == "build":
        build()
    elif args.command == "check":
        check()


if __name__ == "__main__":
    main()
