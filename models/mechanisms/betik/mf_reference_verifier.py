#!/usr/bin/env python3
"""Reference implementation of the verification rule of the profile M-f (Section 7 and Section S6 of the paper).

The verifier adds the checks of M-f to trusted-list processing and certificate path validation. It handles one
trusted list in the XML format of ETSI TS 119 612, in the form of the rule that is available today, that is without a
response bound to a nonce. A list is used only with a valid detached signature under the pinned key of the list
operator (a stand-in for the XML signature of the list), as in any list validation. Each of the ten checks of M-f
can be switched off through `relax`:
  carrier    the pinned key of the list operator must be quantum-safe,
  currency   a list is adopted only if its sequence number is not lower than one that the list cache has processed,
             and a retrieved list only if its next update has not passed,
  sunset     a none value expires at the earlier of its sunset and the next update of its list,
  stored     pq_required, once seen for a provider, is stored permanently under all identities of the provider and
             applies to every entry with one of them, and to evidence that names one of them if the held list has
             no entry with it,
  binding    besides the entries whose service digital identities contain an anchor of the validated path, the
             verifier considers the entries of every provider that the subject of the end-entity certificate names,
  strictest  the strictest state among all considered entries applies, together with the scope of every considered
             entry whose state is not none,
  unknown    an unknown state counts as pq_required,
  path       with path scope, every certificate of the x5c chain that another certificate of the chain signed is
             signed with a quantum-safe key,
  anchor     with path scope, the certificate that the anchor signed is signed with a quantum-safe key, and the
             algorithm of the anchor is the one of its certificate in the list,
  key        with key scope, the end-entity key is the bound key.
A state other than none always requires a quantum-safe end-entity key. A provider without a record counts as none
with the next update of the list as its sunset. A list may be stale even when it was retrieved over an authenticated
channel, so the sunset and the stored state apply to every list, as Section S6 requires of a verifier that may act on
a stale copy. The stored state persists in the JSON file `store`, and the list copy and its sequence number belong to
the list cache of the verifier instance.
A subject names a provider if its organisation name, organisation identifier or common name equals one of the names,
trade names or registration identifiers of the provider after normalisation (NFKC, case folding, white space), and a
registration identifier also matches one with the same country and number under another type or punctuation. The
path check uses the listed anchor closest to the end-entity certificate.
Path validation (signatures, validity periods, basic constraints) is delegated to `openssl verify` of OpenSSL 3.5 or
later. ML-DSA and SLH-DSA count as quantum-safe and composite signatures as classical. Revocation, the type and status
of a service and the signature of the credential itself are left to the existing validation. Only the Python standard
library and the OpenSSL command line are used. `relax=('mf',)` gives a verifier without M-f, which checks the list
signature under the pinned key of any algorithm and accepts every path that a listed anchor validates.
"""
import base64
import datetime
import functools
import hashlib
import json
import os
import re
import subprocess
import tempfile
import unicodedata
import xml.etree.ElementTree as ET

TSL_NS = 'http://uri.etsi.org/02231/v2#'
PQ_NS = 'urn:example:pq-expectation'      # illustrative namespace, as in record_on_trusted_lists.py
NS = {'tsl': TSL_NS, 'pq': PQ_NS}
Q_OIDS = {'2.16.840.1.101.3.4.3.%d' % i for i in range(17, 32)}   # ML-DSA-44/65/87 and the twelve SLH-DSA sets
OID_ORG_ID, OID_O, OID_CN = '2.5.4.97', '2.5.4.10', '2.5.4.3'    # organizationIdentifier, organizationName, commonName
# legal-person identifier types: VAT, NTR (TS 119 612 clause 5.4.2), PSD, LEI (EN 319 412-1 clause 5.1.4)
REG_ID = re.compile(r'^(VAT|NTR|PSD|LEI)[A-Z]{2}-')
ANY_ID = re.compile(r'^[a-z]{3}([a-z]{2})[-:](.+)$')              # any type, applied after normalisation
STRICTNESS = {'none': 0, 'pq_required': 1, 'retired': 2}
CHECKS = ('carrier', 'currency', 'sunset', 'stored', 'binding', 'strictest', 'unknown', 'path', 'anchor', 'key')
SERVICE_IDS = ('tsl:TSPServices/tsl:TSPService/tsl:ServiceInformation/tsl:ServiceDigitalIdentity/'
               'tsl:DigitalId/tsl:X509Certificate')
