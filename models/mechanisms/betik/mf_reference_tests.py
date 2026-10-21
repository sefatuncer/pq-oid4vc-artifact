#!/usr/bin/env python3
"""Tests of the reference verifier of M-f (mf_reference_verifier.py) on generated trusted lists.

The script
  1. generates a test PKI with OpenSSL: classical anchors and certificates with ECDSA P-256 keys, quantum-safe ones
     with ML-DSA-65 keys, end-entity certificates that name a provider or a subscriber in various ways, the keys of
     the list operator (ML-DSA-65, and ECDSA P-256 as a classical key) and the key of an attacker,
  2. writes two versions of a trusted list in the format of ETSI TS 119 612 V2.4.1 that carry the M-f record as a
     non-critical TSP information extension, a forged third version that puts a migrated provider back in state none
     and a fourth version from which that provider is withdrawn, adds detached signatures, and checks the four lists
     against the official schema if a schema directory is given,
  3. runs every test case with the full rule and without M-f, and every rejected case with each of the ten checks
     switched off in turn and with the checks that are expected to stop it switched off together, and writes
     ../sonuc/mf_reference_tests.csv and, for every check, the cases that it alone stops,
     ../sonuc/mf_reference_checks.csv,
  4. measures the time of a decision with the list adopted and path validation cached on the test list and, if
     national lists are given, of a lookup in the largest of them, and writes ../sonuc/mf_reference_timing.csv,
  5. if a directory of national trusted lists is given, inserts the record into every TSP entry as
     record_on_trusted_lists.py does, reads it back with the verifier and counts the listed certificates whose
     subject names their own provider in a form that the verifier recognises, ../sonuc/mf_reference_national.csv.
Usage: mf_reference_tests.py [<schema_dir> [<list_dir>]]
The schema and list directories are those of record_on_trusted_lists.py. Requires OpenSSL 3.5 or later on the path
or in the environment variable OPENSSL, and xmlschema for the schema check. The test PKI is generated anew on every
run, so the decisions are reproducible but keys, list sizes and timings are not.
"""
import csv
import datetime
import io
import os
import random
import statistics
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mf_reference_verifier as mf  # noqa: E402

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(KOK, 'sonuc')
OPENSSL = os.environ.get('OPENSSL', 'openssl')
UTC = datetime.timezone.utc
T2 = datetime.datetime(2027, 4, 1, tzinfo=UTC)     # after the migration of B, list version 1 still valid
T2B = datetime.datetime(2027, 5, 15, tzinfo=UTC)   # after the sunset of H in version 2, before that in version 1
T3 = datetime.datetime(2027, 6, 15, tzinfo=UTC)    # after the sunset of B in version 1, before its next update
T4 = datetime.datetime(2027, 8, 1, tzinfo=UTC)     # after the next update of version 1
VERSIONS = {1: ('2027-01-01T00:00:00Z', '2027-07-01T00:00:00Z'),
            2: ('2027-03-01T00:00:00Z', '2027-09-01T00:00:00Z'),
            3: ('2027-03-15T00:00:00Z', '2027-09-15T00:00:00Z'),     # forged
            4: ('2027-04-15T00:00:00Z', '2027-10-15T00:00:00Z')}     # B withdrawn
SUNSET_B_V1 = '2027-06-01T00:00:00Z'
SUNSET_H_V2 = '2027-05-01T00:00:00Z'               # H has announced an earlier migration in version 2
LETTERS = 'ABCDEFGHX'
REPS = 2000

CNF = """[req]
distinguished_name = dn
[dn]
[ca]
basicConstraints = critical, CA:true
keyUsage = critical, keyCertSign, cRLSign
subjectKeyIdentifier = hash
[int]
basicConstraints = critical, CA:true, pathlen:0
keyUsage = critical, keyCertSign, cRLSign
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid
[ee]
basicConstraints = critical, CA:false
keyUsage = critical, digitalSignature
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid
[ee_san]
basicConstraints = critical, CA:false
keyUsage = critical, digitalSignature
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid
subjectAltName = URI:https://tsp.example/b
"""


# --------------------------------------------------------------------------- test PKI

