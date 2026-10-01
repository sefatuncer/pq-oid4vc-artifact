<!-- ozet_tablolari.py tarafindan uretildi; elle degistirmeyin -->
Toplam satır: **400**; belge sayısı (matriste geçen): **39**

### T1. Artefakt × belge grubu (satır sayısı)

| Artefakt | OIDF | IETF-OAuth | IETF-JOSE | IETF-COSE | IETF-PQUIP | IETF-LAMPS | ARF | ETSI | AB-rehber | BCT | Akademik | Toplam |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A01 LOTL | · | · | · | · | 1 | · | · | 5 | 1 | · | · | 7 |
| A02 TL/LoTE | 2 | · | · | · | · | · | 6 | 21 | · | · | · | 29 |
| A03 CA (x5c zinciri) | 3 | · | 4 | 3 | · | 5 | 1 | 1 | · | · | · | 17 |
| A04 ihraççı sertifikası | 4 | 5 | 2 | 2 | · | · | 1 | 1 | · | · | 1 | 16 |
| A05 imzalı ihraççı meta verisi | 20 | · | · | · | · | · | 1 | · | · | · | · | 21 |
| A06 Type Metadata | · | 11 | · | · | · | · | · | · | · | · | · | 11 |
| A07 kimlik bilgisi (SD-JWT VC) | 7 | 18 | 1 | · | · | · | 5 | · | · | · | · | 31 |
| A08 durum listesi belirteci | 4 | 25 | · | · | · | · | 6 | 1 | · | · | · | 36 |
| A09 cüzdan kanıtlaması (WUA: WIA/KA) | 12 | 21 | · | · | · | · | 9 | · | · | · | · | 42 |
| A10 WSCD anahtarı ve KB-JWT | 18 | 9 | · | · | · | · | 4 | · | · | · | · | 31 |
| A11 RP erişim/kayıt sertifikası | 10 | · | · | · | · | · | 14 | 5 | · | · | · | 29 |
| A12 OID4VP istek nesnesi | 36 | · | · | · | · | · | 1 | · | · | · | · | 37 |
| A13 taşıma (TLS/WebPKI) | 5 | 5 | 3 | · | · | · | · | · | · | · | 1 | 14 |
| genel | 11 | 7 | 25 | 5 | 7 | · | · | 4 | 10 | 10 | · | 79 |
| **Toplam** | 132 | 101 | 35 | 10 | 8 | 5 | 48 | 38 | 11 | 10 | 2 | 400 |

### T2. Artefakt × kanal (satır sayısı)

| Artefakt | aktarilan | cekilen | sabitlenmis | belirsiz |
|---|---|---|---|---|
| A01 LOTL | 0 | 3 | 3 | 1 |
| A02 TL/LoTE | 0 | 28 | 1 | 0 |
| A03 CA (x5c zinciri) | 14 | 1 | 1 | 1 |
| A04 ihraççı sertifikası | 13 | 1 | 1 | 1 |
| A05 imzalı ihraççı meta verisi | 1 | 20 | 0 | 0 |
| A06 Type Metadata | 1 | 7 | 1 | 2 |
| A07 kimlik bilgisi (SD-JWT VC) | 29 | 0 | 0 | 2 |
| A08 durum listesi belirteci | 1 | 33 | 0 | 2 |
| A09 cüzdan kanıtlaması (WUA: WIA/KA) | 36 | 5 | 0 | 1 |
| A10 WSCD anahtarı ve KB-JWT | 28 | 1 | 0 | 2 |
| A11 RP erişim/kayıt sertifikası | 23 | 3 | 1 | 2 |
| A12 OID4VP istek nesnesi | 33 | 1 | 0 | 3 |
| A13 taşıma (TLS/WebPKI) | 6 | 7 | 1 | 0 |
| genel | 1 | 3 | 1 | 74 |

### T2b. Kanal dayanak satırları (artefakt başına, kanal sınıfına göre id'ler)

