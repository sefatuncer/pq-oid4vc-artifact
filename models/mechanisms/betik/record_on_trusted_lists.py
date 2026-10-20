#!/usr/bin/env python3
"""Adds the M-f record to real national trusted lists and checks them against the ETSI TS 119 612 V2.4.1 schema.

The question is whether the record of the profile fits the existing format and what it costs on the lists that are
in use. For every XML trusted list that the LOTL snapshot in data/ points to, the script
  1. inserts the record of record_extension_size.py into the TSP information extensions of every TSP entry
     (as a further non-critical extension where the entry already has extensions, otherwise in a new container),
     and declares the record namespace once on the root element,
  2. validates the original and the modified list against the official schema (19612_xsd.xsd of tag v2.4.1 of
     https://forge.etsi.org/rep/esi/x19_612_trusted_lists, with the W3C xml.xsd and xmldsig-core-schema.xsd),
  3. reports the number of TSP entries, the added bytes and their share of the list size.
The insertion invalidates the list signature, which the operator would recompute. Only the format is checked.

Usage:
  record_on_trusted_lists.py fetch   <list_dir>                 download the XML lists of the LOTL snapshot
  record_on_trusted_lists.py measure <list_dir> <schema_dir>    write ../sonuc/record_on_trusted_lists.csv
  record_on_trusted_lists.py controls <list.xml> <schema_dir>   negative controls, ../sonuc/record_on_trusted_lists_controls.csv
The schema directory holds 19612_xsd.xsd, xml.xsd and xmldsig-core-schema.xsd. Requires xmlschema (pure Python,
tested with 3.4.3). The lists of the recorded run were retrieved on 2026-10-20 (UTC); 28 of the 31 XML lists could be
retrieved.
The downloaded lists are third-party data and are not stored in the repository. Their URLs, sizes and SHA-256
digests are written to ../sonuc/record_on_trusted_lists_manifest.csv.
"""
import csv
import datetime
import hashlib
import io
import os
import re
import sys
import urllib.request

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(KOK))
LOTL = os.path.join(REPO, 'data', 'eu-lotl_seq394.xml')
OUT = os.path.join(KOK, 'sonuc', 'record_on_trusted_lists.csv')
MANIFEST = os.path.join(KOK, 'sonuc', 'record_on_trusted_lists_manifest.csv')

RECORD = '<pq:Expectation Scope="path" Sunset="2031-01-01T00:00:00Z">pq_required</pq:Expectation>'
PQ_NS = ' xmlns:pq="urn:example:pq-expectation"'
TSL_NS = 'http://uri.etsi.org/02231/v2#'


def xml_pointers():
    t = io.open(LOTL, encoding='utf-8').read()
    out = []
    for block in re.findall(r'<(?:\w+:)?OtherTSLPointer>(.*?)</(?:\w+:)?OtherTSLPointer>', t, re.S):
        loc = re.search(r'<(?:\w+:)?TSLLocation>([^<]+)<', block)
        mime = re.search(r'MimeType>([^<]+)<', block)
        terr = re.search(r'SchemeTerritory>([^<]+)<', block)
        if loc and mime and 'xml' in mime.group(1).lower() and 'eu-lotl' not in loc.group(1):
            out.append((terr.group(1) if terr else '', loc.group(1).strip()))
    return out


