# Orikalk for Sass

Two ways to use the files from a [release](https://github.com/orikalk/palette/releases/latest).

## Import one flavour

`_electrum.scss` and `_lapis.scss` define one variable per slot, namespaced by `@use`.

Input:

```scss
@use "lapis";

.my-lapis-class {
  background: lapis.$base;
  color: lapis.$text;
}
```

Output:

```css
.my-lapis-class {
  background: #232b3d;
  color: #e6dcc4;
}
```

## Import the single map

`_orikalk.scss` defines `$palette`, a map of flavour to slot map. Quote slot names when reading the map.

Input:

```scss
@use "sass:map";
@use "orikalk";

@each $flavour, $color in orikalk.$palette {
  .my-#{$flavour}-class {
    background: #{map.get($color, "base")};
    color: #{map.get($color, "blue")};
  }
}
```

Output:

```css
.my-electrum-class {
  background: #e8dfcd;
  color: #3d5a94;
}

.my-lapis-class {
  background: #232b3d;
  color: #4a76b8;
}
```
