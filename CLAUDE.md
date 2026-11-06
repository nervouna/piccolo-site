# piccolo-site

The README is the reference; these are the rules that are easy to miss.

- Edit `src/index.html` and `src/strings/*.json`, then run `scripts/build.py`; never edit the generated `index.html` or `<language>/index.html`. Commit both.
- Every new text goes into all nine strings files; action names and terms come from the app's String Catalogs and the glossary in its `docs/glossary.md`.
- Chinese and Japanese strings have no spaces next to Latin text or digits (`text-autospace` adds the gap), except in attribute strings (title, description, labels, alt).
- After any text or layout change, serve the site and run `scripts/check-wrap.js` in the browser: it must return an empty list.
- The legal pages stay English only.