class PKI:
    def __init__(self, d):
        self.d, self.n = d, 0
        self.cnf = os.path.join(d, 'openssl.cnf')
        with open(self.cnf, 'w') as f:
            f.write(CNF)

    def _run(self, *args):
        subprocess.run([OPENSSL] + list(args), check=True, capture_output=True)

    def _key(self, alg):
        self.n += 1
        path = os.path.join(self.d, 'k%02d.pem' % self.n)
        if alg == 'ec':
            self._run('genpkey', '-algorithm', 'EC', '-pkeyopt', 'ec_paramgen_curve:P-256', '-out', path)
        else:
            self._run('genpkey', '-algorithm', 'ML-DSA-65', '-out', path)
        return path

    def keypair(self, alg):
        key = self._key(alg)
        pub = key[:-4] + '.pub.pem'
        self._run('pkey', '-in', key, '-pubout', '-out', pub)
        return {'key': key, 'alg': alg, 'pub': pub}

    def sign(self, keypair, data):
        path = os.path.join(self.d, 'data.bin')
        with open(path, 'wb') as f:
            f.write(data)
        self._run('pkeyutl', '-sign', '-inkey', keypair['key'], '-rawin', '-in', path, '-out', path + '.sig',
                  *(['-digest', 'sha256'] if keypair['alg'] == 'ec' else []))
        with open(path + '.sig', 'rb') as f:
            return f.read()

    def root(self, subject, alg):
        key, cert = self._key(alg), os.path.join(self.d, 'c%02d.pem' % self.n)
        self._run('req', '-x509', '-new', '-key', key, '-subj', subject, '-days', '3650', '-config', self.cnf,
                  '-extensions', 'ca', '-out', cert, *(['-sha256'] if alg == 'ec' else []))
        return {'key': key, 'alg': alg, 'cert': cert}

    def issue(self, subject, alg, ca, ext):
        key, cert = self._key(alg), os.path.join(self.d, 'c%02d.pem' % self.n)
        csr = cert[:-4] + '.csr'
        self._run('req', '-new', '-key', key, '-subj', subject, '-config', self.cnf, '-out', csr,
                  *(['-sha256'] if alg == 'ec' else []))
        self._run('x509', '-req', '-in', csr, '-CA', ca['cert'], '-CAkey', ca['key'], '-days', '3650',
                  '-set_serial', str(random.getrandbits(63)), '-extfile', self.cnf, '-extensions', ext,
                  '-out', cert, *(['-sha256'] if ca['alg'] == 'ec' else []))
        return {'key': key, 'alg': alg, 'cert': cert}


def cert(entry):
    with open(entry['cert']) as f:
        return mf.load_pem(f.read())


def subject(letter, cn):
    return '/C=ZZ/O=Provider %s/organizationIdentifier=NTRZZ-000000%d/CN=%s' % (letter, LETTERS.index(letter) + 1, cn)


