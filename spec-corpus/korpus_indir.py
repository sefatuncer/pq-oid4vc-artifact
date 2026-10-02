# -*- coding: utf-8 -*-
"""
PQ-OID4VC Step 1 - corpus download, conversion to text and MANIFEST generation.

Usage (from the spec-corpus/ folder or from anywhere):
    python korpus_indir.py                 # downloads missing files, regenerates the texts and the MANIFEST
    python korpus_indir.py --yeniden ID..  # downloads the given ids again (erisim_utc is updated)
    python korpus_indir.py --sadece-metin  # no download; regenerates metin/ and MANIFEST.csv

Privacy: the requests are anonymous. The HTTP headers carry only a generic User-Agent;
no e-mail address, name or other personal data is sent. A document blocked by an access
restriction (bot protection etc.) is recorded as "erisilemedi"; no attempt is made to bypass the restriction.
"""
import csv
import datetime as dt
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

KOK = Path(__file__).resolve().parent
KAYNAK = KOK / "kaynak"
METIN = KOK / "metin"
TANIM = KOK / "korpus_kaynaklari.json"
KAYIT = KOK / "indirme_kaydi.json"
MANIFEST = KOK / "MANIFEST.csv"
UA = "Mozilla/5.0 (compatible; pq-oid4vc-corpus/1.0; anonymous research fetch)"
MANIFEST_SUTUNLAR = ["id", "baslik", "surum_tarih", "durum", "url", "erisim_utc",
                     "sha256_orijinal", "sha256_metin", "boyut_bayt", "not"]


def sha256_dosya(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blok in iter(lambda: f.read(1 << 16), b""):
            h.update(blok)
    return h.hexdigest()


def indir(url: str, hedef: Path, deneme: int = 3):
    """Anonymous download. Returns (http_kodu, son_url, hata)."""
    son_hata = ""
    for i in range(deneme):
        try:
            istek = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "identity"})
            with urllib.request.urlopen(istek, timeout=180) as yanit:
                veri = yanit.read()
                kod = yanit.status
                son_url = yanit.geturl()
            if kod != 200 or not veri:
                son_hata = f"HTTP {kod}, {len(veri)} bayt"
                continue
            hedef.write_bytes(veri)
            return kod, son_url, ""
        except urllib.error.HTTPError as e:
            son_hata = f"HTTPError {e.code}"
            if e.code in (401, 403, 404, 410, 451):
                break  # access restriction: do not try to bypass it
        except Exception as e:  # network error
            son_hata = f"{type(e).__name__}: {e}"
        time.sleep(2 * (i + 1))
    return None, None, son_hata


# ---------------------------------------------------------------- converters
BLOK = {"p", "div", "section", "article", "header", "footer", "nav", "aside", "main",
        "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "li", "dl", "dt", "dd", "table",
        "thead", "tbody", "tfoot", "tr", "pre", "blockquote", "figure", "figcaption",
        "title", "hr", "br", "details", "summary"}
BOS = {"br", "hr", "img", "meta", "link", "input", "wbr", "col", "area", "base", "source"}


