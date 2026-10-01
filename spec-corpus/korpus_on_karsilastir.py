# -*- coding: utf-8 -*-
"""
referans/korpus_on/ (onceden indirilmis kopyalar) ile spec-corpus/ taze indirmelerini karsilastirir.
Cikti: korpus_on_karsilastirma.csv ve korpus_on_karsilastirma.txt (01-korpus altinda).

Karsilastirma adimlari:
 (1) korpus_on dosyasi bir .txt orijinal ise: bayt duzeyinde SHA-256 esitligi (taze orijinal ile).
 (2) korpus_on dosyasi bir PDF'ten cikarilmis metinse (orijinal PDF korpus_on'da yok):
     taze PDF'ten ayni metni YENIDEN URETMEYI dener (pdftotext -layout [Latin-1 varsayilani],
     pypdf sayfa metinleri "\n" ile birlestirilmis). Bayt/metin esitligi, taze PDF'in ayni belge
     oldugunun kanitidir.
 (3) Her durumda bosluk-normallestirilmis sozcuk benzerligi (difflib) raporlanir.
"""
import csv
import difflib
import hashlib
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

KOK = Path(__file__).resolve().parent
ON = KOK.parent / "referans" / "korpus_on"
ESLEME = {  # korpus_on dosyasi -> (korpus id, taze orijinal dosya)
    "draft-ietf-jose-pq-composite-sigs-04.txt": ("JOSECOMP", "draft-ietf-jose-pq-composite-sigs-04.txt"),
    "draft-ietf-oauth-rfc8725bis-10.txt": ("JWTBCP", "draft-ietf-oauth-rfc8725bis-10.txt"),
    "rfc9955.txt": ("RFC9955", "rfc9955.txt"),
    "eccg_acm_v2.txt": ("ACM2", "ECCG_Agreed_Cryptographic_Mechanisms_version_2.pdf"),
    "pqc_roadmap.txt": ("PQCRM", "EU_PQC_Roadmap_Part1_v1.1.pdf"),
    "oid4vp_report.txt": ("HAUCK25", "Report-Deliverable-A_1_B_.pdf"),
}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def coz(b: bytes):
    try:
        return b.decode("utf-8-sig"), "utf-8"
    except UnicodeDecodeError:
        return b.decode("cp1252", errors="replace"), "UTF-8 degil (Latin-1/cp1252)"


def norm(s: str) -> str:
    s = s.replace("\f", " ")
    s = re.sub(r"\n[^\n]*\[Page \d+\]\n", "\n", s)
    return re.sub(r"\s+", " ", s).strip()


def pdf_yeniden_uret(pdf: Path, on_b: bytes):
    """korpus_on metnini taze PDF'ten yeniden uretmeyi dener; basarili yontemi dondurur."""
    exe = shutil.which("pdftotext")
    if exe:
        with tempfile.TemporaryDirectory() as d:
            cikti = Path(d) / "o.txt"
            subprocess.run([exe, "-layout", str(pdf), str(cikti)], capture_output=True)
            if cikti.exists() and cikti.read_bytes() == on_b:
                return "pdftotext -layout (Latin-1 varsayilani): BAYT-OZDES"
    try:
        from pypdf import PdfReader
        s = "\n".join((p.extract_text() or "") for p in PdfReader(str(pdf)).pages)
        if s == on_b.decode("utf-8", errors="replace").replace("\r\n", "\n"):
            return "pypdf sayfa metinleri '\\n' ile (CRLF normallestirilerek): METIN-OZDES"
    except Exception as e:  # pypdf yoksa
        return f"pypdf denenemedi: {e}"
    return "yeniden uretilemedi"


def main():
    satirlar = []
    for ad, (kid, orj) in ESLEME.items():
        on_b = (ON / ad).read_bytes()
        orj_p = KOK / "kaynak" / orj
        orj_b = orj_p.read_bytes()
        met_b = (KOK / "metin" / f"{kid}.txt").read_bytes()
        on_s, kod = coz(on_b)
        if orj.endswith(".pdf"):
            bayt = "uygulanmaz (korpus_on'da PDF yok)"
            yeniden = pdf_yeniden_uret(orj_p, on_b)
        else:
            bayt = "ESIT" if sha(on_b) == sha(orj_b) else "FARKLI"
            yeniden = "gerekmez"
        a, b = norm(on_s).split(" "), norm(met_b.decode("utf-8")).split(" ")
        oran = 1.0 if a == b else difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()
        satirlar.append({
            "korpus_on_dosya": ad, "korpus_id": kid,
            "sha256_korpus_on": sha(on_b), "sha256_taze_orijinal": sha(orj_b),
            "sha256_taze_metin": sha(met_b),
            "bayt_karsilastirma": bayt, "pdf_yeniden_uretim": yeniden,
            "sozcuk_benzerlik_taze_metin": f"{oran:.4f}", "korpus_on_kodlama": kod,
        })
    alanlar = list(satirlar[0].keys())
    with open(KOK / "korpus_on_karsilastirma.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=alanlar)
        w.writeheader()
        w.writerows(satirlar)
    with open(KOK / "korpus_on_karsilastirma.txt", "w", encoding="utf-8", newline="\n") as f:
        f.write("referans/korpus_on <-> 01-korpus taze indirme karsilastirmasi\n")
        f.write("(sozcuk benzerligi, farkli metin cikarma yontemleri ve sayfalama yuzunden 1'in altinda olabilir)\n")
        for r in satirlar:
            f.write(f"- {r['korpus_on_dosya']} -> {r['korpus_id']}: bayt={r['bayt_karsilastirma']}; "
                    f"pdf_yeniden_uretim={r['pdf_yeniden_uretim']}; "
                    f"sozcuk_benzerlik={r['sozcuk_benzerlik_taze_metin']}; kodlama={r['korpus_on_kodlama']}\n")
    print(open(KOK / "korpus_on_karsilastirma.txt", encoding="utf-8").read())


if __name__ == "__main__":
    main()
