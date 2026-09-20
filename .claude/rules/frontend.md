---
paths:
  - "static_global/**"
---

# Frontend Rules

## Stack

jQuery, CSS, Bootstrap, SASS

## Commands

```bash
# Compile SASS to CSS (watches for changes, runs continuously)
gulp

# Install node packages (first time setup)
npm install
```

## Working Directory

- `static_global/css` is the destination directory for compiled css styles, served to the client.
- `static_global/js` is the destination directory for compiled javascript, served to the client.
- `static_global/js_source` is the source that javascript is compiled from and where the javascript code is written.
- `static_global/sass` is where the SASS files are written to and compiled from

## Code Style

- prefer on server work with a request/response design.
- use bootstrap styles
- Bootstrap is loaded via CDN
- SASS source lives under `static_global/`. 
- Gulp compiles SASS source to CSS using `gulp-sass` (Dart Sass). 
- Template files are in `talesofvalor/templates/` (global) and `<app>/templates/` (per-app).