def fetch(list_dir):
    os.makedirs(list_dir, exist_ok=True)
    rows = []
    for terr, url in xml_pointers():
        name = '%s.xml' % terr
        path = os.path.join(list_dir, name)
        status = 'ok'
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            data = urllib.request.urlopen(req, timeout=60).read()
            io.open(path, 'wb').write(data)
        except Exception as e:  # recorded, not fatal
            status = 'failed: %s' % type(e).__name__
            data = b''
        rows.append([terr, url, status, len(data), hashlib.sha256(data).hexdigest() if data else '',
                     datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')])
        print(terr, status, len(data))
    with io.open(MANIFEST, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['territory', 'url', 'status', 'bytes', 'sha256', 'fetched_utc'])
        w.writerows(rows)


def tsl_prefix(text):
    m = re.search(r'<(\w+:)?TrustServiceStatusList[\s>]', text)
    return m.group(1) or ''


def insert_records(text):
    """Returns the modified text, the number of TSP entries and how many already had extensions."""
    p = tsl_prefix(text)
    root = re.search(r'<%sTrustServiceStatusList' % re.escape(p), text)
    text = text[:root.end()] + PQ_NS + text[root.end():]
    open_re = re.compile(r'<%sTSPInformation(?=[\s>])[^>]*>' % re.escape(p))
    close_tag = '</%sTSPInformation>' % p
    ext_close = '</%sTSPInformationExtensions>' % p
    ext = '<%sExtension Critical="false">%s</%sExtension>' % (p, RECORD, p)
    container = '<%sTSPInformationExtensions>%s%s' % (p, ext, ext_close)
    out, pos, n, had = [], 0, 0, 0
    while True:
        m = open_re.search(text, pos)
        if not m:
            break
        end = text.index(close_tag, m.end())
        block = text[m.end():end]
        i = block.rfind(ext_close)
        if i >= 0:
            block = block[:i] + ext + block[i:]
            had += 1
        else:
            block = block + container
        out.append(text[pos:m.end()])
        out.append(block)
        out.append(close_tag)
        pos = end + len(close_tag)
        n += 1
    out.append(text[pos:])
    return ''.join(out), n, had


def load_schema(schema_dir):
    import xmlschema
    src = io.open(os.path.join(schema_dir, '19612_xsd.xsd'), encoding='utf-8').read()
    src = src.replace('schemaLocation="http://www.w3.org/2001/xml.xsd"', 'schemaLocation="xml.xsd"')
    src = src.replace('schemaLocation="http://www.w3.org/TR/2008/REC-xmldsig-core-20080610/xmldsig-core-schema.xsd"',
                      'schemaLocation="xmldsig-core-schema.xsd"')
    local = os.path.join(schema_dir, '19612_xsd_local.xsd')
    io.open(local, 'w', encoding='utf-8').write(src)
    return xmlschema.XMLSchema10(local)


def errors(schema, text):
    try:
        return sum(1 for _ in schema.iter_errors(io.StringIO(text)))
    except Exception as e:
        return 'parse error: %s' % type(e).__name__


def signature_bytes(text):
    m = re.search(r'<(?:\w+:)?SignatureValue[^>]*>([^<]+)<', text)
    return len(re.sub(r'\s', '', m.group(1))) if m else ''


def measure(list_dir, schema_dir):
    schema = load_schema(schema_dir)
    rows = []
    for name in sorted(os.listdir(list_dir)):
        if not name.endswith('.xml'):
            continue
        raw = io.open(os.path.join(list_dir, name), 'rb').read()
        text = raw.decode('utf-8-sig')
        mod, n, had = insert_records(text)
        added = len(mod.encode('utf-8')) - len(text.encode('utf-8'))
        rows.append([name[:-4], len(raw), n, had, added, '%.3f' % (100.0 * added / len(raw)),
                     errors(schema, text), errors(schema, mod), signature_bytes(text)])
        print(rows[-1])
    with io.open(OUT, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['territory', 'list_bytes', 'tsp_entries', 'entries_with_extensions', 'added_bytes',
                    'added_percent', 'schema_errors_original', 'schema_errors_modified',
                    'signature_value_base64_chars'])
        w.writerows(rows)
    ok = [r for r in rows if r[6] == 0]
    print('lists: %d, valid originals: %d, valid after insertion among them: %d' %
          (len(rows), len(ok), sum(1 for r in ok if r[7] == 0)))
    print('TSP entries: %d, added bytes: %d, list bytes: %d' %
          (sum(r[2] for r in rows), sum(r[4] for r in rows), sum(r[1] for r in rows)))


def controls(list_path, schema_dir):
    """Negative controls: the schema must reject a misplaced record, so that a pass is not vacuous."""
    schema = load_schema(schema_dir)
    text = io.open(list_path, 'rb').read().decode('utf-8-sig')
    p = tsl_prefix(text)
    good, n, _ = insert_records(text)
    no_critical = good.replace('<%sExtension Critical="false">' % p, '<%sExtension>' % p, 1)
    i = text.index('</%sTSPInformation>' % p)
    outside = text[:i] + RECORD + text[i:]
    outside = outside.replace('TrustServiceStatusList', 'TrustServiceStatusList' + PQ_NS, 1)
    rows = [['record in a non-critical extension of every entry', errors(schema, good)],
            ['first extension without the required Critical attribute', errors(schema, no_critical)],
            ['record directly in TSPInformation, outside the extension container', errors(schema, outside)]]
    out = os.path.join(KOK, 'sonuc', 'record_on_trusted_lists_controls.csv')
    with io.open(out, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['list', 'variant', 'schema_errors'])
        for v, e in rows:
            w.writerow([os.path.basename(list_path), v, e])
            print(v, e)


if __name__ == '__main__':
    if len(sys.argv) >= 3 and sys.argv[1] == 'fetch':
        fetch(sys.argv[2])
    elif len(sys.argv) >= 4 and sys.argv[1] == 'measure':
        measure(sys.argv[2], sys.argv[3])
    elif len(sys.argv) >= 4 and sys.argv[1] == 'controls':
        controls(sys.argv[2], sys.argv[3])
    else:
        sys.exit(__doc__)
