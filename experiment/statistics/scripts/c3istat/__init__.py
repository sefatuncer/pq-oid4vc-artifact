"""c3istat — PQ-OID4VC C3 (H6) pre-registered statistics scripts (Step 9, task 9).

Modules:
- yapilandirma : constants based on the PR (α, seed, B, families, tolerances)
- kesin        : implementation A — standard library only (fractions, math.comb, decimal)
- referans     : implementation B — scipy / statsmodels / numpy
- karsilastir  : comparison of the two implementations (tolerances)
- sema         : input schema (SCHEMA.md) loading and validation
- bootstrap    : cluster bootstrap (pure Python and numpy)
- analiz       : T1–T5, Holm, effect sizes, Wilson, bootstrap, sensitivity analyses, H6 verdict
- rapor        : human-readable Markdown table
"""
__version__ = "1.0.0"