def build_pki(p):
    ca = {name: p.root('/C=ZZ/O=Provider %s/CN=%s' % (name[0], name), alg) for name, alg in (
        ('A Root EC', 'ec'), ('B Root EC', 'ec'), ('B Root ML-DSA', 'q'), ('C Root ML-DSA', 'q'),
        ('D Root EC', 'ec'), ('Shared Root EC', 'ec'), ('F Root EC', 'ec'), ('G Root EC', 'ec'),
        ('H Root EC', 'ec'), ('X Root EC', 'ec'))}
    impostor = p.root('/C=ZZ/O=Provider B/CN=B Root ML-DSA', 'q')     # same name as the listed anchor, other key
    int_bq = p.issue('/C=ZZ/O=Provider B/CN=B Issuing CA ML-DSA', 'q', ca['B Root ML-DSA'], 'int')
    int_bec = p.issue('/C=ZZ/O=Provider B/CN=B Issuing CA EC', 'ec', ca['B Root ML-DSA'], 'int')
    int_bq2 = p.issue('/C=ZZ/O=Provider B/CN=B Issuing CA ML-DSA under EC', 'q', ca['B Root EC'], 'int')
    leaf = lambda letter, alg, issuer, cn: cert(p.issue(subject(letter, cn), alg, issuer, 'ee'))
    chains = {
        'A classical': [leaf('A', 'ec', ca['A Root EC'], 'A issuer EC')],
        'B Q-clean': [leaf('B', 'q', int_bq, 'B issuer ML-DSA'), cert(int_bq)],
        'B classical': [leaf('B', 'ec', ca['B Root EC'], 'B issuer EC')],
        'B PQ leaf under classical intermediate': [leaf('B', 'q', int_bec, 'B issuer ML-DSA 2'), cert(int_bec)],
        'B PQ path under classical anchor': [leaf('B', 'q', int_bq2, 'B issuer ML-DSA 3'), cert(int_bq2)],
        'C bound key': [leaf('C', 'q', ca['C Root ML-DSA'], 'C issuer ML-DSA')],
        'C other PQ key': [leaf('C', 'q', ca['C Root ML-DSA'], 'C issuer ML-DSA 2')],
        'B name under A anchor': [leaf('B', 'ec', ca['A Root EC'], 'B issuer EC 2')],
        'E name under shared anchor': [leaf('E', 'ec', ca['Shared Root EC'], 'E issuer EC')],
        'D classical': [leaf('D', 'ec', ca['D Root EC'], 'D issuer EC')],
        'F classical': [leaf('F', 'ec', ca['F Root EC'], 'F issuer EC')],
        'G classical': [leaf('G', 'ec', ca['G Root EC'], 'G issuer EC')],
        'H classical': [leaf('H', 'ec', ca['H Root EC'], 'H issuer EC')],
        'X classical': [leaf('X', 'ec', ca['X Root EC'], 'X issuer EC')],
        'B PQ leaf from an unlisted key with the name of the B anchor': [leaf('B', 'q', impostor, 'B issuer ML-DSA 4')],
        'subscriber of A classical': [cert(p.issue('/C=ZZ/O=Subscriber S/organizationIdentifier=NTRZZ-0000099/CN=S',
                                                   'ec', ca['A Root EC'], 'ee'))],
        'subscriber of B under A anchor': [cert(p.issue(
            '/C=ZZ/O=Subscriber T/organizationIdentifier=NTRZZ-0000098/CN=T', 'ec', ca['A Root EC'], 'ee'))],
        'B in the common name only under A anchor': [cert(p.issue('/C=ZZ/CN=Provider B', 'ec', ca['A Root EC'], 'ee'))],
        'B in another spelling under A anchor': [cert(p.issue(
            '/C=ZZ/O=PROVIDER  B/organizationIdentifier=vatzz-0000002/CN=Service', 'ec', ca['A Root EC'], 'ee'))],
        'B in a subject alternative name only under A anchor': [cert(p.issue(
            '/C=ZZ/CN=Service', 'ec', ca['A Root EC'], 'ee_san'))],
    }
    keys = {name: p.keypair(alg) for name, alg in (('operator_q', 'q'), ('operator_ec', 'ec'), ('attacker_q', 'q'))}
    return {k: cert(v) for k, v in ca.items()}, chains, keys


# --------------------------------------------------------------------------- trusted lists

ADDRESS = ('<PostalAddresses><PostalAddress xml:lang="en"><StreetAddress>Test street 1</StreetAddress>'
           '<Locality>Test city</Locality><CountryName>ZZ</CountryName></PostalAddress></PostalAddresses>'
           '<ElectronicAddress><URI xml:lang="en">https://tl.example/</URI></ElectronicAddress>')


def record(state, scope='path', sunset=None, key=None):
    attrs = ' Scope="%s"' % scope + (' Sunset="%s"' % sunset if sunset else '') + (' KeyDigest="%s"' % key if key else '')
    return '<pq:Expectation%s>%s</pq:Expectation>' % (attrs, state)


