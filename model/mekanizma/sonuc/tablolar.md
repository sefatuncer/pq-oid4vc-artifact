# Adım 7 sonuç tabloları (otomatik; `betik/tablolar.py`)

Hücre: gözlenen hüküm. **X≠Y**: gözlenen X, çapa 8 beklentisi Y. Exists-trace lemmada V = iz var.

## 1. İstek yönü ve meta veri (G5 biçimleri)

| Mekanizma | Varyant | zamansız | göç | zamanlı | NR | FCD | G1/G4 | M_downgrade_s1 | M_forgery_crqc |
|---|---|---|---|---|---|---|---|---|---|
| M-b0 | `MB0_taban` | F | F | F | V | V | F | F | V |
| M-a | `MA_taban` | F | F | F | V | V | F | V | V |
| M-b / A.3.2.2 | `MB_taban` | F | F | F | V | V | F | V | V |
| M-e (PQ imzalı, taze) | `ME_signed_fresh` | F | F | V | **F≠V** | V | F | V | V |
| M-e′ (PQ imzalı, taze) | `MEP_signed_fresh` | V | V | V | **F≠V** | F | V | F | F |
| M-e′ (imzasız, klasik TLS) | `MEP_tls_classical` | F | F | F | F | V | F | F | V |
| M-d (PQ kayıt kanalı) | `MD_reg_pq` | V | F | F | F | V | F | V | V |

## 2. M-f çekirdeği ve görev 3b (kapsam × saldırı)

| Hücre | Varyant | G5 zamansız | göç | zamanlı | NR | G1 | yol zamansız | yol göç | yol zamanlı | yol NR | M_weak_path_forgery |
|---|---|---|---|---|---|---|---|---|---|---|---|
| çekirdek (üç saldırı) | `MF_cekirdek` | V | V | V | V | V | V | V | V | V | F |
| yol_sinifi × farklı adlı CA | `MF_3b_yol_farkli_ad` | V | V | V | V | V | V | V | V | V | F |
| yol_sinifi × aynı adlı CA | `MF_3b_yol_ayni_ad` | V | V | V | V | V | V | V | V | V | F |
| yol_sinifi × klasik kök + PQ ara | `MF_3b_yol_klasik_kok` | V | V | V | V | V | V | V | V | V | F |
| anahtar × farklı adlı CA | `MF_3b_anahtar_farkli_ad` | V | V | V | V | V | F | F | F | F | F |
| anahtar × aynı adlı CA | `MF_3b_anahtar_ayni_ad` | V | V | V | V | V | F | F | F | F | F |
| anahtar × klasik kök + PQ ara | `MF_3b_anahtar_klasik_kok` | V | V | V | V | V | F | F | F | F | F |
| yaprak_alg × farklı adlı CA | `MF_3b_yaprak_farkli_ad` | V | V | V | V | F | F | F | F | F | V |
| yaprak_alg × aynı adlı CA | `MF_3b_yaprak_ayni_ad` | V | V | V | V | F | F | F | F | F | V |
| yaprak_alg × klasik kök + PQ ara | `MF_3b_yaprak_klasik_kok` | V | V | V | V | F | F | F | F | F | V |

## 3. Taşıyıcı ikamesi (A3-7)

| Taşıyıcı | Varyant | zamansız | göç | zamanlı | NR | FCD | G1 | yol zamansız | yol göç | yol zamanlı | yol NR | M_downgrade_s1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TL/LoTE çekilen-güncel | `MF_cekirdek` | V | V | V | V | F | V | V | V | V | V | F |
| TL/LoTE önbellek | `MF_tas_tl_onbellek` | V | F | F | F | V | F | V | F | F | F | V |
| WRPRC faz0 | `MF_tas_wrprc_faz0` | F | F | F | F | V | F | F | F | F | F | V |
| WRPRC faz1 | `MF_tas_wrprc_faz1` | V | F | F | F | V | F | V | F | F | F | V |
| OpenID Federation (PQ ara) | `MF_tas_federasyon_pq` | V | V | V | V | F | V | V | V | V | V | F |
| OpenID Federation (klasik ara) | `MF_tas_federasyon_klasik_ara` | F | F | F | F | V | F | F | F | F | F | F |
| OpenID Federation (trust_chain/önbellek) | `MF_tas_federasyon_bayat` | V | F | F | F | V | F | V | F | F | F | V |
| crit başlığı | `MF_tas_crit_baslik` | F | F | F | F | V | F | F | F | F | F | V |

