# Orikalk

Gold on coloured stone. A colour palette drawing on [Ithya](https://www.blueturtle-design.com/), alchemy and faience.

Each theme is named after a stone and tints the backgrounds with its colour, in a dark and a light mode. The gold accent stays the same across all of them.

## Slots

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
| yellow | highlights, warnings, types |
| red | errors |
| green | success, strings |
| blue | links, functions |
| purple | keywords |
| orange | numbers |
| cyan | operators |

Terminal colours are derived from the slots.

## Files

Every [release](https://github.com/orikalk/palette/releases/latest) ships:

| File | What it is |
| --- | --- |
| `palette.json` | every slot with `order`, `rgb`, `hsl`, `oklch`, plus `ansiColors`, nested theme then mode |
| `css/orikalk.css` | custom properties, `--<theme>-<mode>-<slot>`, see [docs/css.md](docs/css.md) |
| `scss/` | one file per mode and a `$palette` map, see [docs/sass.md](docs/sass.md) |
| `gimp/orikalk-<theme>-<mode>.gpl` | for Aseprite, GIMP, Inkscape, Krita |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Acknowledgements

- [catppuccin](https://github.com/catppuccin)
- [Ithya](https://www.blueturtle-design.com/)