def provider(letter, rec, anchors):
    ext = ('<TSPInformationExtensions><Extension Critical="false">%s</Extension></TSPInformationExtensions>' % rec
           if rec else '')
    services = ''.join(
        '<TSPService><ServiceInformation><ServiceTypeIdentifier>http://uri.etsi.org/TrstSvc/Svctype/CA/QC'
        '</ServiceTypeIdentifier><ServiceName><Name xml:lang="en">%s</Name></ServiceName><ServiceDigitalIdentity>'
        '<DigitalId><X509Certificate>%s</X509Certificate></DigitalId></ServiceDigitalIdentity><ServiceStatus>'
        'http://uri.etsi.org/TrstSvc/TrustedList/Svcstatus/granted</ServiceStatus><StatusStartingTime>'
        '2026-10-01T00:00:00Z</StatusStartingTime></ServiceInformation></TSPService>'
        % (name, mf.base64.b64encode(c.der).decode()) for name, c in anchors)
    return ('<TrustServiceProvider><TSPInformation><TSPName><Name xml:lang="en">Provider %s</Name></TSPName>'
            '<TSPTradeName><Name xml:lang="en">NTRZZ-000000%d</Name></TSPTradeName><TSPAddress>%s</TSPAddress>'
            '<TSPInformationURI><URI xml:lang="en">https://tsp.example/%s</URI></TSPInformationURI>%s</TSPInformation>'
            '<TSPServices>%s</TSPServices></TrustServiceProvider>'
            % (letter, LETTERS.index(letter) + 1, ADDRESS, letter.lower(), ext, services))


def trusted_list(version, ca, chains):
    issued, nxt = VERSIONS[version]
    a = lambda *names: [(n, ca[n]) for n in names]
    bound = chains['C bound key'][0].key_digest
    if version == 1:
        b = provider('B', record('none', sunset=SUNSET_B_V1), a('B Root EC', 'Shared Root EC'))
    elif version == 2:
        b = provider('B', record('pq_required'), a('B Root EC', 'B Root ML-DSA', 'Shared Root EC'))
    elif version == 3:
        b = provider('B', record('none', sunset=nxt), a('B Root EC', 'B Root ML-DSA', 'Shared Root EC'))
    else:
        b = ''
    tsps = [provider('A', record('none', sunset=nxt), a('A Root EC')), b,
            provider('C', record('pq_required', scope='key', key=bound), a('C Root ML-DSA')),
            provider('D', record('retired'), a('D Root EC')),
            provider('E', record('none', sunset=nxt), a('Shared Root EC')),
            provider('F', None, a('F Root EC')),
            provider('G', record('pq_preferred'), a('G Root EC')),
            provider('H', record('none', sunset=SUNSET_H_V2 if version in (2, 4) else nxt), a('H Root EC'))]
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<TrustServiceStatusList xmlns="%s" xmlns:pq="%s" '
            'TSLTag="http://uri.etsi.org/19612/TSLTag"><SchemeInformation><TSLVersionIdentifier>6'
            '</TSLVersionIdentifier><TSLSequenceNumber>%d</TSLSequenceNumber><TSLType>'
            'http://uri.etsi.org/TrstSvc/TrustedList/TSLType/EUgeneric</TSLType><SchemeOperatorName>'
            '<Name xml:lang="en">Test scheme operator</Name></SchemeOperatorName><SchemeOperatorAddress>%s'
            '</SchemeOperatorAddress><SchemeName><Name xml:lang="en">ZZ:Test list for the M-f reference verifier'
            '</Name></SchemeName><SchemeInformationURI><URI xml:lang="en">https://tl.example/info</URI>'
            '</SchemeInformationURI><StatusDeterminationApproach>'
            'http://uri.etsi.org/TrstSvc/TrustedList/StatusDetn/EUappropriate</StatusDeterminationApproach>'
            '<SchemeTypeCommunityRules><URI xml:lang="en">http://uri.etsi.org/TrstSvc/TrustedList/schemerules/'
            'EUcommon</URI></SchemeTypeCommunityRules><SchemeTerritory>ZZ</SchemeTerritory><PolicyOrLegalNotice>'
            '<TSLLegalNotice xml:lang="en">Test list without legal effect.</TSLLegalNotice></PolicyOrLegalNotice>'
            '<HistoricalInformationPeriod>65535</HistoricalInformationPeriod><ListIssueDateTime>%s'
            '</ListIssueDateTime><NextUpdate><dateTime>%s</dateTime></NextUpdate></SchemeInformation>'
            '<TrustServiceProviderList>%s</TrustServiceProviderList></TrustServiceStatusList>\n'
            % (mf.TSL_NS, mf.PQ_NS, version, ADDRESS, issued, nxt, ''.join(tsps))).encode('utf-8')


