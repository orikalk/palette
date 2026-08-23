# Orikalk for CSS

Import the palette from a [release](https://github.com/orikalk/palette/releases/latest):

```css
@import url("orikalk.css");
```

Then use it:

```css
.my-div {
  color:        var(--lapis-dark-text);
  background:   rgb(var(--lapis-dark-base-rgb) / 0.9);
  border-color: hsl(var(--lapis-light-red-hsl) / 0.75);
}
```

Every slot exists as `--<theme>-<mode>-<slot>` (hex), `--<theme>-<mode>-<slot>-rgb` (space separated channels), `--<theme>-<mode>-<slot>-hsl` and `--<theme>-<mode>-<slot>-oklch`.