- **A01 LOTL** — cekilen: T001, T002, T003 · sabitlenmis: T004, T005, T007 · belirsiz: T006
- **A02 TL/LoTE** — cekilen: T008, T009, T010, T011, T012, T013, T014, T015, T016, T017, T018, T019, T020, T021, T022, T023, T024, T025, T027, T028, T030, T031, T032, T033, T034, T035, T036, T037 · sabitlenmis: T029
- **A03 CA (x5c zinciri)** — aktarilan: T038, T040, T043, T050, T051, T052, T053, T054, T055, T056, T058, T060, T061, T065 · cekilen: T063 · sabitlenmis: T069 · belirsiz: T128
- **A04 ihraççı sertifikası** — aktarilan: T039, T041, T042, T044, T045, T046, T047, T057, T059, T062, T064, T066, T068 · sabitlenmis: T067 · belirsiz: T111 · cekilen: T310
- **A05 imzalı ihraççı meta verisi** — cekilen: T070, T071, T072, T073, T074, T075, T076, T077, T078, T079, T080, T081, T082, T083, T085, T086, T087, T393, T394, T398 · aktarilan: T084
- **A06 Type Metadata** — aktarilan: T090 · cekilen: T091, T092, T094, T095, T097, T098, T101 · sabitlenmis: T093 · belirsiz: T096, T099
- **A07 kimlik bilgisi (SD-JWT VC)** — aktarilan: T048, T049, T102, T103, T104, T105, T106, T107, T108, T109, T110, T112, T113, T114, T115, T116, T117, T118, T119, T120, T121, T139, T140, T141, T143, T144, T175, T333, T391 · belirsiz: T133, T142
- **A08 durum listesi belirteci** — cekilen: T026, T145, T146, T147, T148, T149, T150, T151, T152, T153, T154, T155, T156, T157, T158, T159, T160, T161, T162, T163, T164, T165, T167, T168, T170, T171, T172, T173, T174, T176, T177, T178, T180 · belirsiz: T166, T179 · aktarilan: T169
- **A09 cüzdan kanıtlaması (WUA: WIA/KA)** — aktarilan: T181, T182, T183, T184, T185, T186, T187, T191, T192, T193, T194, T195, T196, T197, T198, T199, T200, T202, T203, T204, T205, T206, T207, T208, T374, T375, T376, T377, T378, T379, T380, T382, T383, T396, T399, T400 · cekilen: T188, T189, T201, T381, T384 · belirsiz: T190
- **A10 WSCD anahtarı ve KB-JWT** — aktarilan: T209, T210, T211, T212, T213, T214, T216, T217, T218, T219, T220, T221, T222, T223, T224, T225, T227, T228, T229, T230, T231, T232, T233, T234, T235, T236, T239, T395 · belirsiz: T226, T238 · cekilen: T237
- **A11 RP erişim/kayıt sertifikası** — aktarilan: T088, T089, T240, T241, T243, T244, T246, T247, T249, T250, T251, T252, T253, T254, T257, T258, T259, T261, T262, T263, T264, T265, T267 · belirsiz: T242, T266 · cekilen: T245, T255, T260 · sabitlenmis: T256
- **A12 OID4VP istek nesnesi** — aktarilan: T248, T268, T269, T270, T271, T272, T273, T274, T276, T277, T278, T279, T280, T281, T283, T285, T286, T287, T288, T289, T291, T292, T293, T294, T296, T298, T299, T300, T387, T388, T389, T390, T397 · cekilen: T284 · belirsiz: T290, T295, T297
- **A13 taşıma (TLS/WebPKI)** — cekilen: T100, T306, T307, T308, T309, T311, T312 · aktarilan: T275, T282, T302, T303, T304, T305 · sabitlenmis: T313

### T3. Kategori / anahtar sözcük / hedef dağılımı

