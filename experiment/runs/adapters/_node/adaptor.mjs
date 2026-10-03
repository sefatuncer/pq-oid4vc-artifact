// C3 adapter (Node.js): JOSE-009 jose, JOSE-065 jsonwebtoken, COSE-014 cose-js, SDJWT-015 @sd-jwt/core.
// Contract: experiment/oracle/oracle-A/adapter-contract.md (1.0), experiment/runs/RUNNER.md. Does NOT see the oracle.
// ONLY `dogrulama_girdileri` is read from the MANIFEST (the field `insa` is NOT read: it is a construction fact).
// Usage: node /a/adaptor.mjs <hedef_id> <jobs-v1.3.jsonl> <cikti.jsonl> <kosu>
import { readFileSync, writeFileSync, appendFileSync } from 'node:fs';
import { createHash, webcrypto } from 'node:crypto';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const [, , HID, ISLER, CIKTI, KOSU] = process.argv;
const A = 'ES256', LEGACY = 'https://legacy-issuer.example';
const X_OF = { 'kontrol-EdDSA': 'EdDSA', 'kontrol-Ed25519': 'Ed25519', 'kontrol-ES384': 'ES384', 'tedavi-ML-DSA-65': 'ML-DSA-65', 'tedavi-composite': 'ML-DSA-65-ES256' };
const b64d = (s) => Buffer.from(s, 'base64url');
const KID = {}, ALG2KID = {};
for (const f of ['v1/acik-jwks.json', 'v1.3/acik-jwks.json']) for (const k of JSON.parse(readFileSync(`/anahtarlar/${f}`)).keys) KID[k.kid] = k;
for (const f of ['v1/roller.json', 'v1.3/roller.json']) for (const [r, d] of Object.entries(JSON.parse(readFileSync(`/anahtarlar/${f}`)).roller)) if (r.startsWith('issuer/') && !ALG2KID[d.tur]) ALG2KID[d.tur] = d.kid;
const MAN = {}; for (const v of JSON.parse(readFileSync('/v/v1.3/MANIFEST.json')).vektorler) MAN[v.id] = v.dogrulama_girdileri || {};
const hdrOf = (c) => JSON.parse(b64d(c.split('.')[0]).toString());
const issOf = (c) => { try { return JSON.parse(b64d(c.split('.')[1]).toString()).iss; } catch { return undefined; } };
const jwkFor = (h) => KID[h.kid] ?? KID[ALG2KID[h.alg] ?? ALG2KID[h.alg === 'EdDSA' ? 'Ed25519' : h.alg]];
// Configuration name of the policy: the suffixes `|sdjwtvc=…` and `@-19` only split the oracle expectation (oracle-B METHOD §2).
const temel = (p) => p.split('|')[0].split('@')[0];
function allowed(pol, X, iss, supported) {
  pol = temel(pol);
  if (['GEC', 'GEC@-19', 'P0', 'P1'].includes(pol)) return supported;
  if (pol === 'IZIN-A') return [A];
  if (pol === 'IZIN-AX') return [A, X];
  if (['L4', 'L4-S', 'L4-Y', 'L4@-19', 'L4-YOL'].includes(pol)) return iss === LEGACY ? [A, X] : [X];
  return supported;
}
function klass(e) {
  const m = `${e?.code ?? ''} ${e?.name ?? ''} ${e?.message ?? e}`.toLowerCase();
  for (const [p, c] of [['not allowed', 'alg-izin-disi'], ['disallowed', 'alg-izin-disi'], ['invalid algorithm', 'alg-izin-disi'], ['unsupported', 'alg-desteklenmiyor'],
    ['not supported', 'alg-desteklenmiyor'], ['unknown key type', 'alg-desteklenmiyor'], ['must be of type', 'alg-anahtar-uyusmazligi'], ['symmetric', 'alg-anahtar-uyusmazligi'],
    ['signature', 'imza-gecersiz'], ['missmatch', 'imza-gecersiz'], ['expired', 'zaman'], ['exp', 'zaman'], ['no key', 'anahtar-bulunamadi'], ['find signer', 'anahtar-bulunamadi'],
    ['cbor', 'ayristirma'], ['json', 'ayristirma'], ['parse', 'ayristirma']]) if (m.includes(p)) return c;
  return 'istisna-diger';
}
const SUBTLE = { ES256: { name: 'ECDSA', hash: 'SHA-256' }, EdDSA: { name: 'Ed25519' }, Ed25519: { name: 'Ed25519' }, 'ML-DSA-65': { name: 'ML-DSA-65' }, 'ML-DSA-44': { name: 'ML-DSA-44' }, 'ML-DSA-87': { name: 'ML-DSA-87' } };

