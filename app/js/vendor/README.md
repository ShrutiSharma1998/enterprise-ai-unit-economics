# Vendored library

`xlsx.full.min.js` is SheetJS's community edition (the npm `xlsx` package), version 0.18.5, from
`https://registry.npmjs.org/xlsx/-/xlsx-0.18.5.tgz`, its `dist/xlsx.full.min.js` build. Copyright the SheetJS
developers, licensed under the Apache License, Version 2.0; the licence text is `xlsx-LICENSE.txt` in this folder,
copied unmodified from the package. See `NOTICE` at the repository root.

It is vendored (checked in) rather than loaded from a CDN so the calculator makes no network requests once the
page is open. It is unmodified. To update it: download a newer version's tarball, replace both files here with
the new `dist/xlsx.full.min.js` and `dist/LICENSE`, update the version number above and in `NOTICE`, then run the
calculator's tests (`node --test app/tests/*.test.js`).