STRING_TYPES = {0x0C: 'utf-8', 0x12: 'latin-1', 0x13: 'latin-1', 0x14: 'latin-1', 0x16: 'latin-1',
                0x1A: 'latin-1', 0x1C: 'utf-32-be', 0x1E: 'utf-16-be'}
_PATHS = {}                                                       # cache of path validation results


def identities(values):
    """Normalised identities of a set of names; a registration identifier also yields its country and number."""
    out = set()
    for v in values:
        n = ' '.join(unicodedata.normalize('NFKC', v or '').casefold().split())
        if n:
            out.add(n)
            m = ANY_ID.match(n)
            if m:
                out.add('id:' + m.group(1) + re.sub(r'[^0-9a-z]', '', m.group(2)))
    return out


# --------------------------------------------------------------------------- certificates and keys

def _tlv(b, i):
    tag, length, i = b[i], b[i + 1], i + 2
    if length & 0x80:
        n = length & 0x7F
        length, i = int.from_bytes(b[i:i + n], 'big'), i + n
    return tag, i, i + length


def _children(b, start, end):
    out, i = [], start
    while i < end:
        tag, s, e = _tlv(b, i)
        out.append((tag, s, e, i))
        i = e
    return out


def _oid(b):
    parts, v = [b[0] // 40, b[0] % 40], 0
    for x in b[1:]:
        v = (v << 7) | (x & 0x7F)
        if not x & 0x80:
            parts.append(v)
            v = 0
    return '.'.join(str(p) for p in parts)


def _algorithm(der, node):
    first = _children(der, node[1], node[2])[0]
    return _oid(der[first[1]:first[2]])


def _name(der, node):
    attrs = {}
    for rdn in _children(der, node[1], node[2]):
        for atv in _children(der, rdn[1], rdn[2]):
            oid, value = _children(der, atv[1], atv[2])[:2]
            text = der[value[1]:value[2]].decode(STRING_TYPES.get(value[0], 'utf-8'), 'replace')
            attrs.setdefault(_oid(der[oid[1]:oid[2]]), []).append(text)
    return attrs


def _pem_body(text):
    return base64.b64decode(''.join(l for l in text.splitlines() if l and not l.startswith('-----')))


class Cert:
    """The fields of an X.509 certificate that the policy layer needs."""

    def __init__(self, der):
        self.der = der
        _, s, e = _tlv(der, 0)
        tbs, sigalg = _children(der, s, e)[:2]
        self.sig_oid = _algorithm(der, sigalg)
        kids = _children(der, tbs[1], tbs[2])
        k = 1 if kids[0][0] == 0xA0 else 0
        issuer, subject, spki = kids[k + 2], kids[k + 4], kids[k + 5]
        self.issuer_der = der[issuer[3]:issuer[2]]
        self.subject_der = der[subject[3]:subject[2]]
        self.subject = _name(der, subject)
        self.key_oid = _algorithm(der, _children(der, spki[1], spki[2])[0])
        self.key_digest = base64.b64encode(hashlib.sha256(der[spki[3]:spki[2]]).digest()).decode()
        self.key_is_q, self.signed_with_q = self.key_oid in Q_OIDS, self.sig_oid in Q_OIDS

    @functools.cached_property
    def names(self):
        return identities(sum((self.subject.get(o, []) for o in (OID_ORG_ID, OID_O, OID_CN)), []))

    def pem(self):
        b64 = base64.b64encode(self.der).decode()
        return '-----BEGIN CERTIFICATE-----\n%s\n-----END CERTIFICATE-----\n' % '\n'.join(
            b64[i:i + 64] for i in range(0, len(b64), 64))


def load_pem(text):
    return Cert(_pem_body(text))


def public_key_oid(pem_text):
    der = _pem_body(pem_text)
    _, s, e = _tlv(der, 0)
    return _algorithm(der, _children(der, s, e)[0])


# --------------------------------------------------------------------------- trusted list

def parse_time(s):
    if not s:
        return None
    t = datetime.datetime.fromisoformat(re.sub(r'\.\d+', '', s.strip()).replace('Z', '+00:00'))
    return t if t.tzinfo else t.replace(tzinfo=datetime.timezone.utc)


class Provider:
    def __init__(self, names, trade_names, record, certs):
        self.names, self.trade_names, self.record, self.certs = names, trade_names, record, certs
        self.ids = identities(names + trade_names)

    def named_by(self, leaf):
        return bool(self.ids & leaf.names)


class TrustedList:
    def __init__(self, xml_bytes):
        root = ET.fromstring(xml_bytes)
        si = root.find('tsl:SchemeInformation', NS)
        self.sequence = int(si.findtext('tsl:TSLSequenceNumber', namespaces=NS))
        self.next_update = parse_time(si.findtext('tsl:NextUpdate/tsl:dateTime', namespaces=NS))
        self.providers, self.unreadable = [], 0
        for tsp in root.iterfind('tsl:TrustServiceProviderList/tsl:TrustServiceProvider', NS):
            info = tsp.find('tsl:TSPInformation', NS)
            records = [{'state': (e.text or '').strip(), 'scope': e.get('Scope', 'path'),
                        'sunset': parse_time(e.get('Sunset')), 'key': e.get('KeyDigest')}
                       for e in info.iterfind('tsl:TSPInformationExtensions/tsl:Extension/pq:Expectation', NS)]
            certs = []
            for x in tsp.iterfind(SERVICE_IDS, NS):
                try:
                    certs.append(Cert(base64.b64decode(''.join(x.text.split()))))
                except (IndexError, ValueError, TypeError, AttributeError):
                    self.unreadable += 1
            self.providers.append(Provider(
                [n.text for n in info.iterfind('tsl:TSPName/tsl:Name', NS)],
                [n.text for n in info.iterfind('tsl:TSPTradeName/tsl:Name', NS)],
                max(records, key=lambda r: STRICTNESS.get(r['state'], 1)) if records else None, certs))
        self.ids = set().union(*(p.ids for p in self.providers)) if self.providers else set()


# --------------------------------------------------------------------------- verifier

class Decision:
    def __init__(self, accept, reason, source, state=''):
        self.accept, self.reason, self.source, self.state = accept, reason, source, state

    def __repr__(self):
        return '%s (%s; %s)' % ('accept' if self.accept else 'reject', self.reason, self.source)


class Verifier:
    """pinned: PEM file of the public key of the list operator. store: JSON file of the stored state."""

    def __init__(self, pinned=None, store=None, relax=(), openssl=None):
        if set(relax) - set(CHECKS) - {'mf'}:
            raise ValueError('unknown check: %s' % sorted(set(relax) - set(CHECKS) - {'mf'}))
        self.pinned, self.store, self.relax = pinned, store, set(relax)
        self.openssl = openssl or os.environ.get('OPENSSL', 'openssl')
        self.copy, self.max_sequence, self.seen = None, None, set()
        if store and os.path.exists(store):
            with open(store, encoding='utf-8') as f:
                self.seen = set(json.load(f)['seen'])

    def _off(self, check):
        return check in self.relax or 'mf' in self.relax

    def _authentic(self, xml_bytes, signature):
        if not self.pinned or signature is None:
            return False
        with open(self.pinned) as f:
            q = public_key_oid(f.read()) in Q_OIDS
        if not q and not self._off('carrier'):
            return False
        with tempfile.TemporaryDirectory() as d:
            data, sig = os.path.join(d, 'list.xml'), os.path.join(d, 'list.sig')
            with open(data, 'wb') as f:
                f.write(xml_bytes)
            with open(sig, 'wb') as f:
                f.write(signature)
            cmd = [self.openssl, 'pkeyutl', '-verify', '-pubin', '-inkey', self.pinned, '-rawin', '-in', data,
                   '-sigfile', sig] + ([] if q else ['-digest', 'sha256'])    # classical keys sign a SHA-256 digest
            return subprocess.run(cmd, capture_output=True).returncode == 0

    def _not_older(self, tl):
        return self._off('currency') or self.max_sequence is None or tl.sequence >= self.max_sequence

    def _adopt(self, tl):
        self.copy = tl
        self.max_sequence = tl.sequence if self.max_sequence is None else max(self.max_sequence, tl.sequence)
        for p in tl.providers:
            if self._recorded(p, tl)[0] != 'none':
                self.seen |= p.ids
        if self.store:
            with open(self.store, 'w', encoding='utf-8') as f:
                json.dump({'seen': sorted(self.seen)}, f)

    def provision(self, xml_bytes, signature):
        """Installs a copy without a guarantee of currency, for example with the software or from a cache."""
        tl = TrustedList(xml_bytes)
        if self._authentic(xml_bytes, signature) and self._not_older(tl):
            self._adopt(tl)
            return True
        return False

    def refresh(self, xml_bytes, signature, now):
        """Step 1: adopts a list version retrieved from the publisher only if it is authentic and current."""
        tl = TrustedList(xml_bytes)
        current = self._off('currency') or (tl.next_update is not None and now < tl.next_update)
        if self._authentic(xml_bytes, signature) and self._not_older(tl) and current:
            self._adopt(tl)
            return True
        return False

    def _recorded(self, p, tl):
        if p.record is None:
            return 'none', 'path', tl.next_update, None
        state = p.record['state']
        if state not in STRICTNESS:
            state = 'none' if self._off('unknown') else 'pq_required'
        return state, p.record['scope'], p.record['sunset'] or tl.next_update, p.record['key']

    def _state(self, p, tl, now):
        state, scope, sunset, bound = self._recorded(p, tl)
        if state == 'none' and not self._off('stored') and p.ids & self.seen:
            state = 'pq_required'
        if state == 'none' and not self._off('sunset'):
            ends = [t for t in (sunset, tl.next_update) if t is not None]
            if not ends or now >= min(ends):
                state = 'pq_required'
        return state, scope, bound

    def _path_valid(self, chain, anchor, now):
        k = (tuple(c.der for c in chain), anchor.der, int(now.timestamp()))
        if k not in _PATHS:
            with tempfile.TemporaryDirectory() as d:
                files = {}
                for name, certs in (('anchor', [anchor]), ('leaf', chain[:1]), ('untrusted', chain[1:])):
                    if certs:
                        files[name] = os.path.join(d, name + '.pem')
                        with open(files[name], 'w') as f:
                            f.write(''.join(c.pem() for c in certs))
                cmd = [self.openssl, 'verify', '-no-CApath', '-no-CAstore', '-partial_chain',
                       '-attime', str(k[2]), '-CAfile', files['anchor']]
                if 'untrusted' in files:
                    cmd += ['-untrusted', files['untrusted']]
                _PATHS[k] = subprocess.run(cmd + [files['leaf']], capture_output=True).returncode == 0
        return _PATHS[k]

    def decide(self, chain, now, retrieved=None):
        """chain: the certificates of the x5c header, end-entity certificate first.
        retrieved: a list version and its signature, obtained from the publisher for this decision."""
        source = 'retrieved list' if retrieved is not None and self.refresh(*retrieved, now) else 'held copy'
        tl = self.copy
        if tl is None:
            return Decision(False, 'no authentic list', source)
        if any(chain[i].issuer_der != chain[i + 1].subject_der for i in range(len(chain) - 1)):
            return Decision(False, 'x5c is not an ordered chain', source)
        leaf, top = chain[0], chain[-1]
        matches = []                       # (position of the anchor in the chain or after it, provider, anchor)
        positions = {c.der: i for i, c in enumerate(chain)}
        for p in tl.providers:
            for a in p.certs:
                pos = positions.get(a.der)
                if pos is None and a.subject_der == top.issuer_der:
                    pos = len(chain)
                if pos is not None and self._path_valid(chain[:pos + 1] if pos < len(chain) else chain, a, now):
                    matches.append((pos, p, a))
        if not matches:
            return Decision(False, 'no listed anchor validates the path', source)
        if 'mf' in self.relax:
            return Decision(True, 'valid path', source)
        entries = []
        for _, p, _ in matches:
            if p not in entries:
                entries.append(p)
        named = [p for p in tl.providers if p.named_by(leaf)]
        if not self._off('binding'):
            entries += [p for p in named if p not in entries]
        if self._off('strictest'):
            entries = ([p for p in named if p in entries] or entries)[:1]
        required = [s for s in (self._state(p, tl, now) for p in entries) if s[0] != 'none']
        if not self._off('stored') and (leaf.names & self.seen) - tl.ids:
            required.append(('pq_required', 'path', None))         # a stored provider that the list no longer has
        if not required:
            return Decision(True, 'state none', source, 'none')
        state = max((s[0] for s in required), key=STRICTNESS.get)
        if not leaf.key_is_q:
            return Decision(False, 'classical leaf key', source, state)
        if not self._off('key') and any(s[1] == 'key' and leaf.key_digest != s[2] for s in required):
            return Decision(False, 'not the bound key', source, state)
        if all(s[1] == 'key' for s in required):
            return Decision(True, 'key scope met', source, state)
        pos, _, anchor = min(matches, key=lambda m: m[0])             # the listed anchor closest to the leaf
        path = chain[:pos]                                            # certificates below the anchor
        inner, outer = path[:-1], path[-1:]
        if not self._off('path') and not all(c.signed_with_q for c in inner):
            return Decision(False, 'classical edge below the anchor', source, state)
        if not self._off('anchor') and not (all(c.signed_with_q for c in outer) and anchor.key_is_q):
            return Decision(False, 'classical anchor edge', source, state)
        return Decision(True, 'Q-clean path', source, state)
