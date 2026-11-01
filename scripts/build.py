#!/usr/bin/env python3
"""Generate the product page in every language from src/.

src/index.html is the template; src/strings/<language>.json holds its texts.
English goes to index.html, every other language to <dir>/index.html. The
output is committed, so GitHub Pages serves plain files.

    scripts/build.py           write the pages
    scripts/build.py --check   exit 1 if a committed page is out of date
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://piccolo.damao.io/"

# (strings file, output directory, hreflang, name in its own language)
LANGUAGES = [
    ("en", "", "en", "English"),
    ("zh-Hans", "zh-hans", "zh-Hans", "简体中文"),
    ("zh-Hant", "zh-hant", "zh-Hant", "繁體中文"),
    ("ja", "ja", "ja", "日本語"),
    ("fr", "fr", "fr", "Français"),
    ("es", "es", "es", "Español"),
    ("pt-BR", "pt-br", "pt-BR", "Português (Brasil)"),
    ("de", "de", "de", "Deutsch"),
]

PLACEHOLDER = re.compile(r"\{\{(\w+)\}\}")

# Strings that end up in attributes, where markup and line breaks mean nothing.
ATTRIBUTE_KEYS = {
    "title", "description", "nav_label", "demo_label", "f1_label", "f2_label",
    "f3_label", "craft_img_alt", "footer_label", "languages_label", "phrase_gap",
}

# Short labels that sit in buttons, menus and key rows, where an extra span
# would become a layout item of its own. They never wrap anyway.
LABEL_KEYS = {
    "nav_features", "nav_pricing", "nav_faq", "download_trial", "coming_soon",
    "purchase", "available_soon", "download", "rec_typing", "lay_display_arrows",
    "terms", "privacy", "refunds",
}

CJK = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uf900-\ufaff]")
# A visible unit of text: an entity, a placeholder, or one character outside a tag.
UNIT = re.compile(r"<[^>]*>|&\w+;|\{\{\w+\}\}|.", re.S)


def keep_end_together(text):
    """Keeps the end of a text off a line of its own.

    Latin text: the last space becomes a no-break space, so the last two words
    share a line. Chinese and Japanese text: the last three characters, with
    any punctuation after them, go into a span that does not wrap.
    """
    units = [(m.start(), m.group()) for m in UNIT.finditer(text) if not m.group().startswith("<")]
    if CJK.search(text):
        start, cjk, count = None, 0, 0
        for position, unit in reversed(units):
            start, count = position, count + 1
            cjk += bool(CJK.match(unit))
            if cjk == 3 or count == 12:
                break
        tail = text[start:] if start is not None else ""
        # A tail that ends a link takes the whole link along.
        if "</a>" in tail and "<a" not in tail:
            start = text.rfind("<a", 0, start)
            tail = text[start:]
        if cjk == 3 and start >= 0 and tail.count("<a") == tail.count("</a>"):
            return text[:start] + '<span class="nobr">' + tail + "</span>"
        # The text ends in Latin words or markup: keep the last two words together.
        return keep_last_two_words(text, units)
    return keep_last_two_words(text, units)


def keep_last_two_words(text, units):
    spaces = [position for position, unit in units if unit == " "]
    if not spaces:
        return text
    last = spaces[-1]
    return text[:last] + "\u00a0" + text[last + 1:]


def redirect_script():
    """Sends a first visit to the root page on to the visitor's language.

    A language picked in the footer is remembered and always wins, so a
    visitor who chose English is never sent away again.
    """
    pages = {code: directory + "/" for code, directory, _, _ in LANGUAGES if directory}
    return f"""  <script>
    (function () {{
      var pages = {json.dumps(pages)};
      var target = null;
      try {{ target = localStorage.getItem("lang"); }} catch (e) {{}}
      if (!target) {{
        var wanted = navigator.languages || [navigator.language || ""];
        for (var i = 0; i < wanted.length && !target; i++) {{
          var tag = String(wanted[i]).toLowerCase();
          var primary = tag.split("-")[0];
          if (primary === "en") target = "en";
          else if (primary === "zh") target = /hant|-tw|-hk|-mo/.test(tag) ? "zh-Hant" : "zh-Hans";
          else if (primary === "pt") target = "pt-BR";
          else if (pages[primary]) target = primary;
        }}
      }}
      if (target && pages[target]) location.replace(pages[target] + location.hash);
    }})();
  </script>