const T = {
  'JOSE-009': () => {
    const jose = require('jose');
    const supported = ['ES256', 'ES384', 'ES512', 'EdDSA', 'Ed25519', 'ML-DSA-44', 'ML-DSA-65', 'ML-DSA-87', 'PS256', 'RS256'];
    const keyCache = {};
    const resolver = async (h) => { const j = jwkFor(h); if (!j) throw new Error('no key for kid/alg'); const ck = `${j.kid}|${h.alg}`; return keyCache[ck] ??= await jose.importJWK({ ...j }, h.alg); };
    return {
      ver: require('jose/package.json').version, api: 'jose.compactVerify / jose.flattenedVerify / jose.generalVerify(jws, getKey, {algorithms: W})',
      formats: new Set(['compact', 'general', 'flattened']),
      async verify(job, data, X) {
        const pol = temel(job.politika);
        if (pol === 'L4-S') return 'ifade-edilemedi';        // no option "every present signature in W and valid"
        if (job.serilestirme === 'compact') {
          const tok = data.trim();
          const r = await jose.compactVerify(tok, resolver, { algorithms: allowed(pol, X, issOf(tok), supported) });
          return [{ sira: 0, alg: r.protectedHeader.alg, sonuc: 'gecerli' }];
        }
        const j = JSON.parse(data);
        const iss = (() => { try { return JSON.parse(b64d(j.payload).toString()).iss; } catch { return undefined; } })();
        const W = allowed(pol, X, iss, supported);
        const r = j.signatures ? await jose.generalVerify(j, resolver, { algorithms: W }) : await jose.flattenedVerify(j, resolver, { algorithms: W });
        return [{ sira: -1, alg: r.protectedHeader.alg, sonuc: 'gecerli' }];   // jose reports only the first verified signature
      },
    };
  },
  'JOSE-065': () => {
    const jwt = require('jsonwebtoken');
    const supported = ['ES256', 'ES384', 'ES512', 'PS256', 'RS256'];
    return {
      ver: require('jsonwebtoken/package.json').version, api: 'jsonwebtoken.verify(token, pem, {algorithms: W})', formats: new Set(['compact']),
      async verify(job, data, X) {
        const tok = data.trim(); const h = hdrOf(tok); const j = jwkFor(h); if (!j) throw new Error('no key for kid/alg');
        const pem = (await import('node:crypto')).createPublicKey({ key: j, format: 'jwk' }).export({ type: 'spki', format: 'pem' });
        jwt.verify(tok, pem, { algorithms: allowed(job.politika, X, issOf(tok), supported), clockTimestamp: MAN[job.vektor_id].simdi ?? 1790003700 });
        return [{ sira: 0, alg: h.alg, sonuc: 'gecerli' }];
      },
    };
  },
  'COSE-014': () => {
    const cose = require('cose-js');
    const cborlib = require('cbor');
    const cosekeys = JSON.parse(readFileSync('/anahtarlar/v1.3/cose-anahtarlar.json'));
    return {
      ver: require('cose-js/package.json').version, api: 'cose.sign.verify(cbor, {key:{x,y,kid}}) (key from the message kid or alg)', formats: new Set(['COSE_Sign1', 'COSE_Sign']),
      async verify(job, data, X) {
        const pol = temel(job.politika);
        // cose-js has no option for an algorithm allow-list. L4 is expressed through its documented signer selection
        // (pre-freeze decision D8, evidence-rule second attempt).
        if (!['GEC', 'P0', 'P1', 'P2', 'L4'].includes(pol)) return 'ifade-edilemedi';
        const buf = Buffer.from(readFileSync(`/v/${job.dosya}`));
        // Verifier key (cose-js supports ES/PS/RS only; lib/sign.js AlgFromTags). For COSE_Sign1 the key is chosen
        // from the message's kid, or from its alg (-7 ES256, -35 ES384); COSE_Sign keeps the ES256 key.
        let alg = 'ES256', j = KID[ALG2KID['ES256']];
        const t = cborlib.decodeFirstSync(buf);
        // iss of the COSE payload (a CBOR map), read before verification only to select the issuer record of L4c.
        const iss = (() => { try { const p = cborlib.decodeFirstSync(t.value[2]); return p instanceof Map ? p.get('iss') : p?.iss; } catch { return undefined; } })();
        if (pol === 'L4' && iss !== LEGACY) {
          // L4 for a migrated issuer (R = {X}): cose.sign.verify checks exactly the signer whose kid equals the kid
          // of the verifier key (lib/sign.js getSigner), so the configuration is the key of the required algorithm X.
          // A legacy issuer (payload iss = LEGACY: W = {A, X}, R empty) keeps the key resolution below.
          const kx = KID[ALG2KID[X]];
          if (!kx || kx.kty !== 'EC') throw new Error(`unsupported algorithm ${X} for cose-js`);
          j = kx; alg = kx.crv === 'P-384' ? 'ES384' : 'ES256';
        } else if (t && t.tag === 18 && Array.isArray(t.value) && t.value[0] && t.value[0].length) {
          const h = cborlib.decodeFirstSync(t.value[0]);
          // The kid may sit in the protected or in the unprotected header (the battery uses the unprotected one).
          const u = t.value[1] instanceof Map ? t.value[1] : new Map();
          const kidRaw = h.get(4) ?? u.get(4);
          const kid = kidRaw ? Buffer.from(kidRaw).toString('base64url') : null;
          const a = h.get(1);
          if (kid && KID[kid] && KID[kid].kty === 'EC') { j = KID[kid]; alg = KID[kid].crv === 'P-384' ? 'ES384' : 'ES256'; }
          else if (a === -35) { j = KID[ALG2KID['ES384']]; alg = 'ES384'; }
        } else if (t && t.tag === 98 && Array.isArray(t.value) && Array.isArray(t.value[3])) {
          // COSE_Sign: the ES256 key is kept when a signer carries its kid; otherwise the key named by the kid of the
          // first signer that resolves to an EC key (contract section 8 item 1; decision D9).
          const kids = t.value[3].map((s) => {
            const h = s[0] && s[0].length ? cborlib.decodeFirstSync(s[0]) : new Map();
            const u = s[1] instanceof Map ? s[1] : new Map();
            const k = (h instanceof Map ? h.get(4) : undefined) ?? u.get(4);
            return k ? Buffer.from(k).toString('base64url') : null;
          });
          if (!kids.includes(j.kid)) {
            const k = kids.find((x) => x && KID[x] && KID[x].kty === 'EC');
            if (k) { j = KID[k]; alg = KID[k].crv === 'P-384' ? 'ES384' : 'ES256'; }
          }
        }
        // The COSE kid is the base64url-decoded JWK kid (32 bytes). getSigner compares it with Buffer.from(key.kid),
        // so the kid must be passed as bytes; a base64url string never matches a signer of a COSE_Sign message.
        const verifier = { key: { x: b64d(j.x), y: b64d(j.y), kid: b64d(j.kid) } };
        await cose.sign.verify(buf, verifier);
        return [{ sira: 0, alg, sonuc: 'gecerli' }];
      },
    };
  },
  'SDJWT-015': () => {
    const { SDJwtInstance, SDJwtGeneralJSONInstance, GeneralJSON } = require('@sd-jwt/core');
    const jose = require('jose');
    const hasher = async (data, alg) => new Uint8Array(createHash('sha256').update(typeof data === 'string' ? data : Buffer.from(data)).digest());
    // Documented integration: the application supplies the crypto (the verifier callback only answers "is this signature valid with this key?"; the policy is in the library's allowedIssuerAlgorithms option)
    const verifier = async (data, sig) => {
      const h = hdrOf(data); const j = jwkFor(h); if (!j || !SUBTLE[h.alg]) return false;
      try { const k = await jose.importJWK({ ...j }, h.alg); return await webcrypto.subtle.verify(SUBTLE[h.alg], k, b64d(sig), new TextEncoder().encode(data)); } catch { return false; }
    };
    const kbVerifier = async (data, sig, payload) => {
      const h = hdrOf(data); const j = payload?.cnf?.jwk; if (!j || !SUBTLE[h.alg]) return false;
      try { const k = await jose.importJWK({ ...j }, h.alg); return await webcrypto.subtle.verify(SUBTLE[h.alg], k, b64d(sig), new TextEncoder().encode(data)); } catch { return false; }
    };
    const supported = ['ES256', 'EdDSA', 'Ed25519', 'ML-DSA-44', 'ML-DSA-65', 'ML-DSA-87'];
    const sd = new SDJwtInstance({ hasher, verifier, kbVerifier, hashAlg: 'sha-256' });
    const sdg = new SDJwtGeneralJSONInstance({ hasher, verifier, kbVerifier, hashAlg: 'sha-256' });
    return {
      ver: require('@sd-jwt/core/package.json').version, api: 'SDJwtInstance.verify / SDJwtGeneralJSONInstance.verify(…, {allowedIssuerAlgorithms: W, keyBindingNonce})',
      formats: new Set(['sd-jwt-compact', 'sd-jwt-general', 'compact-as-sdjwt']),
      async verify(job, data, X) {
        const pol = temel(job.politika); const g = MAN[job.vektor_id];
        if (['L4-Y'].includes(pol)) return 'ifade-edilemedi';   // no option to ignore a signature outside W (in General JSON every signature must be in the allow-list)
        const opts = { skipJwtClaimValidation: true };
        if (job.artefakt?.startsWith('sd-jwt-vc+kb')) { opts.keyBindingNonce = g.kb_nonce; }
        if (job.serilestirme === 'sd-jwt-general') {
          const j = JSON.parse(data);
          // With several signatures every signature must be in allowedIssuerAlgorithms, and there is no option for a
          // required set: R = {X} with A allowed cannot be configured (decision D9).
          if (['L4', 'L4-S'].includes(pol) && (j.signatures ?? []).length > 1) return 'ifade-edilemedi';
          const iss = (() => { try { return JSON.parse(b64d(j.payload).toString()).iss; } catch { return undefined; } })();
          opts.allowedIssuerAlgorithms = allowed(pol, X, iss, supported);
          const r = await sdg.verify(GeneralJSON.fromSerialized(j), opts);
          return (r.headers ?? []).map((h, i) => ({ sira: i, alg: h.alg, sonuc: 'gecerli' }));
        }
        let s = data.trim(); if (job.serilestirme === 'compact') s = s + '~';   // SD-JWT without disclosures (signature/payload unchanged)
        opts.allowedIssuerAlgorithms = allowed(pol, X, issOf(s.split('~')[0]), supported);
        const r = await sd.verify(s, opts);
        return [{ sira: 0, alg: r.header?.alg, sonuc: 'gecerli' }];
      },
    };
  },
};

