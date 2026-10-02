// Evidence-rule second attempt, COSE-014 (cose-js 0.9.0).
// Own keys and objects only. A = ES256, X = ES384 (cose-js 0.9.0 has no EdDSA: lib/sign.js L16-37).
'use strict';
const crypto = require('crypto');
const cbor = require('cbor');
const cose = require('cose-js');

function ecKey (curve, kid) {
  const { privateKey } = crypto.generateKeyPairSync('ec', { namedCurve: curve });
  const j = privateKey.export({ format: 'jwk' });
  const b = (s) => Buffer.from(s, 'base64url');
  return { kid, d: b(j.d), x: b(j.x), y: b(j.y) };
}
const pub = (k) => ({ key: { x: k.x, y: k.y, kid: k.kid } });
const priv = (k) => ({ key: { d: k.d } });

const MIG_ES256 = ecKey('P-256', 'mig-es256');
const MIG_X = ecKey('P-384', 'mig-es384');
const LEG_ES256 = ecKey('P-256', 'leg-es256');
const PAYLOAD = Buffer.from(JSON.stringify({ iss: 'https://issuer.example', sub: 'user-1' }));
const PAYLOAD_LEG = Buffer.from(JSON.stringify({ iss: 'https://legacy-issuer.example', sub: 'user-1' }));

// COSE_Sign with one signer (library API), body protected header empty.
async function sign1Signer (k, alg) {
  return cose.sign.create({ p: {}, u: {} }, PAYLOAD, [{ key: { d: k.d }, p: { alg }, u: { kid: k.kid } }]);
}
// Test-object generation: merge the signer arrays of single-signer COSE_Sign messages over the same body.
async function multi (parts) {
  const sigs = [];
  let body;
  for (const [k, alg, corrupt] of parts) {
    const t = await cbor.decodeFirst(await sign1Signer(k, alg));
    body = t.value;
    const s = t.value[3][0];
    if (corrupt) { s[2] = Buffer.from(s[2]); s[2][5] ^= 0x01; }
    sigs.push(s);
  }
  return cbor.encode(new cbor.Tagged(98, [body[0], body[1], body[2], sigs]));
}
async function sign1 (k, alg, payload) {
  return cose.sign.create({ p: { alg }, u: { kid: k.kid } }, payload, { key: { d: k.d } });
}

let ok = 0; let n = 0;
async function run (label, msg, verifier, expect) {
  let res; let detail = '';
  try { await cose.sign.verify(msg, verifier); res = 'accept'; } catch (e) { res = 'reject'; detail = String(e.message || e).slice(0, 90); }
  let mark = '-';
  if (expect) { n++; if (res === expect) { ok++; mark = 'OK'; } else mark = 'MISMATCH'; }
  console.log(`${label.padEnd(52)} ${res.padEnd(7)} expect=${(expect || '-').padEnd(7)} ${mark.padEnd(9)} ${detail}`);
}

(async () => {
  console.log('== cose-js', require('cose-js/package.json').version, 'node', process.version);
  console.log('exports of cose.sign:', Object.keys(cose.sign).join(', '));
  console.log('\n== 1. Validity check (COSE_Sign1)');
  const s1MigEs = await sign1(MIG_ES256, 'ES256', PAYLOAD);
  const s1MigX = await sign1(MIG_X, 'ES384', PAYLOAD);
  const s1LegEs = await sign1(LEG_ES256, 'ES256', PAYLOAD_LEG);
  await run('V+ Sign1 migrated ES256', s1MigEs, pub(MIG_ES256), 'accept');
  await run('V+ Sign1 migrated ES384', s1MigX, pub(MIG_X), 'accept');
  await run('V+ Sign1 legacy ES256', s1LegEs, pub(LEG_ES256), 'accept');
  const bad = Buffer.from(s1MigEs); bad[bad.length - 3] ^= 0x01;
  await run('V- Sign1 migrated ES256 corrupted', bad, pub(MIG_ES256), 'reject');

  console.log('\n== 2. L4m (primary form): COSE_Sign, R = {ES384}, W = {ES256, ES384}');
  const T1 = await multi([[MIG_ES256, 'ES256'], [MIG_X, 'ES384']]);
  const T2 = await multi([[MIG_ES256, 'ES256'], [MIG_X, 'ES384', true]]);
  const T3 = await multi([[MIG_ES256, 'ES256']]);
  const T5 = await multi([[MIG_X, 'ES384']]);
  console.log('verify options: only {defaultType}; verifier object: {key:{x,y,kid}, externalAAD}');
  console.log('configuration: verifier = key of the required algorithm X (kid mig-es384)');
  await run('L4m T1 both valid', T1, pub(MIG_X), 'accept');
  await run('L4m T2 X corrupted', T2, pub(MIG_X), 'reject');
  await run('L4m T3 stripped to ES256', T3, pub(MIG_X), 'reject');
  await run('L4m T5 only X', T5, pub(MIG_X), 'accept');
  // the kid is in the unprotected header: relabel the ES256 signer of T3 with the X kid
  const t3 = await cbor.decodeFirst(T3); const sg = t3.value[3][0];
  sg[1] = new Map([[4, Buffer.from('mig-es384')]]);
  const T3relabel = cbor.encode(new cbor.Tagged(98, t3.value));
  await run('L4m T3 with ES256 signer relabelled kid=mig-es384', T3relabel, pub(MIG_X), 'reject');
  console.log('for contrast, verifier = classical key (kid mig-es256):');
  await run('  T2 X corrupted', T2, pub(MIG_ES256), null);
  await run('  T3 stripped to ES256', T3, pub(MIG_ES256), null);

  console.log('\n== 3. L4c (supplement): COSE_Sign1, migrated record holds its ES256 key');
  console.log('there is no algorithm or issuer option; alg is read from the header (lib/sign.js L273) and used as is');
  await run('L4c migrated ES256 (L4c wants reject)', s1MigEs, pub(MIG_ES256), 'reject');
  await run('L4c migrated ES384 (L4c wants accept)', s1MigX, pub(MIG_X), 'accept');
  await run('L4c legacy ES256 (L4c wants accept)', s1LegEs, pub(LEG_ES256), 'accept');

  console.log(`\n== SUMMARY: checked rows OK = ${ok} of ${n}`);
})();
