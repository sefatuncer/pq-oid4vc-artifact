#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PQ-OID4VC — C3 örneklem çerçevesi toplayıcısı (Adım 9a)
=========================================================

Bu betik C3 ampirik çalışmasının ÖRNEKLEM ÇERÇEVESİNİ tekrar üretilebilir biçimde kurar:

  1. Tanımlama : jwt.io kütüphane verisi + GitHub konu aramaları + paket kaydı aramaları
                 + kuruluş listeleri + plan/görev tanımında adı geçenler  -> ham isabetler
  2. Tarama    : gürültü tabanı + elle verilmiş tarama kararları (tarama_kararlari.csv)
                 -> aday listesi (TARAMA.csv tüm isabetleri kararlarıyla birlikte yazar)
  3. Meta veri : deps.dev, ecosyste.ms, paket kayıtlarının genel API'leri, git (ls-remote,
                 sığ/blob'suz klon) -> yıldız, son commit, son sürüm, lisans, indirme ...
  4. Ölçütler  : KRITERLER-TASLAK.md'deki K1–K8 + eşik seçenekleri E1–E4 -> SECIM.csv,
                 ESIK-DUYARLILIK.csv
  5. Çıktı     : CERCEVE.csv (+ destek_kanitlari.csv'deki elle doğrulanmış destek hücreleri)

Yalnız ÇERÇEVE ve META VERİ toplar. Kütüphane DAVRANIŞI ölçülmez; adaptör yazılmaz; test
vektörü koşulmaz (ön kayıt donmadan yapılmamalı).

Gizlilik: Bütün istekler anonimdir. User-Agent genel bir metindir; hiçbir istekte e-posta,
kişisel veri, token ya da hesap bilgisi yoktur. GitHub API'si yalnız son çare olarak ve
bekleme/önbellekle kullanılır (anonim sınır saatte 60).

Kullanım:
  python topla.py                    # önbellekten koş; önbellekte olmayanları ağdan al
  python topla.py --cevrimdisi       # yalnız önbellek (ağ yok); eksikler boş kalır
  python topla.py --tazele           # önbelleği yok say (anlık görüntü değişir!)
  python topla.py --desen-tara       # (isteğe bağlı) sığ klonlarda kanıt ipucu taraması
  python topla.py --klon-dizini D    # git klonları için dizin (vars.: %TEMP%/pq-oid4vc-envanter-klon)

Çerçeve tarihi (REF_TARIH) sabittir: 2026-09-23. "Son 24 ay" bu tarihe göre hesaplanır.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# ---------------------------------------------------------------------------
# Sabitler
# ---------------------------------------------------------------------------
KOK = Path(__file__).resolve().parent
ONBELLEK = KOK / "onbellek"
UA = "pq-oid4vc-envanter/0.1 (anonim arastirma envanteri)"
REF_TARIH = dt.date(2026, 9, 23)
ETKINLIK_SINIRI = dt.date(2024, 9, 23)  # REF_TARIH - 24 ay
JWTIO_COMMIT = "60b70f7d8d2020e4c0165c4dfd442dd3329019a0"  # jsonwebtoken.github.io@master, 23.09.2026
JWTIO_VERI_URL = (f"https://raw.githubusercontent.com/jsonwebtoken/jsonwebtoken.github.io/"
                  f"{JWTIO_COMMIT}/src/data/libraries-next.json")

ARGS = None  # argparse sonucu (global; basitlik için)


def log(*a):
    print(*a, file=sys.stderr, flush=True)


# ---------------------------------------------------------------------------
# HTTP + önbellek
# ---------------------------------------------------------------------------
class AgYok(Exception):
    pass


def _onbellek_yolu(url: str, kategori: str) -> Path:
    h = hashlib.sha1(url.encode("utf-8")).hexdigest()[:20]
    return ONBELLEK / "http" / kategori / f"{h}.json"


def http_get(url: str, kategori: str = "genel", ham: bool = False, bekle: float = 0.25,
             basliklar: dict | None = None, kirp=None):
    """GET + disk önbelleği. (durum, gövde) döndürür. gövde: JSON (ham=False) ya da metin.
    kirp: gövdeyi önbelleğe yazmadan önce küçülten/temizleyen fonksiyon (ör. kişisel veri alanlarını atmak için)."""
    yol = _onbellek_yolu(url, kategori)
    if yol.exists() and not ARGS.tazele:
        rec = json.loads(yol.read_text("utf-8"))
        return rec["durum"], rec["govde"]
    if ARGS.cevrimdisi:
        raise AgYok(url)
    h = {"User-Agent": UA, "Accept": "application/json" if not ham else "*/*"}
    if basliklar:
        h.update(basliklar)
    req = urllib.request.Request(url, headers=h)
    durum, govde = None, None
    for deneme in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                durum = r.status
                veri = r.read().decode("utf-8", errors="replace")
                govde = veri if ham else json.loads(veri) if veri.strip() else None
            break
        except urllib.error.HTTPError as e:
            durum = e.code
            try:
                veri = e.read().decode("utf-8", errors="replace")
                govde = veri if ham else json.loads(veri)
            except Exception:
                govde = None
            if e.code in (429, 502, 503, 504) and deneme < 2:
                time.sleep(5 * (deneme + 1))
                continue
            break
        except Exception as e:  # ağ hatası
            durum, govde = -1, str(e)
            if deneme < 2:
                time.sleep(3 * (deneme + 1))
                continue
    if kirp is not None and govde is not None and durum == 200:
        try:
            govde = kirp(govde)
        except Exception:
            pass
    yol.parent.mkdir(parents=True, exist_ok=True)
    yol.write_text(json.dumps({"url": url, "alindi_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                               "durum": durum, "govde": govde}, ensure_ascii=False), "utf-8")
    time.sleep(bekle)
    return durum, govde


def gh_api(yol: str):
    """GitHub REST API (anonim) — yalnız son çare. Kalan hak 3'ün altına düşerse beklemeden vazgeçer."""
    url = "https://api.github.com/" + yol.lstrip("/")
    onb = _onbellek_yolu(url, "github")
    if onb.exists() and not ARGS.tazele:
        rec = json.loads(onb.read_text("utf-8"))
        return rec["durum"], rec["govde"]
    if ARGS.cevrimdisi or getattr(gh_api, "tukendi", False):
        return None, None
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            kalan = int(r.headers.get("X-RateLimit-Remaining", "0"))
            durum, govde = r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        kalan = int(e.headers.get("X-RateLimit-Remaining", "0") or 0)
        durum, govde = e.code, None
    except Exception:
        return None, None
    if kalan < 3:
        gh_api.tukendi = True
        log("  ! GitHub anonim API hakkı bitmek üzere; bu koşumda başka GitHub API çağrısı yapılmayacak.")
    onb.parent.mkdir(parents=True, exist_ok=True)
    onb.write_text(json.dumps({"url": url, "alindi_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                               "durum": durum, "govde": govde}, ensure_ascii=False), "utf-8")
    time.sleep(1.0)
    return durum, govde


# ---------------------------------------------------------------------------
# Yardımcılar
# ---------------------------------------------------------------------------
def depo_normalize(url_ya_da_yol: str) -> str:
    """'https://github.com/Owner/Repo.git' -> 'github.com/owner/repo' (küçük harf)."""
    if not url_ya_da_yol:
        return ""
    s = url_ya_da_yol.strip()
    s = re.sub(r"^git\+", "", s)
    s = re.sub(r"^(https?://|git://|ssh://git@|git@)", "", s)
    s = s.replace("github.com:", "github.com/")
    s = re.sub(r"\.git$", "", s)
    m = re.match(r"(github\.com|bitbucket\.org|gitlab\.com)/([^/#?]+)/([^/#?]+)", s, re.I)
    if not m:
        return ""
    return f"{m.group(1).lower()}/{m.group(2).lower()}/{re.sub(r'.git$', '', m.group(3).lower())}"


def tarih(s) -> dt.date | None:
    if not s:
        return None
    try:
        return dt.datetime.fromisoformat(str(s).replace("Z", "+00:00")[:25]).date()
    except Exception:
        try:
            return dt.date.fromisoformat(str(s)[:10])
        except Exception:
            return None


def csv_oku(yol: Path) -> list[dict]:
    if not yol.exists():
        return []
    with yol.open(encoding="utf-8", newline="") as f:
        return [dict(r) for r in csv.DictReader(f)]


def csv_yaz(yol: Path, satirlar: list[dict], alanlar: list[str]):
    with yol.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=alanlar, extrasaction="ignore")
        w.writeheader()
        for s in satirlar:
            w.writerow({k: ("" if s.get(k) is None else s.get(k)) for k in alanlar})


DIL_GRUBU = {
    # jwt.io dil anahtarları ve serbest dil adları -> dil grubu
    "javascript": "JS/TS", "node-js": "JS/TS", "bun": "JS/TS", "deno": "JS/TS", "typescript": "JS/TS",
    "python": "Python",
    "java": "JVM", "kotlin": "JVM", "scala": "JVM", "groovy": "JVM", "clojure": "JVM",
    "go": "Go", "rust": "Rust", "dot-net": ".NET", ".net": ".NET", "c#": ".NET",
    "php": "PHP", "ruby": "Ruby", "swift": "Swift/ObjC", "objective-c": "Swift/ObjC",
    "c": "C/C++", "c-plus-plus": "C/C++", "c/c++": "C/C++", "c++": "C/C++",
}
CEKIRDEK_GRUPLAR = ["JS/TS", "Python", "JVM", "Go", "Rust", ".NET", "PHP", "Ruby", "Swift/ObjC"]


def dil_grubu(dil: str) -> str:
    return DIL_GRUBU.get((dil or "").strip().lower(), "Diğer")


# ---------------------------------------------------------------------------
# 1) TANIMLAMA
# ---------------------------------------------------------------------------
def jwtio_yukle() -> dict:
    durum, veri = http_get(JWTIO_VERI_URL, "jwtio", ham=True)
    if durum != 200:
        raise SystemExit(f"jwt.io verisi alınamadı: {durum}")
    kopya = ONBELLEK / "jwtio_libraries-next.json"
    if not kopya.exists():
        kopya.write_text(veri, "utf-8")
    return json.loads(veri)


def jwtio_adaylari() -> tuple[list[dict], dict]:
    """jwt.io'daki 110 girdiyi benzersiz depolara indirger (J kaynağı)."""
    veri = jwtio_yukle()
    esleme = {r["jwtio_yolu"].lower(): r for r in csv_oku(KOK / "jwtio_esleme.csv")}
    adaylar, gorulen = [], {}
    girdi_sayisi = 0
    for dil_anahtari, dil in veri.items():
        for lib in dil["libs"]:
            girdi_sayisi += 1
            if lib.get("gitHubRepoPath"):
                yol = "github.com/" + lib["gitHubRepoPath"]
            else:
                yol = "bitbucket.org/" + (lib.get("altRepoPath") or "")
            anahtar = yol.lower()
            if anahtar in gorulen:
                gorulen[anahtar]["jwtio_dilleri"].append(dil_anahtari)
                continue
            e = esleme.get(anahtar, {})
            s = lib["support"]
            asim = [a for a in ("rs256", "rs384", "rs512", "es256", "es384", "es512", "ps256", "ps384", "ps512",
                                "eddsa", "ed25519", "ed448", "es256k", "ml-dsa-44", "ml-dsa-65", "ml-dsa-87") if s.get(a)]
            kanonik = (e.get("kanonik_depo") or yol)
            aday = {
                "kaynak": "J", "kaynak_ayrinti": f"jwt.io libraries-next.json@{JWTIO_COMMIT[:7]} [{dil_anahtari}]",
                "tabaka": "JOSE", "ad": (lib["gitHubRepoPath"] or lib.get("altRepoPath") or "").split("/")[-1],
                "dil": dil["name"], "dil_anahtari": dil_anahtari,
                "paket_ekosistemi": e.get("paket_ekosistemi", ""), "paket_adi": e.get("paket_adi", ""),
                "depo": kanonik.lower().split("/tree/")[0], "depo_url": "https://" + kanonik.split("/tree/")[0],
                "alt_dizin": e.get("alt_dizin", ""), "not_esleme": e.get("not", ""),
                "jwtio_verify": s.get("verify"), "jwtio_asimetrik": ",".join(asim),
                "jwtio_ml_dsa": ",".join(a for a in asim if a.startswith("ml-dsa")),
                "jwtio_dilleri": [dil_anahtari],
            }
            gorulen[anahtar] = aday
            adaylar.append(aday)
    ozet = {"jwtio_dil": len(veri), "jwtio_girdi": girdi_sayisi, "jwtio_benzersiz_depo": len(adaylar)}
    return adaylar, ozet


def arama_isabetleri() -> list[dict]:
    """T (GitHub konu), K (paket kaydı), O (kuruluş listesi) kaynaklarının ham isabetleri.
    Her isabet: {kaynak, sorgu, anahtar(depo ya da pkg:), ekosistem, paket, yildiz_ham, indirme_ham, indirme_donemi, aciklama, arsiv_ham, push_ham}
    Gürültü tabanı: T ≥5★; npm ≥100/ay; crates ≥300/90g; NuGet ≥1000 toplam; Packagist ≥50 toplam;
    RubyGems ≥1000 toplam; pub.dev ≥100/30g; Go (pkg.go.dev) ve Maven: taban yok (tarama kararı verir)."""
    isabet = []
    SD = re.compile(r"sd[-_ ]?jwt|selective[- ]disclosure", re.I)
    CO = re.compile(r"\bcose\b|cbor object signing|cose_sign|\bcose[-_.]|[-_.@/]cose\b", re.I)

    # --- T: GitHub konu aramaları (arama API'si; dakikada 10 anonim) ---
    for konu in ["sd-jwt", "sd-jwt-vc", "cose", "oid4vp", "openid4vp"]:
        url = f"https://api.github.com/search/repositories?q=topic:{konu}&per_page=100&sort=stars"
        yol = ONBELLEK / "gh_arama" / f"topic_{konu}.json"
        if yol.exists() and not ARGS.tazele:
            d = json.loads(yol.read_text("utf-8"))
        else:
            durum, d = http_get(url, "gh_arama", bekle=7.0)
            if durum != 200:
                log(f"  ! konu araması başarısız: {konu} ({durum})")
                continue
        for it in d.get("items", []):
            if it["stargazers_count"] < 5:
                continue
            isabet.append(dict(kaynak="T", sorgu=f"topic:{konu}", anahtar="github.com/" + it["full_name"].lower(),
                               ekosistem="", paket="", yildiz_ham=it["stargazers_count"], indirme_ham="",
                               indirme_donemi="", aciklama=(it.get("description") or "")[:120],
                               arsiv_ham=it.get("archived"), push_ham=(it.get("pushed_at") or "")[:10]))

    def yukle(ad, url):
        yol = ONBELLEK / "kayit_arama" / ad
        if yol.exists() and not ARGS.tazele:
            metin = yol.read_text("utf-8")
            return metin
        durum, govde = http_get(url, "kayit_arama", ham=True, bekle=1.0)
        if durum != 200:
            return None
        yol.parent.mkdir(parents=True, exist_ok=True)
        yol.write_text(govde, "utf-8")
        return govde

    # --- K: npm ---
    for ad, url, rx, sorgu in [
        ("npm_sd-jwt.json", "https://registry.npmjs.org/-/v1/search?text=sd-jwt&size=100", SD, "npm:text=sd-jwt"),
        ("npm_cose.json", "https://registry.npmjs.org/-/v1/search?text=keywords:cose&size=100", CO, "npm:keywords:cose"),
        ("npm_text_cose.json", "https://registry.npmjs.org/-/v1/search?text=cose&size=100", CO, "npm:text=cose"),
    ]:
        m = yukle(ad, url)
        if not m:
            continue
        for o in json.loads(m).get("objects", []):
            p = o["package"]
            aylik = (o.get("downloads") or {}).get("monthly") or 0
            metin = p["name"] + " " + (p.get("description") or "") + " " + " ".join(p.get("keywords") or [])
            if aylik < 100 or not rx.search(metin):
                continue
            if "cose" in sorgu and not re.search(r"cose", p["name"], re.I) and not CO.search(p.get("description") or ""):
                continue
            depo = depo_normalize((p.get("links") or {}).get("repository", ""))
            isabet.append(dict(kaynak="K", sorgu=sorgu, anahtar=depo or f"pkg:npm:{p['name']}", ekosistem="npm",
                               paket=p["name"], yildiz_ham="", indirme_ham=aylik, indirme_donemi="npm-aylik",
                               aciklama=(p.get("description") or "")[:120], arsiv_ham="", push_ham=(p.get("date") or "")[:10]))
    # --- K: crates.io ---
    for ad, url, rx, sorgu in [
        ("crates_sd-jwt.json", "https://crates.io/api/v1/crates?q=sd-jwt&per_page=100", SD, "crates:q=sd-jwt"),
        ("crates_cose.json", "https://crates.io/api/v1/crates?q=cose&per_page=100", CO, "crates:q=cose"),
    ]:
        m = yukle(ad, url)
        if not m:
            continue
        for c in json.loads(m).get("crates", []):
            r90 = c.get("recent_downloads") or 0
            if r90 < 300 or not rx.search(c["name"] + " " + (c.get("description") or "")):
                continue
            depo = depo_normalize(c.get("repository") or "")
            isabet.append(dict(kaynak="K", sorgu=sorgu, anahtar=depo or f"pkg:cargo:{c['name']}", ekosistem="cargo",
                               paket=c["name"], yildiz_ham="", indirme_ham=r90, indirme_donemi="crates-90g",
                               aciklama=(c.get("description") or "")[:120], arsiv_ham="", push_ham=(c.get("updated_at") or "")[:10]))
    # --- K: NuGet ---
    for ad, url, rx, sorgu in [
        ("nuget_sd-jwt.json", "https://azuresearch-usnc.nuget.org/query?q=sd-jwt&take=100", SD, "nuget:q=sd-jwt"),
        ("nuget_cose.json", "https://azuresearch-usnc.nuget.org/query?q=cose&take=100", CO, "nuget:q=cose"),
    ]:
        m = yukle(ad, url)
        if not m:
            continue
        for c in json.loads(m).get("data", []):
            t = c.get("totalDownloads") or 0
            metin = c["id"] + " " + (c.get("description") or "") + " " + " ".join(c.get("tags") or [])
            if t < 1000 or not rx.search(metin):
                continue
            depo = depo_normalize(c.get("projectUrl") or "")
            isabet.append(dict(kaynak="K", sorgu=sorgu, anahtar=depo or f"pkg:nuget:{c['id'].lower()}", ekosistem="nuget",
                               paket=c["id"], yildiz_ham="", indirme_ham=t, indirme_donemi="nuget-toplam",
                               aciklama=(c.get("description") or "")[:120], arsiv_ham="", push_ham=""))
    # --- K: Packagist ---
    m = yukle("packagist_sd-jwt.json", "https://packagist.org/search.json?q=sd-jwt&per_page=100")
    if m:
        for r in json.loads(m).get("results", []):
            if (r.get("downloads") or 0) < 50:
                continue
            isabet.append(dict(kaynak="K", sorgu="packagist:q=sd-jwt", anahtar=depo_normalize(r.get("repository") or "") or f"pkg:packagist:{r['name']}",
                               ekosistem="packagist", paket=r["name"], yildiz_ham=r.get("favers", ""), indirme_ham=r.get("downloads"),
                               indirme_donemi="packagist-toplam", aciklama=(r.get("description") or "")[:120], arsiv_ham="", push_ham=""))
    # --- K: Maven Central (search.maven.org) ---
    for ad, url, sorgu in [
        ("maven_sd-jwt.json", "https://search.maven.org/solrsearch/select?q=sd-jwt&rows=100&wt=json", "maven:q=sd-jwt"),
        ("maven_sdjwt.json", "https://search.maven.org/solrsearch/select?q=sdjwt&rows=100&wt=json", "maven:q=sdjwt"),
        ("maven_cose.json", "https://search.maven.org/solrsearch/select?q=cose&rows=100&wt=json", "maven:q=cose"),
    ]:
        m = yukle(ad, url)
        if not m:
            continue
        for r in json.loads(m)["response"]["docs"]:
            ga = f"{r['g']}:{r['a']}"
            isabet.append(dict(kaynak="K", sorgu=sorgu, anahtar=f"pkg:maven:{ga.lower()}", ekosistem="maven", paket=ga,
                               yildiz_ham="", indirme_ham="", indirme_donemi="", aciklama=f"latestVersion={r.get('latestVersion')}",
                               arsiv_ham="", push_ham=""))
    # --- K: RubyGems ---
    for ad, url, rx, sorgu in [
        ("rubygems_sd-jwt.json", "https://rubygems.org/api/v1/search.json?query=sd-jwt", re.compile(r".*"), "gem:q=sd-jwt"),
        ("rubygems_cose.json", "https://rubygems.org/api/v1/search.json?query=cose", CO, "gem:q=cose"),
    ]:
        m = yukle(ad, url)
        if not m:
            continue
        for r in json.loads(m):
            if (r.get("downloads") or 0) < 1000 or not rx.search(r["name"] + " " + (r.get("info") or "")):
                continue
            depo = depo_normalize(r.get("source_code_uri") or r.get("homepage_uri") or "")
            isabet.append(dict(kaynak="K", sorgu=sorgu, anahtar=depo or f"pkg:rubygems:{r['name']}", ekosistem="rubygems",
                               paket=r["name"], yildiz_ham="", indirme_ham=r.get("downloads"), indirme_donemi="gem-toplam",
                               aciklama=(r.get("info") or "")[:120], arsiv_ham="", push_ham=""))
    # --- K: pub.dev (arama + paket ayrıntısı) ---
    for sorgu_metni in ["sd-jwt", "cose"]:
        m = yukle(f"pub_{sorgu_metni}.json", f"https://pub.dev/api/search?q={sorgu_metni}")
        if not m:
            continue
        for p in json.loads(m).get("packages", []):
            ad = p["package"]
            dm = yukle(f"pub_{ad}.json", f"https://pub.dev/api/packages/{ad}")
            sm = yukle(f"pub_{ad}_score.json", f"https://pub.dev/api/packages/{ad}/score")
            if not dm or not sm:
                continue
            d, s = json.loads(dm), json.loads(sm)
            ps = d["latest"]["pubspec"]
            metin = ad + " " + (ps.get("description") or "")
            rx = SD if sorgu_metni == "sd-jwt" else CO
            dl30 = s.get("downloadCount30Days") or 0
            if dl30 < 100 or not rx.search(metin):
                continue
            depo = depo_normalize(ps.get("repository") or ps.get("homepage") or "")
            isabet.append(dict(kaynak="K", sorgu=f"pub:q={sorgu_metni}", anahtar=depo or f"pkg:pub:{ad}", ekosistem="pub",
                               paket=ad, yildiz_ham="", indirme_ham=dl30, indirme_donemi="pub-30g",
                               aciklama=(ps.get("description") or "")[:120], arsiv_ham="", push_ham=d["latest"].get("published", "")[:10]))
    # --- K: pkg.go.dev (HTML) ---
    for sorgu_metni in ["sd-jwt", "cose"]:
        m = yukle(f"gopkg_{sorgu_metni}.html", f"https://pkg.go.dev/search?q={sorgu_metni}&m=package&limit=100")
        if not m:
            continue
        gorulen = []
        for mod in re.findall(r'href="/((?:github\.com|gitlab\.com|go\.|gopkg\.in|codeberg\.org)[^"?#]+)"', m):
            if mod not in gorulen:
                gorulen.append(mod)
        for mod in gorulen:
            depo = depo_normalize("https://" + mod)
            if mod.startswith("go.mozilla.org/cose") or mod.startswith("gopkg.in/mozilla-services/go-cose"):
                depo = "github.com/mozilla-services/go-cose"
            # Go için gürültü tabanı: GitHub deposu ≥5★ (konu aramasıyla aynı taban; yıldız ecosyste.ms'ten)
            yildiz = ""
            if depo.startswith("github.com/"):
                _, s, r = depo.split("/", 2)
                durum, d = http_get(f"https://repos.ecosyste.ms/api/v1/hosts/GitHub/repositories/{urllib.parse.quote(s + '/' + r, safe='')}",
                                    "eco_repo", kirp=_eco_repo_kirp)
                if durum == 200 and isinstance(d, dict) and d.get("full_name"):
                    yildiz = d.get("stargazers_count")
                    if isinstance(yildiz, int) and yildiz < 5:
                        continue
            isabet.append(dict(kaynak="K", sorgu=f"pkg.go.dev:q={sorgu_metni}", anahtar=depo or f"pkg:go:{mod}", ekosistem="go",
                               paket=mod, yildiz_ham=yildiz, indirme_ham="", indirme_donemi="", aciklama="", arsiv_ham="", push_ham=""))
    # --- K: PyPI (arama API'si yok; ad yoklaması) ---
    for ad in ["sd-jwt", "pyeudiw", "pycose", "cwt", "joserfc"]:
        m = yukle(f"pypi_{ad}.json", f"https://pypi.org/pypi/{ad}/json")
        if not m:
            continue
        i = json.loads(m)["info"]
        pu = {k.lower(): v for k, v in (i.get("project_urls") or {}).items()}
        depo = ""
        oncelik = [pu.get(k) for k in ("source", "repository", "source code", "code", "homepage")]
        for v in oncelik + list(pu.values()) + [i.get("home_page") or ""]:
            d0 = depo_normalize(v or "")
            if d0 and not d0.startswith("github.com/sponsors/"):
                depo = d0
                break
        isabet.append(dict(kaynak="K", sorgu=f"pypi:ad={ad}", anahtar=depo or f"pkg:pypi:{ad}", ekosistem="pypi", paket=ad,
                           yildiz_ham="", indirme_ham="", indirme_donemi="", aciklama=(i.get("summary") or "")[:120], arsiv_ham="", push_ham=""))
    # --- O: kuruluş listeleri (ad/açıklama süzgeci) ---
    ORX = re.compile(r"sd-?jwt|cose|verifier|openid4vp|oid4vp|oid4vc|jose|jws", re.I)
    for sahip in ["eu-digital-identity-wallet", "openwallet-foundation", "openwallet-foundation-labs", "cose-wg"]:
        yol = ONBELLEK / "eco_owner" / f"{sahip}.json"
        if yol.exists() and not ARGS.tazele:
            d = json.loads(yol.read_text("utf-8"))
        else:
            durum, d = http_get(f"https://repos.ecosyste.ms/api/v1/hosts/GitHub/owners/{sahip}/repositories?per_page=200", "eco_owner")
            if durum != 200:
                continue
        for r in d:
            metin = r["full_name"] + " " + (r.get("description") or "")
            if not ORX.search(metin):
                continue
            isabet.append(dict(kaynak="O", sorgu=f"org:{sahip}", anahtar="github.com/" + r["full_name"].lower(), ekosistem="",
                               paket="", yildiz_ham=r.get("stargazers_count"), indirme_ham="", indirme_donemi="",
                               aciklama=(r.get("description") or "")[:120], arsiv_ham=r.get("archived"), push_ham=str(r.get("pushed_at") or "")[:10]))
    return isabet


# ---------------------------------------------------------------------------
# 2) TARAMA
# ---------------------------------------------------------------------------
def tarama(jwt_adaylar: list[dict], isabetler: list[dict]):
    """Arama isabetlerini tarama_kararlari.csv ile birleştirir. Döndürür: (tarama_satirlari, ek_adaylar)."""
    kararlar = {r["anahtar"].strip().lower(): r for r in csv_oku(KOK / "tarama_kararlari.csv")}
    jwt_depolar = {a["depo"] for a in jwt_adaylar}
    # isabetleri anahtara göre topla
    grup: dict[str, dict] = {}
    for h in isabetler:
        g = grup.setdefault(h["anahtar"], {"anahtar": h["anahtar"], "kaynaklar": set(), "sorgular": set(),
                                            "paketler": set(), "yildiz_ham": "", "indirme_ham": "", "aciklama": "",
                                            "arsiv_ham": "", "push_ham": ""})
        g["kaynaklar"].add(h["kaynak"])
        g["sorgular"].add(h["sorgu"])
        if h["paket"]:
            g["paketler"].add(f"{h['ekosistem']}:{h['paket']}")
        for k in ("yildiz_ham", "indirme_ham", "aciklama", "arsiv_ham", "push_ham"):
            if h.get(k) not in ("", None) and g[k] in ("", None):
                g[k] = h[k]
    # kararlarda olup isabetlerde olmayanlar: yalnız G (görev/plan), H (halef) ya da P (pilot) kaynaklılar
    # çerçeveye girer; diğerleri gürültü tabanının altında kalmış isabetlerdir ("taban-alti").
    taban_alti = set()
    for anahtar, k in kararlar.items():
        if anahtar not in grup:
            kaynaklar = set(filter(None, k.get("kaynak", "").split("+")))
            if not kaynaklar & {"G", "Gt", "H", "P"}:
                taban_alti.add(anahtar)
            grup[anahtar] = {"anahtar": anahtar, "kaynaklar": kaynaklar or {"K"},
                             "sorgular": {k.get("kaynak_ayrinti", "")}, "paketler": set(), "yildiz_ham": "",
                             "indirme_ham": "", "aciklama": "", "arsiv_ham": "", "push_ham": ""}
        else:
            for kk in filter(None, k.get("kaynak", "").split("+")):
                if kk in ("G", "Gt", "H", "P"):
                    grup[anahtar]["kaynaklar"].add(kk)
    satirlar, ek = [], []
    for anahtar, g in sorted(grup.items()):
        k = kararlar.get(anahtar)
        if anahtar in jwt_depolar and not k:
            karar, gerekce = "yinelenen-jwtio", "jwt.io çerçevesinde zaten var (J kaynağı)"
        elif anahtar in taban_alti:
            karar, gerekce = "taban-alti", "gürültü tabanının altında (pkg.go.dev isabeti, GitHub <5★); önceki karar: " + (k or {}).get("karar", "")
        elif not k:
            karar, gerekce = "INCELENECEK", "tarama kararı yok"
        else:
            karar, gerekce = k["karar"], k.get("gerekce", "")
        satir = dict(anahtar=anahtar, kaynaklar="+".join(sorted(g["kaynaklar"])), sorgular="; ".join(sorted(filter(None, g["sorgular"]))),
                     paketler="; ".join(sorted(g["paketler"])), yildiz_ham=g["yildiz_ham"], indirme_ham=g["indirme_ham"],
                     aciklama=g["aciklama"], karar=karar, tabaka=(k or {}).get("tabaka", ""), gerekce=gerekce)
        satirlar.append(satir)
        if karar == "aday":
            depo = anahtar if not anahtar.startswith("pkg:") else ""
            ek.append({
                "kaynak": satir["kaynaklar"], "kaynak_ayrinti": satir["sorgular"],
                "tabaka": k["tabaka"], "ad": k.get("ad") or (anahtar.split("/")[-1] if depo else anahtar.split(":")[-1]),
                "dil": k.get("dil", ""), "dil_anahtari": k.get("dil", "").lower(),
                "paket_ekosistemi": k.get("paket_ekosistemi", ""), "paket_adi": k.get("paket_adi", ""),
                "depo": depo or (depo_normalize(k.get("depo_url", "")) if k.get("depo_url") else ""),
                "depo_url": k.get("depo_url") or (("https://" + depo) if depo else ""),
                "alt_dizin": k.get("alt_dizin", ""), "not_esleme": k.get("gerekce", ""),
                "jwtio_verify": "", "jwtio_asimetrik": "", "jwtio_ml_dsa": "", "jwtio_dilleri": [],
            })
    return satirlar, ek


# ---------------------------------------------------------------------------
# 3) META VERİ
# ---------------------------------------------------------------------------
def _eco_repo_kirp(d):
    if not isinstance(d, dict):
        return d
    tut = ["full_name", "html_url", "description", "fork", "archived", "stargazers_count", "forks_count",
           "pushed_at", "created_at", "updated_at", "license", "language", "default_branch", "source_name",
           "status", "topics", "size", "last_synced_at", "error"]
    return {k: d.get(k) for k in tut}


def repo_meta(depo: str) -> dict:
    """Depo düzeyi meta: ecosyste.ms (yıldız, push, arşiv, lisans), deps.dev (yıldız, lisans, OpenSSF)."""
    sonuc = {}
    if not depo:
        return sonuc
    host, sahip, ad = depo.split("/", 2)
    if host == "github.com":
        durum, d = http_get(f"https://repos.ecosyste.ms/api/v1/hosts/GitHub/repositories/{urllib.parse.quote(sahip + '/' + ad, safe='')}",
                            "eco_repo", kirp=_eco_repo_kirp)
        if durum == 200 and isinstance(d, dict) and d.get("full_name"):
            sonuc.update(eco_tam_ad=d["full_name"], eco_yildiz=d.get("stargazers_count"), eco_push=d.get("pushed_at"),
                         eco_arsiv=d.get("archived"), eco_lisans=d.get("license"), eco_dil=d.get("language"),
                         eco_fork=d.get("fork"), eco_kaynak=d.get("source_name"), eco_dal=d.get("default_branch"),
                         eco_aciklama=(d.get("description") or "")[:200])
        durum, p = http_get(f"https://api.deps.dev/v3/projects/{urllib.parse.quote(depo, safe='')}", "depsdev_proje",
                            kirp=lambda x: {k: x.get(k) for k in ("projectKey", "starsCount", "forksCount", "license", "description")}
                            | {"scorecard_overall": (x.get("scorecard") or {}).get("overallScore"),
                               "scorecard_date": (x.get("scorecard") or {}).get("date")} if isinstance(x, dict) else x)
        if durum == 200 and isinstance(p, dict):
            sonuc.update(dd_yildiz=p.get("starsCount"), dd_lisans=p.get("license"), dd_openssf=p.get("scorecard_overall"))
        if "eco_tam_ad" not in sonuc and "dd_yildiz" not in sonuc:
            # son çare: GitHub API (yeniden adlandırmaları da çözer)
            durum, g = gh_api(f"repos/{sahip}/{ad}")
            if durum == 200 and isinstance(g, dict):
                sonuc.update(gh_tam_ad=g.get("full_name"), eco_yildiz=g.get("stargazers_count"), eco_push=g.get("pushed_at"),
                             eco_arsiv=g.get("archived"), eco_lisans=((g.get("license") or {}).get("spdx_id") or "").lower(),
                             eco_dil=g.get("language"), eco_fork=g.get("fork"), eco_dal=g.get("default_branch"),
                             eco_aciklama=(g.get("description") or "")[:200])
    elif host == "bitbucket.org":
        durum, b = http_get(f"https://api.bitbucket.org/2.0/repositories/{sahip}/{ad}", "bitbucket",
                            kirp=lambda x: {k: x.get(k) for k in ("full_name", "updated_on", "language", "is_private", "description")}
                            | {"mainbranch": (x.get("mainbranch") or {}).get("name")} if isinstance(x, dict) else x)
        if durum == 200 and isinstance(b, dict):
            sonuc.update(eco_tam_ad=b.get("full_name"), eco_dil=b.get("language"), eco_dal=b.get("mainbranch"),
                         eco_aciklama=(b.get("description") or "")[:200], eco_arsiv=False)
        durum, c = http_get(f"https://api.bitbucket.org/2.0/repositories/{sahip}/{ad}/commits?pagelen=1", "bitbucket",
                            kirp=lambda x: {"values": [{"hash": v.get("hash"), "date": v.get("date")} for v in (x.get("values") or [])[:1]]})
        if durum == 200 and isinstance(c, dict) and c.get("values"):
            sonuc.update(bb_son_commit=c["values"][0]["date"], bb_son_sha=c["values"][0]["hash"])
    return sonuc


# Anonim git: kimlik bilgisi yardımcıları (ör. Git Credential Manager) ve parola istemleri kapalı.
# Silinmiş/özel depolar 401 döndürünce GCM'nin oturum açma penceresi AÇILMAMALI (gizlilik kuralı).
GIT_ANONIM = ["git", "-c", "credential.helper=", "-c", "credential.interactive=never", "-c", "core.askPass="]
GIT_ORTAM = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never", GIT_ASKPASS="", SSH_ASKPASS="",
                 GIT_CONFIG_NOSYSTEM="1")


def git_bas(depo_url: str, anahtar: str) -> dict:
    """Varsayılan dal HEAD'i: sha + committer tarihi. Blob'suz, derinliği 1 klon; yalnız sha/tarih önbelleğe yazılır."""
    onb = ONBELLEK / "git" / (re.sub(r"[^a-z0-9]+", "_", anahtar.lower()) + ".json")
    if onb.exists() and not ARGS.tazele:
        return json.loads(onb.read_text("utf-8"))
    if ARGS.cevrimdisi or not depo_url:
        return {}
    hedef = Path(ARGS.klon_dizini) / "meta" / re.sub(r"[^a-z0-9]+", "_", anahtar.lower())
    if hedef.exists():
        shutil.rmtree(hedef, ignore_errors=True)
    hedef.parent.mkdir(parents=True, exist_ok=True)
    sonuc = {}
    try:
        r = subprocess.run(GIT_ANONIM + ["clone", "--quiet", "--depth", "1", "--filter=tree:0", "--no-checkout",
                            depo_url.rstrip("/") + ".git", str(hedef)],
                           capture_output=True, text=True, timeout=300, env=GIT_ORTAM)
        if r.returncode == 0:
            q = subprocess.run(GIT_ANONIM + ["-C", str(hedef), "log", "-1", "--format=%H|%cI"], capture_output=True, text=True, timeout=60)
            sha, tarihi = q.stdout.strip().split("|")
            dal = subprocess.run(GIT_ANONIM + ["-C", str(hedef), "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True).stdout.strip()
            sonuc = {"sha": sha, "commit_tarihi": tarihi, "dal": dal, "alindi_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
        else:
            sonuc = {"hata": r.stderr.strip()[:300]}
    except Exception as e:
        sonuc = {"hata": str(e)[:300]}
    finally:
        shutil.rmtree(hedef, ignore_errors=True)
    onb.parent.mkdir(parents=True, exist_ok=True)
    onb.write_text(json.dumps(sonuc, ensure_ascii=False), "utf-8")
    return sonuc


DEPSDEV_SISTEM = {"npm": "npm", "pypi": "pypi", "maven": "maven", "go": "go", "cargo": "cargo", "nuget": "nuget", "rubygems": "rubygems"}
ECO_REGISTRY = {"npm": "npmjs.org", "pypi": "pypi.org", "cargo": "crates.io", "maven": "repo1.maven.org", "go": "proxy.golang.org",
                "nuget": "nuget.org", "packagist": "packagist.org", "rubygems": "rubygems.org", "pub": "pub.dev", "hex": "hex.pm",
                "cocoapods": "cocoapods.org", "hackage": "hackage.haskell.org", "cpan": "metacpan.org", "clojars": "clojars.org",
                "luarocks": "luarocks.org", "swiftpm": "swiftpackageindex.com"}


def paket_meta(eko: str, paket: str) -> dict:
    """Paket düzeyi meta: son sürüm + tarih, aylık indirme (varsa), bağımlı paket sayısı (ecosyste.ms)."""
    s = {}
    if not eko or not paket or eko in ("kaynak",):
        return s
    # deps.dev: sürümler (varsayılan sürüm + yayım tarihi)
    if eko in DEPSDEV_SISTEM:
        durum, d = http_get(f"https://api.deps.dev/v3/systems/{DEPSDEV_SISTEM[eko]}/packages/{urllib.parse.quote(paket, safe='')}",
                            "depsdev_paket",
                            kirp=lambda x: {"versions": [v for v in (x.get("versions") or []) if v.get("isDefault")] +
                                            sorted([v for v in (x.get("versions") or []) if v.get("publishedAt")],
                                                   key=lambda v: v.get("publishedAt") or "")[-3:]} if isinstance(x, dict) else x)
        if durum == 200 and isinstance(d, dict):
            vs = d.get("versions") or []
            var = [v for v in vs if v.get("isDefault")]
            if var:
                s.update(son_surum=var[0]["versionKey"]["version"], son_surum_tarihi=(var[0].get("publishedAt") or "")[:10])
            elif vs:
                v = sorted(vs, key=lambda v: v.get("publishedAt") or "")[-1]
                s.update(son_surum=v["versionKey"]["version"], son_surum_tarihi=(v.get("publishedAt") or "")[:10])
    # ecosyste.ms packages: bağımlılar + (bazı kayıtlarda) indirme + son sürüm yedeği
    reg = ECO_REGISTRY.get(eko)
    if reg:
        ad = paket
        if eko == "swiftpm":
            ad = depo_normalize(paket)
        durum, p = http_get(f"https://packages.ecosyste.ms/api/v1/registries/{reg}/packages/{urllib.parse.quote(ad, safe='')}",
                            "eco_paket", kirp=lambda x: {k: x.get(k) for k in (
                                "name", "ecosystem", "downloads", "downloads_period", "latest_release_number",
                                "latest_release_published_at", "dependent_packages_count", "dependent_repos_count",
                                "repository_url", "normalized_licenses", "status", "error")} if isinstance(x, dict) else x)
        if durum == 200 and isinstance(p, dict) and p.get("name"):
            s.update(bagimli_paket=p.get("dependent_packages_count"), bagimli_depo=p.get("dependent_repos_count"),
                     eco_indirme=p.get("downloads"), eco_indirme_donemi=p.get("downloads_period"),
                     paket_lisans=",".join(p.get("normalized_licenses") or []), paket_durum=p.get("status"))
            if not s.get("son_surum"):
                s.update(son_surum=p.get("latest_release_number"), son_surum_tarihi=(p.get("latest_release_published_at") or "")[:10])
    # yerel indirme API'leri
    if eko == "npm":
        durum, d = http_get(f"https://api.npmjs.org/downloads/point/last-month/{paket}", "npm_indirme")
        if durum == 200 and isinstance(d, dict):
            s.update(aylik_indirme=d.get("downloads"), indirme_kaynagi="npm last-month")
    elif eko == "pypi":
        durum, d = http_get(f"https://pypistats.org/api/packages/{paket.lower()}/recent", "pypistats", bekle=1.0)
        if durum == 200 and isinstance(d, dict):
            s.update(aylik_indirme=(d.get("data") or {}).get("last_month"), indirme_kaynagi="pypistats last_month")
    elif eko == "cargo":
        durum, d = http_get(f"https://crates.io/api/v1/crates/{paket}", "crates", bekle=1.0,
                            kirp=lambda x: {"crate": {k: (x.get("crate") or {}).get(k) for k in (
                                "name", "downloads", "recent_downloads", "max_stable_version", "max_version", "updated_at", "repository")}}
                            if isinstance(x, dict) else x)
        if durum == 200 and isinstance(d, dict):
            c = d.get("crate") or {}
            if c.get("recent_downloads") is not None:
                s.update(aylik_indirme=round(c["recent_downloads"] / 3), indirme_kaynagi="crates.io recent_downloads(90g)/3")
    elif eko == "packagist":
        durum, d = http_get(f"https://packagist.org/packages/{paket}.json", "packagist",
                            kirp=lambda x: {"package": {"downloads": (x.get("package") or {}).get("downloads"),
                                                        "repository": (x.get("package") or {}).get("repository"),
                                                        "abandoned": (x.get("package") or {}).get("abandoned"),
                                                        "github_stars": (x.get("package") or {}).get("github_stars")}}
                            if isinstance(x, dict) else x)
        if durum == 200 and isinstance(d, dict):
            dl = ((d.get("package") or {}).get("downloads") or {})
            s.update(aylik_indirme=dl.get("monthly"), indirme_kaynagi="packagist monthly", toplam_indirme=dl.get("total"),
                     packagist_terk=(d.get("package") or {}).get("abandoned"))
    elif eko == "nuget":
        durum, d = http_get(f"https://azuresearch-usnc.nuget.org/query?q=packageid:{urllib.parse.quote(paket)}&prerelease=false&take=1",
                            "nuget", kirp=lambda x: {"data": [{k: v.get(k) for k in ("id", "version", "totalDownloads", "projectUrl")}
                                                              for v in (x.get("data") or [])[:1]]} if isinstance(x, dict) else x)
        if durum == 200 and isinstance(d, dict) and d.get("data"):
            s.update(toplam_indirme=d["data"][0].get("totalDownloads"))
    elif eko == "rubygems":
        durum, d = http_get(f"https://rubygems.org/api/v1/gems/{paket}.json", "rubygems",
                            kirp=lambda x: {k: x.get(k) for k in ("name", "downloads", "version", "version_created_at", "source_code_uri", "licenses")}
                            if isinstance(x, dict) else x)
        if durum == 200 and isinstance(d, dict):
            s.update(toplam_indirme=d.get("downloads"))
            if not s.get("son_surum"):
                s.update(son_surum=d.get("version"), son_surum_tarihi=(d.get("version_created_at") or "")[:10])
    elif eko == "pub":
        durum, d = http_get(f"https://pub.dev/api/packages/{paket}/score", "pub")
        if durum == 200 and isinstance(d, dict):
            s.update(aylik_indirme=d.get("downloadCount30Days"), indirme_kaynagi="pub.dev downloadCount30Days")
    elif eko == "hex":
        durum, d = http_get(f"https://hex.pm/api/packages/{paket}", "hex",
                            kirp=lambda x: {k: x.get(k) for k in ("name", "downloads", "latest_stable_version", "updated_at")} if isinstance(x, dict) else x)
        if durum == 200 and isinstance(d, dict):
            rec = (d.get("downloads") or {}).get("recent")
            if rec is not None:
                s.update(aylik_indirme=round(rec / 3), indirme_kaynagi="hex.pm recent(90g)/3")
    # ecosyste.ms indirme yedeği (aylık dönem ise)
    if s.get("aylik_indirme") in (None, "") and s.get("eco_indirme") and s.get("eco_indirme_donemi") == "last-month":
        s.update(aylik_indirme=s["eco_indirme"], indirme_kaynagi="ecosyste.ms last-month")
    return s


# ---------------------------------------------------------------------------
# 4) ÖLÇÜTLER VE SEÇİM
# ---------------------------------------------------------------------------
# Eşik seçenekleri (KRITERLER-TASLAK.md §3). "ya da" bağlaçlı: yıldız, aylık indirme, bağımlı paket.
ESIKLER = {
    "E1": {"_ad": "Tek biçim, gevşek: ≥50★ ya da ≥10k/ay ya da ≥50 bağımlı paket (tüm tabakalar)",
           "JOSE": (50, 10_000, 50), "SDJWT": (50, 10_000, 50), "COSE": (50, 10_000, 50), "REF": (50, 10_000, 50)},
    "E2": {"_ad": "Tabakaya göre ölçekli (ÖNERİLEN): JOSE ≥200★/≥100k/≥100 bağımlı; SD-JWT ve COSE ≥20★/≥1k/≥10 bağımlı; REF ≥20★",
           "JOSE": (200, 100_000, 100), "SDJWT": (20, 1_000, 10), "COSE": (20, 1_000, 10), "REF": (20, None, None)},
    "E3": {"_ad": "Tek biçim, sıkı: ≥200★ ya da ≥100k/ay ya da ≥100 bağımlı paket",
           "JOSE": (200, 100_000, 100), "SDJWT": (200, 100_000, 100), "COSE": (200, 100_000, 100), "REF": (200, 100_000, 100)},
    "E4": {"_ad": "Tabakaya göre ölçekli, gevşek: JOSE ≥50★/≥10k/≥50; SD-JWT ve COSE ≥10★/≥500/≥5; REF ≥10★",
           "JOSE": (50, 10_000, 50), "SDJWT": (10, 500, 5), "COSE": (10, 500, 5), "REF": (10, None, None)},
    "E5": {"_ad": "Yüksek eşik + sayım (kota yok) seçeneği: JOSE ≥1000★/≥1M/≥500; SD-JWT ≥50★/≥10k/≥10; COSE ≥40★/≥10k/≥10; REF ≥100★",
           "JOSE": (1000, 1_000_000, 500), "SDJWT": (50, 10_000, 10), "COSE": (40, 10_000, 10), "REF": (100, None, None)},
}
RESMI_REFERANS_SAHIPLERI = {"eu-digital-identity-wallet", "openwallet-foundation", "openwallet-foundation-labs"}
# Sürüm 3 §9.2 pilot kümesi (jose, @sd-jwt/core [halef depo], jwcrypto, Authlib, joserfc)
PILOT_DEPOLARI = {"github.com/panva/jose", "github.com/openwallet-foundation-labs/identity-common-ts", "github.com/latchset/jwcrypto",
                  "github.com/lepture/authlib", "github.com/authlib/joserfc"}
KOTALAR = {"JOSE": 18, "SDJWT": 8, "COSE": 5, "REF": 3}  # toplam 34 (25–40 aralığında); gerekçe KRITERLER-TASLAK.md §4


def olcutleri_uygula(a: dict, esik: str) -> tuple[bool, list[str]]:
    """K1–K8'i uygular (K6 Linux: yalnız belge düzeyi ön eleme; nihai test C3 kurulumunda)."""
    neden = []
    # K7 kapsam zaten tarama aşamasında; burada K1..K8
    if a["tabaka"] == "JOSE" and a.get("kaynak") == "J":
        if a.get("jwtio_verify") is False:
            neden.append("K1: doğrulama yok")
        asim = [x for x in (a.get("jwtio_asimetrik") or "").split(",") if x]
        if not asim and a.get("k1_elle") != "evet":
            neden.append("K1: yalnız simetrik (jwt.io destek bayrakları: asimetrik alg yok)")
    if a.get("k1_elle") == "hayir":
        neden.append("K1: asimetrik doğrulama yok (belge)")
    son = tarih(a.get("son_commit"))
    if son is None:
        neden.append("K2: son commit tarihi alınamadı")
    elif son < ETKINLIK_SINIRI:
        neden.append(f"K2: son commit {son.isoformat()} < {ETKINLIK_SINIRI.isoformat()}")
    if a.get("arsiv") is True:
        neden.append("K3: depo arşivlenmiş")
    if a.get("k3_elle"):
        neden.append("K3: " + a["k3_elle"])
    lis = (a.get("lisans") or "").strip().lower()
    if not lis or lis in GECERSIZ_LISANS:
        if not a.get("k4_elle"):
            neden.append(f"K4: açık lisans doğrulanamadı ({lis or 'yok'}; kaynak: {a.get('lisans_kaynagi') or '-'})")
    if a.get("k4_elle") == "hayir":
        neden.append("K4: açık kaynak lisansı değil (belge)")
    # K5 eşik
    y, ind, bag = ESIKLER[esik][a["tabaka"]]
    yildiz = a.get("yildiz")
    aylik = a.get("aylik_indirme")
    bagimli = a.get("bagimli_paket")
    gecti = False
    if y is not None and isinstance(yildiz, int) and yildiz >= y:
        gecti = True
    if ind is not None and isinstance(aylik, int) and aylik >= ind:
        gecti = True
    if bag is not None and isinstance(bagimli, int) and bagimli >= bag:
        gecti = True
    toplam = a.get("toplam_indirme")
    if ind is not None and aylik is None and isinstance(toplam, int) and toplam >= 12 * ind:
        gecti = True  # aylık istatistik yayımlamayan kayıtlar (NuGet, RubyGems): toplam ≥ 12 × aylık eşik
    if a["tabaka"] in ("SDJWT", "REF") and a.get("depo", "").split("/")[1:2] and a["depo"].split("/")[1] in RESMI_REFERANS_SAHIPLERI:
        gecti = True  # resmî referans uygulama muafiyeti (KRITERLER-TASLAK.md K5-istisna)
    if a["tabaka"] == "REF" and "G" in (a.get("kaynak") or "").split("+"):
        gecti = True  # plan/görev tanımında adı geçen referans doğrulayıcı
    if not gecti:
        neden.append(f"K5[{esik}]: eşik altı (★{yildiz}, aylık {aylik}, bağımlı {bagimli}, toplam {toplam})")
    if a.get("k6_elle"):
        neden.append("K6: " + a["k6_elle"])
    if a.get("k8_elle"):
        neden.append("K8: " + a["k8_elle"])
    return (not neden), neden


GOSTERGELER = ("yildiz", "aylik_indirme", "bagimli_paket", "toplam_indirme_yalniz")
# toplam_indirme_yalniz: yalnız aylık indirme yayımlamayan kayıtlar (NuGet, RubyGems) için toplam indirme
GECERSIZ_LISANS = {"none", "other", "noassertion", "non-standard", "unknown", "unlicensed", "proprietary", ""}


def lisans_sec(adaylar: list[tuple[str, str | None]]) -> tuple[str, str]:
    """İlk geçerli SPDX benzeri lisans değerini (ve kaynağını) seçer; hiçbiri geçerli değilse ilk boş olmayanı
    '(geçersiz)' etiketiyle döndürür. deps.dev bazı depolarda GitHub'ın eşleştiremediği lisansları 'non-standard'
    raporladığı için tek kaynağa güvenilmez (ör. veraison/go-cose: ecosyste.ms 'mpl-2.0')."""
    for kaynak, l in adaylar:
        if l and str(l).strip().lower() not in GECERSIZ_LISANS:
            return str(l).strip(), kaynak
    for kaynak, l in adaylar:
        if l:
            return str(l).strip(), kaynak + " (geçersiz)"
    return "", ""


def populerlik_puanla(adaylar: list[dict]):
    """Eşikten bağımsız popülerlik puanı (KRITERLER-TASLAK.md §5.2):
    her gösterge için TABAKA-İÇİ (o göstergesi olan tüm çerçeve adayları) orta-sıra yüzdeliği
    p = (#(değer < v) + 0,5·#(değer = v)) / n; eksik gösterge yok sayılır (eşit değerler şişirilmez).
    pop_puani = mevcut göstergelerin en yüksek yüzdeliği; pop_puani2 = ikinci en yüksek (eşitlik bozucu)."""
    from bisect import bisect_left, bisect_right
    for a in adaylar:
        a["toplam_indirme_yalniz"] = (a.get("toplam_indirme") if a.get("aylik_indirme") is None
                                      and isinstance(a.get("toplam_indirme"), int) else None)
    for tabaka in {a["tabaka"] for a in adaylar}:
        grup = [a for a in adaylar if a["tabaka"] == tabaka]
        for g in GOSTERGELER:
            degerler = sorted(a[g] for a in grup if isinstance(a.get(g), int))
            for a in grup:
                v = a.get(g)
                if isinstance(v, int) and degerler:
                    az, esit = bisect_left(degerler, v), bisect_right(degerler, v) - bisect_left(degerler, v)
                    a[f"p_{g}"] = round((az + 0.5 * esit) / len(degerler), 4)
                else:
                    a[f"p_{g}"] = None
        for a in grup:
            ps = sorted([a[f"p_{g}"] for g in GOSTERGELER if a[f"p_{g}"] is not None], reverse=True)
            a["pop_puani"] = ps[0] if ps else 0.0
            a["pop_puani2"] = ps[1] if len(ps) > 1 else 0.0


def populerlik_anahtari(a: dict):
    """Tabaka içi sıralama anahtarı: pop_puani ↓, pop_puani2 ↓, id ↑ (deterministik)."""
    return (-a.get("pop_puani", 0.0), -a.get("pop_puani2", 0.0), a["id"])


def secim(adaylar: list[dict], esik: str) -> dict:
    """Seçim kuralı (KRITERLER-TASLAK.md §5):
       JOSE : çekirdek 9 dil grubunun her birinden popülerlik sırasıyla en çok 2 (kota 18); kota dolmazsa
              çekirdek dışı gruplardan (C/C++ vb.) popülerlik sırasıyla, grup başına en çok 2.
       SDJWT, COSE : dil grubu başına en çok 2, popülerlik sırasıyla kotaya kadar.
       REF  : Sürüm 3 §9.2'de adı geçenler (G) önce; sonra popülerlik; kotaya kadar.
       YEDEK: (i) seçilen her dil grubunda sıradaki uygun aday (grup-içi değiştirme için);
              (ii) tabakanın genel sırasındaki ilk 2 seçilmemiş uygun aday (grup dışı değiştirme için)."""
    uygun = [a for a in adaylar if a[f"uygun_{esik}"]]
    sonuc = {}
    for tabaka, kota in KOTALAR.items():
        havuz = sorted([a for a in uygun if a["tabaka"] == tabaka], key=populerlik_anahtari)
        secilen = []
        sayac = {}
        if tabaka == "REF":
            havuz = sorted(havuz, key=lambda a: (0 if "G" in (a.get("kaynak") or "").split("+") else 1,) + populerlik_anahtari(a))
            secilen = havuz[:kota]
        else:
            gecisler = ([lambda g: g in CEKIRDEK_GRUPLAR, lambda g: g not in CEKIRDEK_GRUPLAR] if tabaka == "JOSE"
                        else [lambda g: True])
            for uygun_mu in gecisler:
                for a in havuz:
                    if len(secilen) >= kota:
                        break
                    g = dil_grubu(a["dil_anahtari"])
                    if a not in secilen and uygun_mu(g) and sayac.get(g, 0) < 2:
                        secilen.append(a)
                        sayac[g] = sayac.get(g, 0) + 1
        kalan = [a for a in havuz if a not in secilen]
        yedek = []
        if tabaka != "REF":
            for g in dict.fromkeys(dil_grubu(a["dil_anahtari"]) for a in secilen):
                aday = next((a for a in kalan if dil_grubu(a["dil_anahtari"]) == g), None)
                if aday and aday not in yedek:
                    yedek.append(aday)
        genel = 0
        for a in kalan:
            if genel >= 2:
                break
            if a not in yedek:
                yedek.append(a)
                genel += 1
        sonuc[tabaka] = {"uygun": len(havuz), "secilen": [a["id"] for a in secilen], "yedek": [a["id"] for a in yedek]}
    return sonuc


# ---------------------------------------------------------------------------
# 5) (İsteğe bağlı) DESEN TARAMASI — elle doğrulama için ipucu; hüküm değildir
# ---------------------------------------------------------------------------
DESENLER = {
    "ml_dsa": r"ML[-_]?DSA|MLDSA|\bAKP\b|Dilithium|dilithium",
    "composite": r"ML-?DSA-?(44|65|87)-(ES256|ES384|Ed25519|Ed448|RS256|PS256)|MLDSA(44|65|87)[-_]?(ES256|ES384|Ed25519|Ed448)|pq-composite|composite[-_ ]sig",
    "general_json": r"GeneralJWS|general[_ -]?json|JSON[ _-]?[Ss]erializ|\"signatures\"|'signatures'|deserialize_json|GeneralSign|generalVerify|JWSObjectJSON|JsonSerialization|serialize_json|VerifyMulti|verifyMulti|multi-?signature|multiple signatures|GeneralJson|JSONGeneral|general_serialization|signatureIndex|signature_index",
    "alg_izin": r"allowed[_ ]?alg|allowedAlg|AllowedAlg|algorithms\s*[:=]|acceptedAlg|AlgorithmPolicy|alg(orithm)?[_ ]?(allow|white)list|ValidAlgorithms|valid_algorithms|allowed_algorithms|JWSAlgorithm\.Family|WithValidMethods|ValidMethods|expectedAlg|AlgorithmConstraints|allowedAlgorithms|validAlgorithms|allowed_algs|setAllowedAlgorithms|WithAcceptableAlgorithms|SignatureAlgorithm\[\]|\[\]jose\.SignatureAlgorithm|algorithms=",
    "anahtar_alg": r"key\.alg\b|key_alg|keyAlg|\.alg\s*!==?|alg\s*!==?\s*\w*key|alg(orithm)?\s*mismatch|does not match.*alg|JWSVerificationKeySelector|checkKeyType|checkSigCryptoKey|InvalidKeyAlgorithm|incompatible.*key|key.*incompatible|algorithm_name|KeyAlgorithm|alg.*not.*allowed.*key|WithKey\(",
    "sd_jwt": r"SD-JWT|sd_jwt|SdJwt|sdjwt|_sd_alg|Disclosure",
    "cose_sign": r"COSE_Sign\b|CoseSign\b|CoseSignMessage|COSE_Sign[^1]|SignMessage|CoseMultiSign|tag\s*=\s*98\b|Sign\s*=\s*98\b|MultiSign",
}
TARANACAK_UZANTI = {".js", ".mjs", ".cjs", ".ts", ".py", ".java", ".kt", ".kts", ".go", ".rs", ".cs", ".php", ".rb", ".swift",
                    ".c", ".h", ".cc", ".cpp", ".hpp", ".md", ".rst", ".adoc", ".txt", ".dart", ".scala", ".ex", ".exs", ".erl"}


def desen_tara(aday: dict) -> dict:
    """Sığ klonda (derinlik 1) desen eşleşmelerini dosya:satır olarak toplar. Klon sonra silinir."""
    onb = ONBELLEK / "tarama" / f"{aday['id']}.json"
    if onb.exists() and not ARGS.tazele:
        return json.loads(onb.read_text("utf-8"))
    if ARGS.cevrimdisi or not aday.get("depo_url"):
        return {}
    hedef = Path(ARGS.klon_dizini) / "tarama" / aday["id"]
    shutil.rmtree(hedef, ignore_errors=True)
    hedef.parent.mkdir(parents=True, exist_ok=True)
    sonuc = {"depo": aday["depo_url"], "desenler": {}}
    try:
        komut = GIT_ANONIM + ["clone", "--quiet", "--depth", "1", "--filter=blob:limit=2m"]
        if aday.get("alt_dizin"):
            komut += ["--sparse"]
        komut += [aday["depo_url"].rstrip("/") + ".git", str(hedef)]
        r = subprocess.run(komut, capture_output=True, text=True, timeout=900, env=GIT_ORTAM)
        if r.returncode != 0:
            sonuc["hata"] = r.stderr.strip()[:300]
        else:
            if aday.get("alt_dizin"):
                subprocess.run(GIT_ANONIM + ["-C", str(hedef), "sparse-checkout", "set", aday["alt_dizin"]], capture_output=True, timeout=600, env=GIT_ORTAM)
            sonuc["sha"] = subprocess.run(GIT_ANONIM + ["-C", str(hedef), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
            kok = hedef / aday["alt_dizin"] if aday.get("alt_dizin") else hedef
            derlenmis = {k: re.compile(v) for k, v in DESENLER.items()}
            dosyalar = []
            for yol in kok.rglob("*"):
                if not yol.is_file() or yol.suffix.lower() not in TARANACAK_UZANTI:
                    continue
                if any(p in {".git", "node_modules", "vendor", "dist", "build", "target"} for p in yol.parts):
                    continue
                goreli = str(yol.relative_to(hedef)).replace("\\", "/")
                gl = goreli.lower()
                # öncelik: 0 kaynak, 1 belge, 2 test/örnek (kanıt için kaynak ve belge önce gelsin)
                if re.search(r"(^|/)(tests?|spec|__tests__|testdata|test-vectors?|fixtures?|examples?|samples?|benchmarks?)(/|$)|_test\.|\.test\.|\.spec\.|test_", gl):
                    o = 2
                elif yol.suffix.lower() in {".md", ".rst", ".adoc", ".txt"}:
                    o = 1
                else:
                    o = 0
                dosyalar.append((o, goreli, yol))
            toplam = {}
            for o, goreli, yol in sorted(dosyalar):
                try:
                    satirlar = yol.read_text("utf-8", errors="ignore").splitlines()
                except Exception:
                    continue
                for no, s in enumerate(satirlar, 1):
                    for ad, rx in derlenmis.items():
                        if rx.search(s):
                            toplam[ad] = toplam.get(ad, 0) + 1
                            lst = sonuc["desenler"].setdefault(ad, [])
                            if len(lst) < 120:
                                lst.append(f"{goreli}:{no}: {s.strip()[:180]}")
            sonuc["sayilar"] = toplam
            sonuc["dosya_sayisi"] = len(dosyalar)
    except Exception as e:
        sonuc["hata"] = str(e)[:300]
    finally:
        shutil.rmtree(hedef, ignore_errors=True)
    onb.parent.mkdir(parents=True, exist_ok=True)
    onb.write_text(json.dumps(sonuc, ensure_ascii=False, indent=1), "utf-8")
    return sonuc


# ---------------------------------------------------------------------------
# ANA AKIŞ
# ---------------------------------------------------------------------------
DESTEK_ALANLARI = ["general_json_coklu_imza", "coklu_imza_semantigi_belgelenmis", "alg_izin_listesi", "anahtar_alg_baglama",
                   "ml_dsa_rfc9964", "composite_destegi", "sd_jwt", "cose_sign_coklu"]


def main():
    global ARGS
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cevrimdisi", action="store_true")
    ap.add_argument("--tazele", action="store_true")
    ap.add_argument("--desen-tara", action="store_true", help="adayların sığ klonlarında desen taraması (ipucu)")
    ap.add_argument("--desen-kapsam", default="secilen+yedek", choices=["secilen+yedek", "uygun", "hepsi"])
    ap.add_argument("--klon-dizini", default=str(Path(tempfile.gettempdir()) / "pq-oid4vc-envanter-klon"))
    ap.add_argument("--esik", default="E2", choices=list(ESIKLER))
    ap.add_argument("--yalniz-tarama", action="store_true", help="tanımlama+tarama sonrası dur (TARAMA.csv)")
    ARGS = ap.parse_args()
    ONBELLEK.mkdir(parents=True, exist_ok=True)

    # 1) Tanımlama
    log("1) Tanımlama …")
    jwt_adaylar, jwt_ozet = jwtio_adaylari()
    isabetler = arama_isabetleri()
    # 2) Tarama
    log("2) Tarama …")
    tarama_satirlari, ek_adaylar = tarama(jwt_adaylar, isabetler)
    csv_yaz(KOK / "TARAMA.csv", tarama_satirlari,
            ["anahtar", "kaynaklar", "sorgular", "paketler", "yildiz_ham", "indirme_ham", "aciklama", "karar", "tabaka", "gerekce"])
    incelenecek = [s["anahtar"] for s in tarama_satirlari if s["karar"] == "INCELENECEK"]
    if incelenecek:
        log(f"  ! {len(incelenecek)} isabetin tarama kararı yok: {incelenecek[:20]}")
    if ARGS.yalniz_tarama:
        log(f"   jwt.io: {jwt_ozet}; isabet: {len(isabetler)}; tarama satırı: {len(tarama_satirlari)}; ek aday: {len(ek_adaylar)}")
        return
    adaylar = jwt_adaylar + ek_adaylar
    # kimlik
    sayac = {}
    for a in adaylar:
        onek = {"JOSE": "JOSE", "SDJWT": "SDJWT", "COSE": "COSE", "REF": "REF"}[a["tabaka"]]
        sayac[onek] = sayac.get(onek, 0) + 1
        a["id"] = f"{onek}-{sayac[onek]:03d}"
    # elle bayraklar (K1/K3/K4/K6/K8) ve destek kanıtları
    elle = {r["id_ya_da_depo"].strip().lower(): r for r in csv_oku(KOK / "elle_bayraklar.csv")}
    kanit = {}
    for r in csv_oku(KOK / "destek_kanitlari.csv"):
        kanit.setdefault(r["depo"].strip().lower(), {})[r["alan"].strip()] = r

    # 3) Meta veri
    log("3) Meta veri …")
    for i, a in enumerate(adaylar, 1):
        if i % 20 == 0:
            log(f"   {i}/{len(adaylar)}")
        rm = repo_meta(a["depo"]) if a.get("depo") else {}
        gm = git_bas(a["depo_url"], a["depo"] or a["id"]) if a.get("depo_url") else {}
        pm = paket_meta(a.get("paket_ekosistemi"), a.get("paket_adi"))
        a["yildiz"] = rm.get("dd_yildiz") if isinstance(rm.get("dd_yildiz"), int) else rm.get("eco_yildiz")
        a["yildiz_kaynagi"] = "deps.dev" if isinstance(rm.get("dd_yildiz"), int) else ("ecosyste.ms" if rm.get("eco_yildiz") is not None else "")
        if a["depo"].startswith("bitbucket.org/"):
            a["yildiz"], a["yildiz_kaynagi"] = None, "bitbucket (yıldız yok)"
        a["son_commit"] = (gm.get("commit_tarihi") or rm.get("bb_son_commit") or "")[:10]
        a["son_commit_sha"] = gm.get("sha") or rm.get("bb_son_sha") or ""
        a["son_commit_kaynagi"] = "git HEAD (varsayılan dal)" if gm.get("commit_tarihi") else ("bitbucket API" if rm.get("bb_son_commit") else "")
        if not a["son_commit"] and rm.get("eco_push"):
            a["son_commit"] = str(rm["eco_push"])[:10]
            a["son_commit_kaynagi"] = "ecosyste.ms pushed_at (yedek)"
        a["arsiv"] = rm.get("eco_arsiv")
        a["fork"] = rm.get("eco_fork")
        a["kanonik_ad"] = rm.get("eco_tam_ad") or rm.get("gh_tam_ad") or ""
        a["depo_dili"] = rm.get("eco_dil") or ""
        a["lisans"], a["lisans_kaynagi"] = lisans_sec([("deps.dev", rm.get("dd_lisans")), ("ecosyste.ms", rm.get("eco_lisans")),
                                                       ("paket kaydı", pm.get("paket_lisans"))])
        a["openssf"] = rm.get("dd_openssf")
        a["son_surum"] = pm.get("son_surum", "")
        a["son_surum_tarihi"] = pm.get("son_surum_tarihi", "")
        a["aylik_indirme"] = pm.get("aylik_indirme") if isinstance(pm.get("aylik_indirme"), int) else None
        a["indirme_kaynagi"] = pm.get("indirme_kaynagi", "") if a["aylik_indirme"] is not None else ""
        a["toplam_indirme"] = pm.get("toplam_indirme")
        a["bagimli_paket"] = pm.get("bagimli_paket") if isinstance(pm.get("bagimli_paket"), int) else None
        a["bagimli_depo"] = pm.get("bagimli_depo")
        a["paket_durum"] = pm.get("paket_durum") or ("abandoned" if pm.get("packagist_terk") else "")
        e = elle.get(a["depo"]) or elle.get(a["id"].lower()) or {}
        for k in ("k1_elle", "k3_elle", "k4_elle", "k6_elle", "k8_elle", "linux_notu", "not_elle", "yildiz_elle"):
            if e.get(k):
                a[k] = e[k]
        if e.get("yildiz_elle") == "kullanma":
            # birim, alanı başka olan büyük bir platform tek-deposunun küçük bir bileşeni: depo yıldızı birimi temsil etmez
            a["yildiz_depo"] = a["yildiz"]
            a["yildiz"], a["yildiz_kaynagi"] = None, f"kullanılmadı (tek-depo; depo ★{a['yildiz_depo']})"
        elif e.get("yildiz_elle") and a["yildiz"] is None:
            a["yildiz"] = int(e["yildiz_elle"])
            a["yildiz_kaynagi"] = "elle (bkz. elle_bayraklar.csv)"
        if e.get("lisans_elle"):
            a["lisans"], a["lisans_kaynagi"] = e["lisans_elle"], "elle (bkz. elle_bayraklar.csv)"
        kk = kanit.get(a["depo"], {})
        for alan in DESTEK_ALANLARI:
            r = kk.get(alan)
            a[alan] = r["deger"] if r else "belirsiz"
            a[alan + "_dayanak"] = r["dayanak"] if r else "incelenmedi"
        a["linux_konteyner_derleme"] = "test edilecek"

    # 4) Ölçütler
    log("4) Ölçütler …")
    populerlik_puanla(adaylar)
    for esik in ESIKLER:
        for a in adaylar:
            ok, neden = olcutleri_uygula(a, esik)
            a[f"uygun_{esik}"] = ok
            a[f"neden_{esik}"] = " | ".join(neden)
    secimler = {esik: secim(adaylar, esik) for esik in ESIKLER}
    for a in adaylar:
        for esik in ESIKLER:
            t = secimler[esik][a["tabaka"]]
            a[f"karar_{esik}"] = "SECILDI" if a["id"] in t["secilen"] else ("YEDEK" if a["id"] in t["yedek"] else
                                                                            ("uygun-disarida" if a[f"uygun_{esik}"] else "DISLANDI"))

    # 5) (isteğe bağlı) desen taraması
    if ARGS.desen_tara:
        log("5) Desen taraması …")
        for a in adaylar:
            k = a[f"karar_{ARGS.esik}"]
            if ARGS.desen_kapsam == "secilen+yedek" and k not in ("SECILDI", "YEDEK"):
                continue
            if ARGS.desen_kapsam == "uygun" and not a[f"uygun_{ARGS.esik}"]:
                continue
            s = desen_tara(a)
            log(f"   {a['id']} {a['ad']}: {s.get('sayilar') or s.get('hata')}")

    # Çıktılar
    log("6) Çıktılar …")
    for a in adaylar:
        a["dil_grubu"] = dil_grubu(a["dil_anahtari"])
        a["jwtio_dilleri"] = ",".join(a.get("jwtio_dilleri") or [])
        a["not"] = "; ".join(x for x in [a.get("not_esleme"), a.get("not_elle"), a.get("linux_notu"),
                                          ("paket durumu: " + a["paket_durum"]) if a.get("paket_durum") else "",
                                          ("fork" if a.get("fork") else "")] if x)
        a["olcut_sonucu"] = a[f"karar_{ARGS.esik}"]
        a["dislama_nedeni"] = a[f"neden_{ARGS.esik}"]
    cerceve_alanlari = (["id", "tabaka", "ad", "dil", "dil_grubu", "paket_ekosistemi", "paket_adi", "depo_url", "alt_dizin",
                         "kaynak", "kaynak_ayrinti",
                         "yildiz", "yildiz_kaynagi", "son_commit", "son_commit_sha", "son_commit_kaynagi", "son_surum", "son_surum_tarihi",
                         "lisans", "lisans_kaynagi", "aylik_indirme", "indirme_kaynagi", "toplam_indirme", "bagimli_paket", "bagimli_depo",
                         "openssf", "arsiv", "pop_puani", "p_yildiz", "p_aylik_indirme", "p_bagimli_paket", "p_toplam_indirme_yalniz",
                         "jwtio_asimetrik", "jwtio_ml_dsa"]
                        + [x for alan in DESTEK_ALANLARI for x in (alan, alan + "_dayanak")]
                        + ["linux_konteyner_derleme", "olcut_sonucu", "dislama_nedeni", "not"])
    csv_yaz(KOK / "CERCEVE.csv", adaylar, cerceve_alanlari)
    secim_alanlari = ["id", "tabaka", "ad", "dil_grubu", "yildiz", "aylik_indirme", "bagimli_paket", "pop_puani", "pop_puani2",
                      "son_commit", "lisans", "lisans_kaynagi"] + \
                     [x for e in ESIKLER for x in (f"uygun_{e}", f"karar_{e}", f"neden_{e}")]
    csv_yaz(KOK / "SECIM.csv", adaylar, secim_alanlari)
    # eşik duyarlılığı
    duy = []
    for esik, s in secimler.items():
        satir = {"esik": esik, "tanim": ESIKLER[esik]["_ad"]}
        top_u, top_s = 0, 0
        for t in KOTALAR:
            satir[f"{t}_uygun"] = s[t]["uygun"]
            satir[f"{t}_secilen"] = len(s[t]["secilen"])
            if t == "REF":
                continue  # ÖK §2A Ö6: referans doğrulayıcılar n'nin DIŞINDA, ayrı raporlanır
            top_u += s[t]["uygun"]
            top_s += len(s[t]["secilen"])
        satir["toplam_uygun"] = top_u
        satir["toplam_secilen"] = top_s
        satir["n_25_40_icinde"] = "evet" if 25 <= top_s <= 40 else "hayır"
        # sayım (kota yok) seçeneği: uygun olanların hepsi
        satir["sayim_n"] = top_u
        satir["sayim_25_40_icinde"] = "evet" if 25 <= top_u <= 40 else "hayır"
        idx = {a["id"]: a for a in adaylar}
        satir["jose_cekirdek_grup_uygun"] = len({dil_grubu(a["dil_anahtari"]) for a in adaylar
                                                 if a["tabaka"] == "JOSE" and a[f"uygun_{esik}"]} & set(CEKIRDEK_GRUPLAR))
        satir["jose_cekirdek_grup_secilen"] = len({dil_grubu(idx[i]["dil_anahtari"]) for i in s["JOSE"]["secilen"]} & set(CEKIRDEK_GRUPLAR))
        satir["pilot_secilen"] = ",".join(sorted(idx[i]["ad"] for t in KOTALAR for i in s[t]["secilen"]
                                                 if "P" in (idx[i].get("kaynak") or "").split("+")
                                                 or idx[i]["depo"] in PILOT_DEPOLARI))
        duy.append(satir)
    csv_yaz(KOK / "ESIK-DUYARLILIK.csv", duy, ["esik", "tanim"] + [f"{t}_{x}" for t in KOTALAR for x in ("uygun", "secilen")] +
            ["toplam_uygun", "toplam_secilen", "n_25_40_icinde", "sayim_n", "sayim_25_40_icinde",
             "jose_cekirdek_grup_uygun", "jose_cekirdek_grup_secilen", "pilot_secilen"])
    kayit = {"calisma_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "ref_tarih": REF_TARIH.isoformat(),
             "etkinlik_siniri": ETKINLIK_SINIRI.isoformat(), "jwtio_commit": JWTIO_COMMIT, **jwt_ozet,
             "arama_isabeti": len(isabetler), "tarama_satiri": len(tarama_satirlari),
             "tarama_kararlari": {k: sum(1 for s in tarama_satirlari if s["karar"] == k) for k in sorted({s["karar"] for s in tarama_satirlari})},
             "aday": len(adaylar), "aday_tabaka": {t: sum(1 for a in adaylar if a["tabaka"] == t) for t in KOTALAR},
             "secim": secimler, "python": sys.version.split()[0]}
    (KOK / "topla_kayit.json").write_text(json.dumps(kayit, ensure_ascii=False, indent=1), "utf-8")
    log(json.dumps({k: kayit[k] for k in ("aday", "aday_tabaka", "tarama_kararlari")}, ensure_ascii=False))
    for esik in ESIKLER:
        log(esik, {t: (secimler[esik][t]["uygun"], len(secimler[esik][t]["secilen"])) for t in KOTALAR})


if __name__ == "__main__":
    main()
