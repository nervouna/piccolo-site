// Finds lines that hold a single word (or one or two Chinese or Japanese
// characters) and text that overflows, in every language at several widths.
//
// Serve the site locally (see README.md), open http://localhost:8765/ and run
// in the browser console:
//
//   await import("/scripts/check-wrap.js").then(m => m.checkWrap())
//
// It returns one line per problem; an empty list means none.

const PAGES = ["", "zh-hans/", "zh-hant/", "ja/", "fr/", "es/", "pt-br/", "de/"];
const WIDTHS = [360, 375, 390, 414, 600, 768, 900, 1024, 1280, 1440];
const BLOCKS = [
  ".hero h1 span", ".lead span", ".hero-fine", "h2", "h3", ".feature-text p",
  ".layouts p", ".points p", ".button", ".price-card li", ".price-card .fine", ".price-card small",
  ".faq p", ".faq li", ".step span", ".button .note", ".rec-button span",
].join(", ");
const CJK = /[\u3040-\u30ff\u3400-\u9fff\uf900-\ufaff]/g;

async function load(path, width) {
  const frame = document.createElement("iframe");
  frame.style.cssText = `position:fixed;left:0;top:0;width:${width}px;height:900px;visibility:hidden`;
  frame.src = `/${path}?check=${Date.now()}`;
  document.body.append(frame);
  await new Promise((resolve) => (frame.onload = resolve));
  await frame.contentDocument.fonts.ready;
  return frame;
}

// A button's label is its own text, without the note under it.
function textNodes(element) {
  const doc = element.ownerDocument;
  if (element.matches(".button")) return [...element.childNodes].filter((n) => n.nodeType === Node.TEXT_NODE);
  const nodes = [];
  const walker = doc.createTreeWalker(element, NodeFilter.SHOW_TEXT);
  for (let node; (node = walker.nextNode()); ) nodes.push(node);
  return nodes;
}

function lines(element, segmenter) {
  const doc = element.ownerDocument;
  const words = [];
  for (const node of textNodes(element)) {
    for (const segment of segmenter.segment(node.data)) {
      if (!segment.isWordLike) continue;
      const range = doc.createRange();
      range.setStart(node, segment.index);
      range.setEnd(node, segment.index + segment.segment.length);
      const rect = range.getClientRects()[0];
      if (rect) words.push({ top: Math.round(rect.top), text: segment.segment });
    }
  }
  const result = [];
  for (const word of words) {
    const line = result.find((l) => Math.abs(l.top - word.top) < 4);
    line ? line.words.push(word.text) : result.push({ top: word.top, words: [word.text] });
  }
  return result;
}

export async function checkWrap(pages = PAGES, widths = WIDTHS) {
  const problems = [];
  let saved = null;
  try { saved = localStorage.getItem("lang"); localStorage.setItem("lang", "en"); } catch (e) {}
  for (const path of pages) {
    for (const width of widths) {
      const frame = await load(path, width);
      const doc = frame.contentDocument;
      const segmenter = new Intl.Segmenter(doc.documentElement.lang, { granularity: "word" });
      if (doc.documentElement.scrollWidth > width) problems.push(`/${path} ${width}px: page scrolls sideways`);
      // A no-wrap span from the generator must stay inline in running text.
      for (const span of doc.querySelectorAll(".nobr")) {
        const parent = frame.contentWindow.getComputedStyle(span.parentElement).display;
        if (frame.contentWindow.getComputedStyle(span).display !== "inline" || /flex|grid/.test(parent)) {
          problems.push(`/${path} ${width}px: no-wrap span laid out on its own: ${span.parentElement.textContent.trim().slice(0, 50)}`);
        }
      }
      for (const element of doc.querySelectorAll(BLOCKS)) {
        const sample = element.textContent.trim().replace(/\s+/g, " ").slice(0, 50);
        if (element.scrollWidth > element.clientWidth + 1) problems.push(`/${path} ${width}px: overflows: ${sample}`);
        const found = lines(element, segmenter);
        if (found.length < 2) continue;
        for (const line of found) {
          const cjk = (line.words.join("").match(CJK) || []).length;
          const latin = line.words.filter((w) => !w.match(CJK)).length;
          if ((cjk === 0 && latin === 1) || (latin === 0 && cjk <= 2)) {
            problems.push(`/${path} ${width}px: "${line.words.join(" ")}" alone in: ${sample}`);
          }
        }
      }
      frame.remove();
    }
  }
  try { saved === null ? localStorage.removeItem("lang") : localStorage.setItem("lang", saved); } catch (e) {}
  return problems;
}
