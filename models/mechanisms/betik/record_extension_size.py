#!/usr/bin/env python3
"""Size of the M-f record when it is carried in the extension containers of the ETSI list formats.

ek_yuk.py measures the bare record (87 bytes as an XML element and as a JSON member). Both list formats admit the
record only as an extension:
  - ETSI TS 119 612 V2.4.1, clause 5.4.5: TSP information extensions; in EU Member State trusted lists they shall not
    be made critical.
  - ETSI TS 119 602 V1.1.1, clause 6.5.5: TEInformationExtensions; the JSON schema of Annex A sets
    "additionalProperties": false on TrustedEntityInformation, so a new member is valid only inside this array.
The script measures the UTF-8 length of the record with its extension wrapper (entry that already carries
extensions) and with a new extension container (entry without extensions). Namespace prefixes, the member name and
the date are illustrative, as in ek_yuk.py.

Output: ../sonuc/record_extension_size.csv
"""
import csv
import io
import os

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RECORD_XML = '<pq:Expectation Scope="path" Sunset="2031-01-01T00:00:00Z">pq_required</pq:Expectation>'
RECORD_JSON_OBJECT = '{"state":"pq_required","scope":"path","sunset":"2031-01-01T00:00:00Z"}'

ROWS = [
    ('trusted list (XML)', 'bare record (as in ek_yuk.py)', RECORD_XML),
    ('trusted list (XML)', 'record in a non-critical extension',
     '<tsl:Extension Critical="false">' + RECORD_XML + '</tsl:Extension>'),
    ('trusted list (XML)', 'record in a new TSPInformationExtensions container',
     '<tsl:TSPInformationExtensions><tsl:Extension Critical="false">' + RECORD_XML
     + '</tsl:Extension></tsl:TSPInformationExtensions>'),
    ('LoTE (JSON)', 'bare member (as in ek_yuk.py)', ',"pqExpectation":' + RECORD_JSON_OBJECT),
    ('LoTE (JSON)', 'record as a further element of TEInformationExtensions',
     ',{"pqExpectation":' + RECORD_JSON_OBJECT + '}'),
    ('LoTE (JSON)', 'record in a new TEInformationExtensions array',
     ',"TEInformationExtensions":[{"pqExpectation":' + RECORD_JSON_OBJECT + '}]'),
]


def main():
    out = os.path.join(KOK, 'sonuc', 'record_extension_size.csv')
    with io.open(out, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['format', 'placement', 'bytes', 'text'])
        for fmt, placement, text in ROWS:
            w.writerow([fmt, placement, len(text.encode('utf-8')), text])
    for fmt, placement, text in ROWS:
        print('%-20s %-55s %4d' % (fmt, placement, len(text.encode('utf-8'))))


if __name__ == '__main__':
    main()