"""


REMEMBER_SCRIPT = """  <script>
    document.querySelectorAll("[data-lang]").forEach(function (link) {
      link.addEventListener("click", function () {
        try { localStorage.setItem("lang", link.dataset.lang); } catch (e) {}
      });
    });
  </script>
"""


def alternates():
    lines = [
        f'  <link rel="alternate" hreflang="{hreflang}" href="{SITE}{directory + "/" if directory else ""}">'
        for _, directory, hreflang, _ in LANGUAGES
    ]
    lines.append(f'  <link rel="alternate" hreflang="x-default" href="{SITE}">')
    return "\n".join(lines) + "\n"


def language_nav(current, root, label):
    links = []
    for code, directory, hreflang, name in LANGUAGES:
        href = root + (directory + "/" if directory else "")
        current_attr = ' aria-current="page"' if code == current else ""
        links.append(
            f'        <a href="{href or "./"}" hreflang="{hreflang}" lang="{hreflang}"'
            f' data-lang="{code}"{current_attr}>{name}</a>'
        )
    return f'      <nav class="langs" aria-label="{label}">\n' + "\n".join(links) + "\n      </nav>\n"


def fill(text, values, where):
    def replace(match):
        key = match.group(1)
        if key not in values:
            sys.exit(f"{where}: no value for {{{{{key}}}}}")
        return values[key]

    # Twice, because a few strings hold {{root}} themselves.
    return PLACEHOLDER.sub(replace, PLACEHOLDER.sub(replace, text))


def build():
    template = (ROOT / "src/index.html").read_text()
    english = json.loads((ROOT / "src/strings/en.json").read_text())
    pages = {}
    for code, directory, hreflang, _ in LANGUAGES:
        strings = json.loads((ROOT / f"src/strings/{code}.json").read_text())
        missing = english.keys() - strings.keys()
        extra = strings.keys() - english.keys()
        if missing or extra:
            sys.exit(f"src/strings/{code}.json: missing {sorted(missing)}, extra {sorted(extra)}")
        root = "../" if directory else ""
        values = {key: value if key in ATTRIBUTE_KEYS | LABEL_KEYS or key.startswith("act_")
                  else keep_end_together(value)
                  for key, value in strings.items()}
        values.update(
            html_lang=hreflang,
            shortcuts_image="settings-shortcuts.webp" if code == "en" else f"settings-shortcuts-{code}.webp",
            root=root,
            redirect=redirect_script() if not directory else "",
            alternates=alternates(),
            languages=language_nav(code, root, strings["languages_label"]),
            remember=REMEMBER_SCRIPT,
        )
        page = fill(template, values, f"src/strings/{code}.json")
        page = page.replace(
            "<!doctype html>\n",
            "<!doctype html>\n<!-- Generated from src/ by scripts/build.py. Edit those, not this file. -->\n",
            1,
        )
        pages[Path(directory) / "index.html"] = page
    return pages


def main():
    pages = build()
    if "--check" in sys.argv[1:]:
        stale = [str(path) for path, page in pages.items()
                 if not (ROOT / path).exists() or (ROOT / path).read_text() != page]
        if stale:
            sys.exit("Out of date, run scripts/build.py: " + ", ".join(stale))
        return
    for path, page in pages.items():
        (ROOT / path).parent.mkdir(parents=True, exist_ok=True)
        (ROOT / path).write_text(page)
        print(path)


if __name__ == "__main__":
    main()
