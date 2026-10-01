# H4 reproduction in Tamarin: relying-party authentication cell (exploratory, post hoc)

The pre-registered H4 rule asks for at least one candidate cell to be reproduced by a Tamarin example.
The ASP comparison found four G4 cells (unsigned request, WRPRC phase 1) in which the "roots and devices
first" strategy S5 is insufficient, because it does not migrate the RP access certificate and the request
object, while the computed minimal strategy S7 does and conveys an authenticated per-RP expectation.

| Variant | Flags (`../../modeller/M_istek.spthy`) | G4_rp_authentication | G5 forms | Source |
|---|---|---|---|---|
| S5-like: unsigned-request fallback, no expectation | `MB0` | falsified | all falsified | `../../sonuc/ozet.csv` (`MB0_taban`, pre-registered run) |
| S7-like: unsigned-request fallback, authenticated per-RP expectation | `MB0`, `WALLET_EXPECT` | verified | all verified | `MB0_WALLET_EXPECT.txt` (this folder; run 2026-10-01) |

Under pre-registration amendment 8 (item 3), these four G4 cells were redefined after the result and do
not count for the H4 verdict or the scientific gate. They are reported as exploratory. The second variant
was not part of the pre-registered run set either. Command (Tamarin 1.12.0, image `pq-a02-tamarin:1.12.0`, memory limit 4 GB):

    tamarin-prover --derivcheck-timeout=60 -D=MB0 -D=WALLET_EXPECT --prove modeller/M_istek.spthy

All well-formedness checks passed; processing time 2.0 s.