# --------------------------------------------------------------------------- cases

# id, scenario, chain, expected decision under the full rule, checks expected to stop the case (joined by +)
CASES = [
    ('C01', 'current', 'A classical', True, ''),
    ('C02', 'current', 'B Q-clean', True, ''),
    ('C03', 'current', 'B classical', False, ''),
    ('C04', 'current', 'B PQ leaf under classical intermediate', False, 'path'),
    ('C05', 'current', 'B PQ path under classical anchor', False, 'anchor'),
    ('C06', 'current', 'C bound key', True, ''),
    ('C07', 'current', 'C other PQ key', False, 'key'),
    ('C08', 'current', 'B name under A anchor', False, 'binding'),
    ('C09', 'current', 'E name under shared anchor', False, 'strictest'),
    ('C10', 'current', 'D classical', False, ''),
    ('C11', 'current', 'G classical', False, 'unknown'),
    ('C12', 'current', 'F classical', True, ''),
    ('C13', 'current', 'X classical', False, ''),
    ('C14', 'rollback', 'B classical', False, 'currency+stored'),
    ('C15', 'superseded before sunset', 'B classical', True, ''),
    ('C16', 'superseded after sunset', 'B classical', False, 'sunset'),
    ('C17', 'cache cleared', 'B classical', False, 'stored'),
    ('C18', 'stale copy after next update', 'F classical', False, 'sunset'),
    ('C19', 'current', 'B PQ leaf from an unlisted key with the name of the B anchor', False, ''),
    ('C20', 'rollback after shortened sunset', 'H classical', False, 'currency'),
    ('C21', 'forged list, unpinned key', 'B classical', False, ''),
    ('C22', 'forged list, classical pinned key', 'B classical', False, 'carrier'),
    ('C23', 'current', 'subscriber of A classical', True, ''),
    ('C24', 'current', 'subscriber of B under A anchor', True, ''),
    ('C25', 'withdrawn', 'B name under A anchor', False, 'stored'),
    ('C26', 'current', 'B in the common name only under A anchor', False, 'binding'),
    ('C27', 'current', 'B in another spelling under A anchor', False, 'binding'),
    ('C28', 'current', 'B in a subject alternative name only under A anchor', True, ''),
]
SCENARIOS = {
    'current': 'version 2 retrieved at T2',
    'rollback': 'version 2 processed, then version 1 served at T2',
    'rollback after shortened sunset': 'version 2 processed, then version 1 served at T2B',
    'superseded before sunset': 'version 1 retrieved at T2 by a verifier that has not seen version 2',
    'superseded after sunset': 'version 1 retrieved at T3 by a verifier that has not seen version 2',
    'cache cleared': 'version 2 processed, list cache cleared, version 1 installed, stored state kept, T2',
    'stale copy after next update': 'version 1 installed and held at T4',
    'forged list, unpinned key': 'forged version 3 signed with an unpinned ML-DSA key, retrieved at T2',
    'forged list, classical pinned key': 'forged version 3 signed with the pinned ECDSA key of the operator, T2',
    'withdrawn': 'version 2 processed, then version 4 without B retrieved at T2B',
}


def run(scenario, chain, relax, lists):
    with tempfile.TemporaryDirectory() as d:
        store = os.path.join(d, 'state.json')

        def verifier(pinned=lists['pinned_q'], **kw):
            return mf.Verifier(pinned=pinned, relax=relax, **kw)

        if scenario == 'current':
            return verifier().decide(chain, T2, retrieved=lists[2])
        if scenario.startswith('rollback'):
            v = verifier()
            v.refresh(*lists[2], T2)
            return v.decide(chain, T2 if scenario == 'rollback' else T2B, retrieved=lists[1])
        if scenario.startswith('superseded'):
            return verifier().decide(chain, T2 if 'before' in scenario else T3, retrieved=lists[1])
        if scenario == 'cache cleared':
            verifier(store=store).refresh(*lists[2], T2)
            v = verifier(store=store)
            v.provision(*lists[1])
            return v.decide(chain, T2)
        if scenario == 'stale copy after next update':
            v = verifier()
            v.provision(*lists[1])
            return v.decide(chain, T4)
        if scenario == 'withdrawn':
            v = verifier()
            v.refresh(*lists[2], T2)
            return v.decide(chain, T2B, retrieved=lists[4])
        if scenario == 'forged list, unpinned key':
            return verifier().decide(chain, T2, retrieved=lists['forged_q'])
        return verifier(pinned=lists['pinned_ec']).decide(chain, T2, retrieved=lists['forged_ec'])


