#!/usr/bin/env python3
"""Adım 9 görev 4a — sürüm etiketini commit'e çözer (anonim `git ls-remote`; kod indirmez).
Her git çağrısı: GIT_TERMINAL_PROMPT=0, GCM_INTERACTIVE=never, -c credential.helper= (IS-PLANI §3.3, D-E12).
Girdi: kayit/hedef_listesi.csv. Çıktı: kayit/surum_commit.csv ve kayit/lsremote/<id>.txt (ham ref listesi)."""
import csv, os, pathlib, re, subprocess, concurrent.futures as cf
KOK = pathlib.Path(__file__).resolve().parents[1]
GIRDI = KOK / "kayit" / "hedef_listesi.csv"
CIKTI = KOK / "kayit" / "surum_commit.csv"
HAM = KOK / "kayit" / "lsremote"; HAM.mkdir(parents=True, exist_ok=True)
ORTAM = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never", GIT_ASKPASS="", SSH_ASKPASS="")
GIT = ["git", "-c", "credential.helper=", "-c", "core.askPass="]

def ls_remote(url):
    u = url.rstrip("/")
    if not u.endswith(".git"):
        u += ".git"
    r = subprocess.run(GIT + ["ls-remote", "--tags", u], capture_output=True, text=True, timeout=180, env=ORTAM,
                       stdin=subprocess.DEVNULL)
    return r.returncode, r.stdout, r.stderr

def etiket_sec(refs, surum, paket):
    v = surum.lstrip("v")
    cands = []
    for t in refs:
        if (t == v or t == "v" + v or re.search(r"(^|[-_/@])v?" + re.escape(v) + r"$", t)):
            cands.append(t)
    if not cands:
        return "", []
    def puan(t):
        p = 0
        if t in (v, "v" + v): p -= 10
        if paket:
            son = paket.split("/")[-1].split(":")[-1].lower()
            if son and son in t.lower(): p -= 5
        return (p, len(t), t)
    cands.sort(key=puan)
    return cands[0], cands

def isle(r):
    sonuc = dict(id=r["id"], depo_url=r["depo_url"], son_surum=r["son_surum"], etiket="", etiket_commit="",
                 son_commit_sha=r["son_commit_sha"], etiket_eq_head="", aday_etiketler="", not_="")
    if not r["son_surum"]:
        sonuc["not_"] = "son_surum yok -> son_commit_sha kullanılır"
        return sonuc
    try:
        kod, out, err = ls_remote(r["depo_url"])
    except subprocess.TimeoutExpired:
        sonuc["not_"] = "ls-remote zaman aşımı"; return sonuc
    (HAM / f"{r['id']}.txt").write_text(out, encoding="utf-8")
    if kod != 0:
        sonuc["not_"] = "ls-remote hata: " + err.strip()[:200]; return sonuc
    refs = {}
    for satir in out.splitlines():
        sha, ref = satir.split("\t")
        ad = ref[len("refs/tags/"):]
        if ad.endswith("^{}"):
            refs[ad[:-3]] = (refs.get(ad[:-3], (None, None))[0], sha)   # soyulmuş (peeled) commit
        else:
            refs[ad] = (sha, refs.get(ad, (None, None))[1])
    et, cands = etiket_sec(list(refs), r["son_surum"], r["paket_adi"])
    sonuc["aday_etiketler"] = ";".join(cands[:6])
    if et:
        sha, peeled = refs[et]
        sonuc["etiket"] = et
        sonuc["etiket_commit"] = peeled or sha
        sonuc["etiket_eq_head"] = "evet" if (peeled or sha) == r["son_commit_sha"] else "hayir"
    else:
        sonuc["not_"] = "sürüm etiketi bulunamadı"
    return sonuc

satirlar = list(csv.DictReader(open(GIRDI, encoding="utf-8")))
with cf.ThreadPoolExecutor(8) as ex:
    sonuclar = list(ex.map(isle, satirlar))
with open(CIKTI, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(sonuclar[0].keys()))
    w.writeheader(); w.writerows(sonuclar)
for s in sonuclar:
    print(s["id"], s["son_surum"], "|", s["etiket"], s["etiket_commit"][:12], "| head_eq:", s["etiket_eq_head"], "|", s["aday_etiketler"][:80], s["not_"])
