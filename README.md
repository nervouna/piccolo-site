# piccolo-site

The product site of Piccolo, served at https://piccolo.damao.io by GitHub Pages.

Piccolo is a macOS menu bar app that moves, resizes and arranges windows with global keyboard shortcuts. Its source repository is private; this repository holds only the public site.

GitHub Pages serves the repository root as it is, with no requests to other hosts. The product page comes in Piccolo's eight languages and is generated locally: edit `src/`, run `scripts/build.py`, and commit both the sources and the generated pages.

| Path | What it is |
|---|---|
| `src/index.html` | Template of the product page: animated demos drawn in CSS, layouts, details, pricing, FAQ |
| `src/strings/<language>.json` | Its texts, one file per language, all with the same keys |
| `scripts/build.py` | Writes the product page in every language; `--check` fails if a committed page is out of date |
| `scripts/check-wrap.js` | Browser check for lines of a single word and for overflowing text, in every language |
| `index.html`, `<language>/index.html` | Generated: English at the root, the others in `zh-hans/`, `zh-hant/`, `ja/`, `fr/`, `es/`, `pt-br/`, `de/` |
| `terms.html`, `privacy.html`, `refunds.html` | Terms of Service, Privacy Policy, Refund Policy |
| `styles.css` | The only stylesheet, light and dark through `prefers-color-scheme` |
| `images/` | Banner, icon (also the favicon) and the two Settings screenshots |
| `appcast.xml` | The Sparkle appcast that Piccolo fetches once a day |
| `downloads/` | Release zips, `downloads/Piccolo-<version>.zip` |
| `CNAME`, `.nojekyll` | GitHub Pages: the custom domain, and no Jekyll processing |

## Languages

- The English page sends a first visit on to the visitor's language, from the browser's language list. A language picked in the footer is remembered in `localStorage` and wins from then on, English included. Pages link each other with `hreflang`.
- The action names in the demos are the app's own translations, from its String Catalogs, so the page and the app use the same words. The terms follow the glossary in the app's `docs/localization.md`.
- The legal pages are English only; the localized pages say so where they link to them.
- A new text goes into every `src/strings/*.json`: the build stops on a missing or extra key.
- Chinese and Japanese texts have no spaces between Chinese or Japanese and Latin text; the gap comes from `text-autospace` in `styles.css`.
- No line may hold a single word, or one or two Chinese or Japanese characters. The build keeps the end of every text together (a no-break space before the last word, or a no-wrap span around the last three characters). After changing a text, serve the site and run `scripts/check-wrap.js` in the browser console, as its header says: it checks every language at widths from 360 to 1440 px and must return an empty list.

## Preview locally

From the repository root:

```sh
python3 -m http.server 8765
```

Then open http://localhost:8765. Stop the server with Control-C.

## Releasing a version

1. Copy the signed, notarized archive to `downloads/Piccolo-<version>.zip`.
2. Add an `<item>` for it inside the `<channel>` of `appcast.xml`, for example:

   ```xml
   <item>
     <title>Version <version></title>
     <pubDate><RFC 822 date></pubDate>
     <sparkle:version><build number></sparkle:version>
     <sparkle:shortVersionString><version></sparkle:shortVersionString>
     <sparkle:minimumSystemVersion>14.0</sparkle:minimumSystemVersion>
     <enclosure url="https://piccolo.damao.io/downloads/Piccolo-<version>.zip"
                length="<size in bytes>"
                type="application/octet-stream"
                sparkle:edSignature="<EdDSA signature>"/>
   </item>
   ```

3. Check that the file is still valid XML: `xmllint --noout appcast.xml`.
4. In `src/index.html`, replace the two disabled Download buttons, "Download free trial" in the hero and "Download" in the pricing section, with links to the zip, and the disabled Purchase button with `id="buy"` in the pricing section with the checkout link. Then run `scripts/build.py`.
5. Commit and push to `main`; GitHub Pages publishes the site.
