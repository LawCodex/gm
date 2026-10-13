#!/usr/bin/env python3
"""The Gambia: the Constitution of 1997 (2002 revision) and the Acts published as PDFs by the Ministry of Justice
(moj.gov.gm; list of PDF files from the WordPress media API). Drafts, reports and other documents are skipped; PDFs
without a usable text layer are skipped and reported.
Usage: python3 gm_fetch.py [--no-download]"""
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gm_text as T  # noqa

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(os.path.dirname(REPO), "_raw", "gm")
RETRIEVED = os.environ.get("LC_RETRIEVED", "2026-10-13")
NODL = "--no-download" in sys.argv
API = "https://moj.gov.gm/wp-json/wp/v2/media?mime_type=application/pdf&per_page=100"
DELAY = 3


def constitution_lines(pdf):
    """The Constitution PDF has marginal notes (section titles) and section numbers in a left column: read the
    layout text, split the margin from the body and rebuild 'Section N — Title' lines."""
    import subprocess
    txt = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True).stdout.decode("utf-8", "replace")
    pages = txt.split("\f")
    # skip the cover and the table of contents: start at the preamble
    start = next(i for i, p in enumerate(pages) if "In the name of God, the Almighty" in p)
    pages[start] = pages[start][pages[start].index("In the name of God, the Almighty"):]
    out = []          # list of [kind, text]; kind = "sec" | "line"
    cur = None        # current section entry (to extend its marginal title)
    for p in pages[start:]:
        for ln in p.split("\n"):
            if not ln.strip() or re.match(r"^\s*\d+\s*$", ln):
                continue
            m = re.match(r"^(\S.{0,34}?)(\s{2,}(.*))?$", ln) if not ln.startswith(" ") else None
            if m and re.match(r"^(CHAPTER|PART|SCHEDULE)\b", ln.strip()):
                m = None
            if m:
                left, right = m.group(1).strip(), (m.group(3) or "").strip()
                left = re.sub(r"\s*\b(No\.\s*)?\d+\s+of\s+\d{4}\b\s*", " ", left).strip()  # amendment references
                if not left:
                    if right:
                        out.append(["line", right])
                    continue
                nm = re.match(r"^(.*?)\s*(\d{1,3}[A-Z]?)\.?\s*(\(\d+\))?$", left)
                if nm and not re.match(r"^(No\. )?\d+ of \d{4}$", left) and not nm.group(2).startswith("0") and (not nm.group(1) or re.search(r"[A-Za-z]", nm.group(1))):
                    cur = ["sec", nm.group(2), [nm.group(1)] if nm.group(1) else []]
                    out.append(cur)
                    if nm.group(3):
                        right = (nm.group(3) + " " + right).strip()
                elif cur is not None and not re.match(r"^(No\. )?\d+ of \d{4}$", left):
                    cur[2].append(left)
                if right:
                    out.append(["line", right])
            else:
                out.append(["line", ln.strip()])
    lines = []
    for e in out:
        if e[0] == "sec":
            title = re.sub(r"\s+", " ", " ".join(e[2])).strip()
            title = title[:1].upper() + title[1:] if title else ""  # marginal note as printed
            lines += ["", "Section %s — %s" % (e[1], title) if title else "Section %s —  " % e[1], ""]
        else:
            lines.append(T.norm(e[1]))
    return lines


def main():
    os.makedirs(os.path.join(RAW, "pdf"), exist_ok=True)
    dest = os.path.join(RAW, "media.json")
    if not NODL:
        T.fetch(API, dest, delay=DELAY)
    media = json.load(open(dest))
    rep = {"ok": [], "skipped": []}
    seen = {}
    for m in sorted(media, key=lambda m: m["source_url"]):
        url = m["source_url"]
        name = url.rsplit("/", 1)[-1]
        if not re.search(r"(\bAct\b|[-_]Act[-_]|Act-\d|Constitution-1997)", name) or re.search(r"Draft|Explanatory|Report|White", name):
            continue
        pdf = os.path.join(RAW, "pdf", name)
        if not NODL:
            T.fetch(url, pdf, delay=DELAY, check_pdf=True, timeout=300)
        if not os.path.exists(pdf) or not T.pdf_ok(pdf):
            rep["skipped"].append(name + " (download failed)")
            continue
        h = hashlib.md5(open(pdf, "rb").read()).hexdigest()
        if h in seen:
            rep["skipped"].append(name + " (duplicate of %s)" % seen[h])
            continue
        seen[h] = name
        pages, _ = T.pdf_text(pdf, "eng", tmpdir=RAW, ocr=False)
        txt = "\n".join(pages)
        if len(re.sub(r"\s", "", txt)) / max(1, len(pages)) < 400 or T.text_quality(txt) < 0.8:
            rep["skipped"].append(name + " (scanned, no usable text layer)")
            continue
        lines = T.clean_pages(pages)
        if "Constitution-1997" in name:
            lines = constitution_lines(pdf)
            title, rel, typ = "Constitution of the Republic of The Gambia, 1997 (2002 reprint)", "constitution/constitution-1997.md", "constitution"
        else:
            t = re.sub(r"\.pdf$", "", name)
            t = re.sub(r"^(Final-)?Assent-Copy-|-Passed-.*$|_Now\d*$|-1(-1)?$", "", t).replace("_", " ").replace("-", " ")
            title = re.sub(r"\bSPO\b", "Special Prosecutor's Office", t).strip()
            ym = re.findall(r"(19|20)\d\d", title)
            year = re.findall(r"(?:19|20)\d\d", title)
            rel, typ = "acts/%s/%s.md" % (year[-1] if year else "undated", T.slug(title, 90)), "act"
        if rel in rep["ok"]:
            rel = rel[:-3] + "-" + h[:6] + ".md"
        body = T.structure(lines, "en")
        meta = {"title": title, "type": typ, "jurisdiction": "gm", "language": "en",
                "date": "1997-01-16" if typ == "constitution" else None,
                "status": "in_force" if typ == "constitution" else "unknown", "source": url,
                "record": "https://moj.gov.gm/", "retrieved": RETRIEVED}
        T.write_md(os.path.join(REPO, rel), meta, title, body)
        rep["ok"].append(rel)
        print("OK", rel, sum(1 for x in body if x.startswith("#")))
    json.dump(rep, open(os.path.join(RAW, "report.json"), "w"), indent=1)
    print({k: len(v) for k, v in rep.items()})
    for x in rep["skipped"]:
        print("SKIPPED", x)


if __name__ == "__main__":
    main()
