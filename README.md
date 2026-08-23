# Orikalk

A blue and gold colour palette in two flavours, drawing on [Ithya](https://www.blueturtle-design.com/), alchemy and faience.

## Roles

### Backgrounds

| Slot | Use |
| --- | --- |
| base | main background |
| mantle | sidebars, secondary panes |
| crust | borders, status bars |
| surface0 to surface2 | selections, inputs, cards, increasing prominence |
| overlay0 to overlay2 | muted borders, hover states |

### Text

| Slot | Use |
| --- | --- |
| text | body |
| subtext1, subtext0 | secondary text, decreasing prominence |
| overlay2 | comments, disabled text |

### Accents

| Slot | Use |
| --- | --- |
| red | errors |
| yellow | warnings, types |
| green | success, strings |
| blue | links, functions |
| purple | keywords |
| orange | numbers |
| cyan | operators |

### Terminal

| ANSI | Slot |
| --- | --- |
| black, white | neutral ramp, by flavour |
| red, green, yellow, blue | same slot |
| magenta | pink |
| cyan | teal |

Bright variants reuse the normal value, except black and white, which step one slot along the neutral ramp.

## Usage

Each [release](https://github.com/orikalk/palette/releases/latest) carries the built formats:

| Use | File |
| --- | --- |
| JSON with `order`, `rgb`, `hsl`, `oklch` and `ansiColors` | `palette.json` |
| CSS custom properties, see [docs/css.md](docs/css.md) | `css/orikalk.css` |
| Sass variables and map, see [docs/sass.md](docs/sass.md) | `scss/` |
| Aseprite, GIMP, Inkscape, Krita | `gimp/orikalk-<flavour>.gpl` |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