def schema_check(schema_dir, xml):
    import record_on_trusted_lists as rtl
    schema = rtl.load_schema(schema_dir)
    return {v: rtl.errors(schema, x.decode('utf-8')) for v, x in xml.items()}


def national(list_dir, chains):
    import record_on_trusted_lists as rtl
    rows, largest = [], None
    for name in sorted(os.listdir(list_dir)):
        if not name.endswith('.xml'):
            continue
        with io.open(os.path.join(list_dir, name), 'rb') as f:
            raw = f.read()
        mod, n, _ = rtl.insert_records(raw.decode('utf-8-sig'))
        mod = mod.encode('utf-8')
        t = time.perf_counter()
        tl = mf.TrustedList(mod)
        ms = 1000 * (time.perf_counter() - t)
        read = sum(1 for p in tl.providers if p.record and p.record['state'] == 'pq_required'
                   and p.record['scope'] == 'path' and p.record['sunset'] is not None)
        reg = sum(1 for p in tl.providers if any(mf.REG_ID.match(x or '') for x in p.trade_names))
        certs = sum(len(p.certs) for p in tl.providers)
        own = sum(1 for p in tl.providers for c in p.certs if p.ids & c.names)
        with_certs = [p for p in tl.providers if p.certs]
        known = sum(1 for p in with_certs if any(p.ids & c.names for c in p.certs))
        rows.append([name[:-4], n, read, reg, certs, tl.unreadable, own, len(with_certs), known, '%.1f' % ms])
        if largest is None or len(raw) > largest[1]:
            largest = (name[:-4], len(raw), mod, certs)
        print(rows[-1])
    with io.open(os.path.join(OUT, 'mf_reference_national.csv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['territory', 'tsp_entries', 'records_read', 'entries_with_registration_id', 'certificates_read',
                    'certificates_unreadable', 'certificates_naming_own_provider', 'providers_with_certificates',
                    'providers_named_in_a_certificate', 'parse_ms'])
        w.writerows(rows)
    print('lists %d, entries %d, records read %d, with registration identifier %d, certificates %d, unreadable %d, '
          'naming own provider %d, providers with certificates %d, named in one %d, slowest parse %.1f ms'
          % tuple([len(rows)] + [sum(r[i] for r in rows) for i in range(1, 9)] + [max(float(r[9]) for r in rows)]))
    v = mf.Verifier()
    v._adopt(mf.TrustedList(largest[2]))                # the enveloped signature of a national list is not measured
    chain = chains['X classical']                       # matches no entry, so every listed certificate is compared
    v.decide(chain, T2)
    times = []
    for _ in range(REPS):
        t = time.perf_counter()
        v.decide(chain, T2)
        times.append(time.perf_counter() - t)
    return [['lookup of a chain that matches no entry in the largest national list (%s, %d certificates), median'
             % (largest[0], largest[3]), '%.1f' % (1e6 * statistics.median(times)), 'us', len(times)]]


