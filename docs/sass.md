# Orikalk for Sass

Two ways to use the files from a [release](https://github.com/orikalk/palette/releases/latest).

## Import one mode

`_<theme>-<mode>.scss` files such as `_lapis-dark.scss` define one variable per slot, namespaced by `@use`.

Input:

```scss
@use "lapis-dark";

.my-lapis-class {
  background: lapis-dark.$base;
  color: lapis-dark.$text;
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

`_orikalk.scss` defines `$palette`, a map of `<theme>-<mode>` to slot map. Quote slot names when reading the map.

Input:

```scss
@use "sass:map";
@use "orikalk";

@each $mode, $color in orikalk.$palette {
  .my-#{$mode}-class {
    background: #{map.get($color, "base")};
    color: #{map.get($color, "blue")};
  }
}
```

Output:

```css
.my-lapis-dark-class {
  background: #232b3d;
  color: #4a76b8;
}

.my-lapis-light-class {
  background: #e8dfcd;
  color: #3d5a94;
}
```