| Kategori | Satır |
|---|---|
| alg-muzakere | 75 |
| downgrade | 55 |
| gecerlilik | 48 |
| guven-capasi | 46 |
| diger | 33 |
| anahtar-baglama | 32 |
| tazelik | 30 |
| x5c | 23 |
| istek-imzasi | 16 |
| durum-listesi | 12 |
| kanitlama | 12 |
| dpop | 11 |
| tl-lote | 7 |

| Hedef | Satır |
|---|---|
| G1 | 187 |
| G2 | 89 |
| G3 | 65 |
| G4 | 80 |
| G5 | 115 |

| Anahtar sözcük (baskın) | Satır |
|---|---|
| MUST | 133 |
| bilgi/diğer | 124 |
| SHALL | 49 |
| SHOULD | 30 |
| MUST NOT | 26 |
| MAY | 11 |
| OPTIONAL | 9 |
| RECOMMENDED | 8 |
| REQUIRED | 7 |
| SHALL NOT | 3 |

### T4. Artefakt başına kaynak belgeler

- **A01 LOTL** (7): PQCRM×1, RFC9955×1, TS119612×5
- **A02 TL/LoTE** (29): ARF-A202×3, ARF-M06×3, HAIP×1, OID4VP×1, TS119312×3, TS119602×7, TS119612×11
- **A03 CA (x5c zinciri)** (17): ARF-M06×1, HAIP×2, JOSECOMP×2, LAMPSCOMP×5, OID4VP×1, RFC7515×2, RFC9360×3, TS119312×1
- **A04 ihraççı sertifikası** (16): ARF-M06×1, HAIP×3, HAUCK25×1, JOSECOMP×1, OID4VCI×1, RFC7515×1, RFC9360×2, RFC9901×1, SDJWTVC×4, TS119312×1
- **A05 imzalı ihraççı meta verisi** (21): ARF-M06×1, HAIP×5, OID4VCI×15
- **A06 Type Metadata** (11): SDJWTVC×11
- **A07 kimlik bilgisi (SD-JWT VC)** (31): ARF-A202×4, ARF-M06×1, HAIP×2, JWTBCP×1, OID4VCI×2, OID4VP×3, RFC7519×1, RFC9901×10, SDJWTVC×5, SDJWTVC13×2
- **A08 durum listesi belirteci** (36): ARF-A202×3, ARF-M06×3, HAIP×4, SDJWTVC×3, TS119602×1, TSL×22
- **A09 cüzdan kanıtlaması (WUA: WIA/KA)** (42): ABCA×14, ARF-A202×5, ARF-M06×4, HAIP×7, OID4VCI×5, RFC9449×7
- **A10 WSCD anahtarı ve KB-JWT** (31): ARF-A202×3, ARF-M06×1, HAIP×4, OID4VCI×7, OID4VP×7, RFC9901×8, SDJWTVC×1
- **A11 RP erişim/kayıt sertifikası** (29): ARF-A202×12, ARF-M06×2, HAIP×3, OID4VP×7, TS119411-8×1, TS119475×4
- **A12 OID4VP istek nesnesi** (37): ARF-A202×1, HAIP×4, OID4VP×32
- **A13 taşıma (TLS/WebPKI)** (14): ABCA×1, HAIP×1, HAUCK25×1, JWTBCP×1, OID4VCI×2, OID4VP×2, RFC7515×2, RFC8725×1, SDJWTVC×3
- **genel** (79): ACM2×4, ACM3D×1, ENISAHYB×1, HAIP×8, JOSECOMP×3, JWTBCP×6, OID4VCI×2, OID4VP×1, PQCFAQ×2, PQCRM×2, RFC6781×4, RFC6840×5, RFC7515×8, RFC7517×2, RFC7518×1, RFC7519×1, RFC7583×1, RFC8725×4, RFC9052×3, RFC9053×2, RFC9864×3, RFC9901×1, RFC9955×7, RFC9964×3, TS119312×4