def main(schema_dir=None, list_dir=None):
    version = subprocess.run([OPENSSL, 'version'], capture_output=True, text=True).stdout.strip()
    print(version)
    with tempfile.TemporaryDirectory() as d:
        pki = PKI(d)
        ca, chains, keys = build_pki(pki)
        xml = {v: trusted_list(v, ca, chains) for v in (1, 2, 3, 4)}
        lists = {1: (xml[1], pki.sign(keys['operator_q'], xml[1])), 2: (xml[2], pki.sign(keys['operator_q'], xml[2])),
                 4: (xml[4], pki.sign(keys['operator_q'], xml[4])),
                 'forged_q': (xml[3], pki.sign(keys['attacker_q'], xml[3])),
                 'forged_ec': (xml[3], pki.sign(keys['operator_ec'], xml[3])),
                 'pinned_q': keys['operator_q']['pub'], 'pinned_ec': keys['operator_ec']['pub']}
        checked = schema_check(schema_dir, xml) if schema_dir else {v: 'not checked' for v in xml}
        print('schema errors of the test lists:', checked)

        rows, wrong, stops = [], 0, {c: [] for c in mf.CHECKS}
        for cid, scenario, chain_name, expected, declared in CASES:
            chain = chains[chain_name]
            full = run(scenario, chain, (), lists)
            single = [] if full.accept else [c for c in mf.CHECKS if run(scenario, chain, (c,), lists).accept]
            for c in single:
                stops[c].append(cid)
            together = run(scenario, chain, declared.split('+'), lists).accept if declared else None
            without = run(scenario, chain, ('mf',), lists)
            ok = (full.accept == expected and (together is None or together)
                  and ('+' in declared or not declared or declared in single))
            wrong += not ok
            rows.append([cid, SCENARIOS[scenario], chain_name, 'accept' if expected else 'reject',
                         'accept' if full.accept else 'reject', full.reason, full.source, declared,
                         '' if together is None else ('accept' if together else 'reject'), ' '.join(single),
                         'accept' if without.accept else 'reject', 'yes' if ok else 'NO'])
            print(rows[-1])
        with io.open(os.path.join(OUT, 'mf_reference_tests.csv'), 'w', encoding='utf-8', newline='') as f:
            w = csv.writer(f)
            w.writerow(['case', 'scenario', 'chain', 'expected', 'full_rule', 'reason', 'list_used', 'declared_checks',
                        'with_declared_checks_off', 'single_checks_admitting', 'without_mf', 'as_expected'])
            w.writerows(rows)
        with io.open(os.path.join(OUT, 'mf_reference_checks.csv'), 'w', encoding='utf-8', newline='') as f:
            w = csv.writer(f)
            w.writerow(['check', 'cases_admitted_when_only_this_check_is_off'])
            w.writerows([c, ' '.join(stops[c])] for c in mf.CHECKS)
        needed = all(stops[c] for c in mf.CHECKS)
        print('cases admitted when one check is off:', stops)
        print('every check stops at least one case on its own:', needed)

        v = mf.Verifier(pinned=lists['pinned_q'])
        v.refresh(*lists[2], T2)
        current = [chains[c] for _, s, c, _, _ in CASES if s == 'current']
        for c in current:
            v.decide(c, T2)
        times = []
        for c in current:
            for _ in range(REPS):
                t = time.perf_counter()
                v.decide(c, T2)
                times.append(time.perf_counter() - t)
        t = time.perf_counter()
        for _ in range(100):
            mf.TrustedList(xml[2])
        parse_ms = 10 * (time.perf_counter() - t)
        timing = [['OpenSSL', version, '', 1],
                  ['decision on the test list with the list adopted and path validation cached, median',
                   '%.1f' % (1e6 * statistics.median(times)), 'us', len(times)],
                  ['parsing the test list version 2', '%.2f' % parse_ms, 'ms', 100],
                  ['size of the test list version 2', len(xml[2]), 'bytes', 1],
                  ['size of the detached ML-DSA-65 signature of version 2', len(lists[2][1]), 'bytes', 1],
                  ['schema errors of the test lists (versions 1 to 4)', ', '.join(str(checked[v]) for v in xml), '', 4]]
        if list_dir:
            timing += national(list_dir, chains)
    with io.open(os.path.join(OUT, 'mf_reference_timing.csv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['measure', 'value', 'unit', 'n'])
        w.writerows(timing)
    for r in timing:
        print(r)
    print('cases %d, as expected %d' % (len(rows), len(rows) - wrong))
    return wrong + (not needed)


if __name__ == '__main__':
    sys.exit(1 if main(*sys.argv[1:3]) else 0)
