#!/usr/bin/env python3
"""Extracts the external test vectors from the corpus texts (Step 9b).

Sources (spec-corpus/metin, MANIFEST ids):
  * RFC9964   Appendix A.1 (JOSE: ML-DSA-44/65/87) and A.2 (COSE: raw fields)
  * JOSECOMP  draft-ietf-jose-pq-composite-sigs-04 Appendix A.1 (JOSE, 6 composite alg)

The texts use two different line-folding styles:
  * JOSECOMP: RFC 8792 single-backslash ('\\') line folding
  * RFC9964 : string values continue at the start of the line (without indentation)
Both are resolved by dropping spaces, line breaks and backslashes inside the JSON strings
(base64url and hex values do not contain these characters).

Usage: python dis_vektorler.py <corpus_text_folder> <output_folder>
"""
import hashlib
import json
import os
import re
import sys


def _unwrap_json_text(txt: str) -> str:
    """Cleans the line-folding leftovers inside JSON strings."""
    out = []
    in_str = False
    i = 0
    while i < len(txt):
        c = txt[i]
        if in_str:
            if c == '"':
                in_str = False
                out.append(c)
            elif c in '\\\n\r \t':
                pass  # line-folding leftover
            else:
                out.append(c)
        else:
            if c == '"':
                in_str = True
            out.append(c)
        i += 1
    return ''.join(out)


def _blocks_between(lines, start_pat, end_pat):
    s = next(i for i, l in enumerate(lines) if re.match(start_pat, l))
    e = next(i for i, l in enumerate(lines) if i > s and re.match(end_pat, l))
    return s, e


def _json_objects_with_captions(lines, s, e):
    """Returns the '{ ... }' + 'Figure N: name' blocks in the range [s,e)."""
    res = []
    i = s
    while i < e:
        if lines[i].strip() == '{':
            # matching close: '}' at the same indentation level (counter for nested objects)
            depth = 0
            j = i
            buf = []
            while j < e:
                l = lines[j]
                if 'NOTE:' in l and 'line wrapping' in l:
                    j += 1
                    continue
                buf.append(l)
                # count only the braces outside strings
                t = re.sub(r'"[^"]*"', '""', l)
                depth += t.count('{') - t.count('}')
                j += 1
                if depth == 0:
                    break
            cap = None
            k = j
            while k < e and k < j + 12:
                m = re.match(r'\s+Figure (\d+): (\S.*)$', lines[k])
                if m:
                    cap = (int(m.group(1)), m.group(2).strip())
                    break
                k += 1
            text = _unwrap_json_text('\n'.join(buf))
            obj = json.loads(text)
            res.append({'figure': cap, 'lines': [i + 1, j], 'obj': obj})
            i = j
        else:
            i += 1
    return res


def main(src_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    rapor = {'kaynaklar': {}, 'vektorler': []}

    # ---------------- RFC 9964 ----------------
    p = os.path.join(src_dir, 'RFC9964.txt')
    raw = open(p, 'rb').read()
    rapor['kaynaklar']['RFC9964'] = {'dosya': 'RFC9964.txt', 'sha256': hashlib.sha256(raw).hexdigest()}
    lines = raw.decode('utf-8').split('\n')
    s, e = _blocks_between(lines, r'^A\.1\.\s+JOSE', r'^A\.2\.\s+COSE')
    for b in _json_objects_with_captions(lines, s, e):
        o = b['obj']
        v = {'id': 'RFC9964-JOSE-' + o['jwk']['alg'], 'kaynak': 'RFC9964', 'bolum': 'Appendix A.1',
             'figure': b['figure'], 'satirlar': b['lines'], 'tur': 'jose-mldsa', 'veri': o}
        rapor['vektorler'].append(v)
    s2 = next(i for i, l in enumerate(lines) if re.match(r'^A\.2\.\s+COSE', l))
    e2 = next(i for i, l in enumerate(lines) if i > s2 and re.match(r'^(Acknowledgements|Authors\' Addresses)', l))
    for b in _json_objects_with_captions(lines, s2, e2):
        o = b['obj']
        name = b['figure'][1] if b['figure'] else '?'
        v = {'id': 'RFC9964-COSE-' + name.replace('_', '-'), 'kaynak': 'RFC9964', 'bolum': 'Appendix A.2',
             'figure': b['figure'], 'satirlar': b['lines'], 'tur': 'cose-mldsa-ham', 'veri': o}
        rapor['vektorler'].append(v)

    # ---------------- JOSECOMP (-04) ----------------
    p = os.path.join(src_dir, 'JOSECOMP.txt')
    raw = open(p, 'rb').read()
    rapor['kaynaklar']['JOSECOMP'] = {'dosya': 'JOSECOMP.txt', 'sha256': hashlib.sha256(raw).hexdigest(),
                                      'surum': 'draft-ietf-jose-pq-composite-sigs-04'}
    lines = raw.decode('utf-8').split('\n')
    s, e = _blocks_between(lines, r'^A\.1\.\s+JOSE', r'^A\.2\.\s+COSE')
    for b in _json_objects_with_captions(lines, s, e):
        o = b['obj']
        v = {'id': 'JOSECOMP04-JOSE-' + o['jwk']['alg'], 'kaynak': 'JOSECOMP', 'bolum': 'Appendix A.1',
             'figure': b['figure'], 'satirlar': b['lines'], 'tur': 'jose-composite', 'veri': o}
        rapor['vektorler'].append(v)

    for v in rapor['vektorler']:
        fn = os.path.join(out_dir, v['id'] + '.json')
        with open(fn, 'w', encoding='utf-8') as f:
            json.dump(v, f, indent=1, ensure_ascii=False)
            f.write('\n')
    ozet = {'kaynaklar': rapor['kaynaklar'],
            'vektorler': [{'id': v['id'], 'figure': v['figure'], 'satirlar': v['satirlar'],
                           'alanlar': sorted(v['veri'].keys())} for v in rapor['vektorler']]}
    with open(os.path.join(out_dir, '00-OZET.json'), 'w', encoding='utf-8') as f:
        json.dump(ozet, f, indent=1, ensure_ascii=False)
        f.write('\n')
    for v in rapor['vektorler']:
        print(v['id'], v['figure'], sorted(v['veri'].keys()))
    print('toplam', len(rapor['vektorler']))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