## 4. M-h (reddy, vicente) ve görev 3a

| Hücre | Varyant | zamansız | göç | zamanlı | NR | FCD | G1_learned | G1_learned_pq | G1_learned_pq_genuine | no_rollback_path | M_downgrade_s1 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| reddy, klasik zincir (3a-i) | `MH_reddy_klasik_zincir` | F | F | F | V | V | F | F | — | F | V |
| reddy × farklı adlı CA | `MH_reddy_farkli_ad` | F | F | F | V | V | F | F | — | F | V |
| reddy × aynı adlı CA | `MH_reddy_ayni_ad` | F | F | F | V | V | F | F | — | F | V |
| reddy × klasik kök | `MH_reddy_klasik_kok` | F | F | F | V | V | F | F | — | F | V |
| reddy + ad bağlama × farklı adlı CA | `MH_reddy_adbag_farkli_ad` | F | F | F | V | V | F | F | — | F | V |
| vicente, klasik zincir (3a-i) | `MH_vicente_klasik_zincir` | F | F | F | F | V | F | F | V | F | V |
| vicente × farklı adlı CA | `MH_vicente_farkli_ad` | F | F | F | F | V | F | F | V | F | V |
| vicente × aynı adlı CA | `MH_vicente_ayni_ad` | F | F | F | F | V | F | F | V | F | V |
| vicente × klasik kök | `MH_vicente_klasik_kok` | F | F | F | F | V | F | F | V | F | V |

## 5. EK: M-g (sheffer) zincir politikası okumaları × 3b

| Hücre | Varyant | zamansız | göç | zamanlı | NR | FCD | G1_learned | G1_learned_pq | no_rollback_path | M_cache_cleared |
|---|---|---|---|---|---|---|---|---|---|---|
| anahtar PQ × farklı adlı CA | `EK_mg_anahtar_farkli_ad` | F | F | F | F | V | F | F | F | V |
| anahtar PQ × aynı adlı CA | `EK_mg_anahtar_ayni_ad` | F | F | F | F | V | F | F | F | V |
| anahtar PQ × klasik kök | `EK_mg_anahtar_klasik_kok` | F | F | F | F | V | F | F | F | V |
| imza PQ × farklı adlı CA | `EK_mg_imza_farkli_ad` | F | F | F | V | V | V | V | V | F |
| imza PQ × aynı adlı CA | `EK_mg_imza_ayni_ad` | F | F | F | V | V | V | V | V | F |
| imza PQ × klasik kök | `EK_mg_imza_klasik_kok` | F | F | F | V | V | V | V | V | F |

## 6. EK: yola duyarlı çevrimdışı ek (2 × 2)

| Tekdüzelik | Sunset | Varyant | zamansız | göç | zamanlı | NR | yol zamansız | yol göç | yol zamanlı | yol NR | G1 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| dar | anahtar | `EK_mf_r7_tanimlari` | V | F | V | V | V | F | F | F | F |
| geniş | anahtar | `EK_mf_monoton_genis` | V | F | V | V | V | F | F | V | F |
| dar | beklenti | `EK_mf_sunset_beklenti` | V | F | V | V | V | F | V | F | F |
| geniş | beklenti | `EK_mf_yola_duyarli` | V | F | V | V | V | F | V | V | F |
