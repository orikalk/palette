# Orikalk for CSS

Import the palette from a [release](https://github.com/orikalk/palette/releases/latest):

```css
@import url("orikalk.css");
```

Then use it:

```css
.my-div {
  color:        var(--lapis-text);
  background:   rgb(var(--lapis-base-rgb) / 0.9);
  border-color: hsl(var(--electrum-red-hsl) / 0.75);
}
```

Every slot exists as `--<flavour>-<slot>` (hex), `--<flavour>-<slot>-rgb` (space separated channels), `--<flavour>-<slot>-hsl` and `--<flavour>-<slot>-oklch`.
