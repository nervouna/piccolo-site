# piccolo-site

The product site of Piccolo, served at https://piccolo.damao.io by GitHub Pages.

Piccolo is a macOS menu bar app that moves, resizes and arranges windows with global keyboard shortcuts. Its source repository is private; this repository holds only the public site.

The site is plain static files at the repository root: no build step, no JavaScript and no requests to other hosts.

| Path | What it is |
|---|---|
| `index.html` | Product page: animated demos drawn in CSS, layouts, details, pricing, FAQ |
| `terms.html`, `privacy.html`, `refunds.html` | Terms of Service, Privacy Policy, Refund Policy |
| `styles.css` | The only stylesheet, light and dark through `prefers-color-scheme` |
| `images/` | Banner, icon (also the favicon) and the two Settings screenshots |
| `appcast.xml` | The Sparkle appcast that Piccolo fetches once a day |
| `downloads/` | Release zips, `downloads/Piccolo-<version>.zip` |
| `CNAME`, `.nojekyll` | GitHub Pages: the custom domain, and no Jekyll processing |

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
4. Replace the two disabled Download buttons of `index.html`, "Download free trial" in the hero and "Download" in the pricing section, with links to the zip, and the disabled Purchase button with `id="buy"` in the pricing section with the checkout link.
5. Commit and push to `main`; GitHub Pages publishes the site.
