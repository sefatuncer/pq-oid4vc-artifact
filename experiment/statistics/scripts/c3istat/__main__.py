"""Command line.

  python -m c3istat surum
  python -m c3istat dogrula --girdi GIRDI [--vakalar VAKALAR.csv]
  python -m c3istat analiz  --girdi GIRDI --cikti DIZIN [--vakalar VAKALAR.csv]

Exit codes: 0 ok · 2 the two implementations disagree (analysis invalid) · 3 input could not be validated.
"""
from __future__ import annotations

import argparse
import json
import sys

from . import __version__, analiz, sema, yapilandirma


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="c3istat")
    alt = ap.add_subparsers(dest="komut", required=True)
    alt.add_parser("surum")
    d = alt.add_parser("dogrula")
    d.add_argument("--girdi", required=True)
    d.add_argument("--vakalar")
    a = alt.add_parser("analiz")
    a.add_argument("--girdi", required=True)
    a.add_argument("--cikti", required=True)
    a.add_argument("--vakalar")
    arg = ap.parse_args(argv)

    if arg.komut == "surum":
        print(json.dumps({"surumler": analiz._surumler(), "betik_sha256": analiz._betik_ozetleri(),
                          "yapilandirma": yapilandirma.ozet()}, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if arg.komut == "dogrula":
        try:
            g = sema.yukle(arg.girdi, arg.vakalar)
        except sema.GirdiHatasi as e:
            print(json.dumps({"gecerli": False, "hatalar": e.mesajlar}, ensure_ascii=False, indent=2))
            return 3
        print(json.dumps({"gecerli": True, "hedef": len(g.hedefler), "vaka": len(g.vakalar), "kaynak": g.kaynak},
                         ensure_ascii=False, indent=2))
        return 0
    return analiz.calistir(arg.girdi, arg.cikti, arg.vakalar)


if __name__ == "__main__":
    sys.exit(main())