const t = T[HID]();
const asha = createHash('sha256').update(readFileSync(new URL(import.meta.url))).digest('hex');
writeFileSync(CIKTI, '');
for (const line of readFileSync(ISLER, 'utf8').split('\n').filter(Boolean)) {
  const job = JSON.parse(line); const X = X_OF[job.kol] ?? 'EdDSA';
  const rec = { hedef_id: HID, hedef_surum: t.ver, adaptor_sha256: asha, kosu: KOSU, vektor_id: job.vektor_id, politika: job.politika, kol: job.kol,
    sonuc_ham: null, hata_sinifi: null, hata_ozeti: null, dogrulanan_algoritmalar: [], api_yolu: t.api, sure_ms: null };
  const eff = (job.serilestirme === 'compact' && t.formats.has('compact-as-sdjwt')) ? 'compact-as-sdjwt' : job.serilestirme;
  if (!t.formats.has(eff)) { Object.assign(rec, { sonuc_ham: 'uygulanamaz', hata_sinifi: 'bicim-desteklenmiyor' }); appendFileSync(CIKTI, JSON.stringify(rec) + '\n'); continue; }
  const data = readFileSync(`/v/${job.dosya}`, 'utf8'); const t0 = performance.now();
  try {
    const r = await Promise.race([t.verify(job, data, X), new Promise((_, rej) => setTimeout(() => rej(Object.assign(new Error('zaman-asimi'), { code: 'TIMEOUT' })), 60000))]);
    if (r === 'ifade-edilemedi') rec.sonuc_ham = 'ifade-edilemedi'; else Object.assign(rec, { sonuc_ham: 'kabul', dogrulanan_algoritmalar: r });
  } catch (e) {
    if (e?.code === 'TIMEOUT') Object.assign(rec, { sonuc_ham: 'zaman-asimi', hata_sinifi: 'zaman-asimi' });
    else Object.assign(rec, { sonuc_ham: 'red', hata_sinifi: klass(e), hata_ozeti: `${e?.code ?? e?.name}: ${e?.message ?? e}`.slice(0, 200) });
  }
  rec.sure_ms = Math.round((performance.now() - t0) * 100) / 100;
  appendFileSync(CIKTI, JSON.stringify(rec) + '\n');
}
process.exit(0);