class HtmlMetin(HTMLParser):
    """Converts xml2rfc HTML into readable plain text; pilcrow links and scripts are skipped."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parca = []
        self.yigin = []  # (tag, skip?, pre?)
        self.atla = 0
        self.pre = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        sinif = a.get("class") or ""
        atla = tag in ("script", "style", "noscript", "template") or (tag == "a" and "pilcrow" in sinif)
        if tag in BLOK:
            self.parca.append("\n")
        if tag in ("td", "th"):
            self.parca.append(" | ")
        if tag in BOS:
            return
        pre = tag == "pre"
        self.yigin.append((tag, atla, pre))
        if atla:
            self.atla += 1
        if pre:
            self.pre += 1

    def handle_startendtag(self, tag, attrs):
        if tag in BLOK:
            self.parca.append("\n")

    def handle_endtag(self, tag):
        if tag in BOS:
            return
        # unwind up to the matching opening tag
        for i in range(len(self.yigin) - 1, -1, -1):
            if self.yigin[i][0] == tag:
                for (t, atla, pre) in self.yigin[i:]:
                    if atla:
                        self.atla -= 1
                    if pre:
                        self.pre -= 1
                del self.yigin[i:]
                break
        if tag in BLOK:
            self.parca.append("\n")

    def handle_data(self, data):
        if self.atla > 0:
            return
        if self.pre > 0:
            self.parca.append(data)
        else:
            d = re.sub(r"\s+", " ", data)
            if self.parca and self.parca[-1].endswith("\n"):
                d = d.lstrip(" ")
            if d:
                self.parca.append(d)

    def sonuc(self):
        s = "".join(self.parca)
        s = "\n".join(satir.rstrip() for satir in s.split("\n"))
        s = re.sub(r"\n{3,}", "\n\n", s)
        return s.strip() + "\n"


def html_metin(b: bytes) -> str:
    p = HtmlMetin()
    p.feed(b.decode("utf-8", errors="strict"))
    p.close()
    return p.sonuc()


SAYFA_SONU = re.compile(r"\n[^\n]*\[Page \d+\]\n\f\n?[^\n]*\n")


def ietf_metin(b: bytes) -> str:
    """IETF .txt: the BOM and the pagination (footer + form feed + header) are removed; the content is unchanged."""
    s = b.decode("utf-8-sig").replace("\r\n", "\n")
    s = SAYFA_SONU.sub("\n", s)
    s = s.replace("\f", "\n")
    return s


def md_metin(b: bytes) -> str:
    return b.decode("utf-8-sig").replace("\r\n", "\n")


def pdf_metin(p: Path) -> (str, str):
    exe = shutil.which("pdftotext")
    if exe:
        cikti = subprocess.run([exe, "-enc", "UTF-8", str(p), "-"], capture_output=True)
        if cikti.returncode == 0 and cikti.stdout.strip():
            s = cikti.stdout.decode("utf-8", errors="replace").replace("\r\n", "\n")
            return s, "pdftotext -enc UTF-8"
    from pypdf import PdfReader  # pure Python fallback
    r = PdfReader(str(p))
    s = "\n\f\n".join((pg.extract_text() or "") for pg in r.pages)
    return s, "pypdf"


def metne_cevir(tanim: dict) -> (str, str):
    kaynak = KAYNAK / tanim["dosya"]
    tur = tanim["tur"]
    b = kaynak.read_bytes()
    if tur == "html":
        return html_metin(b), "html.parser (pilcrow ve betikler atlandi)"
    if tur == "txt":
        return ietf_metin(b), "IETF txt (BOM ve sayfa ust/alt bilgileri cikarildi)"
    if tur == "md":
        return md_metin(b), "Markdown kaynagi (degistirilmedi)"
    if tur == "pdf":
        return pdf_metin(kaynak)
    raise ValueError(tur)


def main(argv):
    tanimlar = json.loads(TANIM.read_text(encoding="utf-8"))["belgeler"]
    kayit = json.loads(KAYIT.read_text(encoding="utf-8")) if KAYIT.exists() else {}
    KAYNAK.mkdir(exist_ok=True)
    METIN.mkdir(exist_ok=True)
    sadece_metin = "--sadece-metin" in argv
    yeniden = set()
    if "--yeniden" in argv:
        yeniden = set(argv[argv.index("--yeniden") + 1:])

    satirlar = []
    for t in tanimlar:
        hedef = KAYNAK / t["dosya"]
        k = kayit.get(t["id"], {})
        if not sadece_metin and (not hedef.exists() or t["id"] in yeniden):
            zaman = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            kod, son_url, hata = indir(t["url"], hedef)
            k = {"erisim_utc": zaman, "http": kod, "son_url": son_url, "hata": hata}
            kayit[t["id"]] = k
            print(f"[indir] {t['id']:<10} {kod} {hata}")
            time.sleep(0.5)
        erisildi = hedef.exists()
        yontem = ""
        if erisildi:
            s, yontem = metne_cevir(t)
            (METIN / f"{t['id']}.txt").write_text(s, encoding="utf-8", newline="\n")
        notlar = [x for x in [t.get("not", "")] if x]
        if erisildi:
            notlar.append(f"metin: {yontem}")
        else:
            notlar.append(f"ERISILEMEDI ({k.get('hata', 'indirilmedi')})")
        satirlar.append({
            "id": t["id"], "baslik": t["baslik"], "surum_tarih": t["surum_tarih"],
            "durum": t["durum"], "url": t["url"], "erisim_utc": k.get("erisim_utc", ""),
            "sha256_orijinal": sha256_dosya(hedef) if erisildi else "",
            "sha256_metin": sha256_dosya(METIN / f"{t['id']}.txt") if erisildi else "",
            "boyut_bayt": hedef.stat().st_size if erisildi else "",
            "not": " | ".join(notlar),
        })

    KAYIT.write_text(json.dumps(kayit, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    with open(MANIFEST, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=MANIFEST_SUTUNLAR)
        w.writeheader()
        w.writerows(satirlar)
    print(f"MANIFEST: {len(satirlar)} satir -> {MANIFEST}")


if __name__ == "__main__":
    main(sys.argv[1:])
