"""Asgari CBOR (RFC 8949) kodlayici/cozucu — COSE vektorleri icin.

Kodlama: belirlenimci (RFC 8949 §4.2.1 "core deterministic"): en kisa tamsayi/uzunluk bicimi, belirli
uzunluklar, harita anahtarlari kodlanmis baytlarina gore sozluksel sirali (canonical=True). canonical=False
ekleme sirasini korur (dis test vektorlerini — ornegin RFC 9964 Ek A COSE_Key — birebir yeniden uretmek icin).
Cozme: yalniz belirli uzunluk; artik bayt reddi; etiketler Tag nesnesi olarak doner. Desteklenen turler:
uint/nint, bstr, tstr, dizi, harita, etiket, false/true/null.
"""


class Tag:
    __slots__ = ('tag', 'value')

    def __init__(self, tag, value):
        self.tag = tag
        self.value = value

    def __eq__(self, other):
        return isinstance(other, Tag) and self.tag == other.tag and self.value == other.value

    def __repr__(self):
        return 'Tag(%d, %r)' % (self.tag, self.value)


class CBORError(ValueError):
    pass


def _head(major, n):
    if n < 24:
        return bytes([(major << 5) | n])
    if n < 0x100:
        return bytes([(major << 5) | 24, n])
    if n < 0x10000:
        return bytes([(major << 5) | 25]) + n.to_bytes(2, 'big')
    if n < 0x100000000:
        return bytes([(major << 5) | 26]) + n.to_bytes(4, 'big')
    if n < 0x10000000000000000:
        return bytes([(major << 5) | 27]) + n.to_bytes(8, 'big')
    raise CBORError('tamsayi cok buyuk')


def encode(obj, canonical=True) -> bytes:
    if obj is False:
        return b'\xf4'
    if obj is True:
        return b'\xf5'
    if obj is None:
        return b'\xf6'
    if isinstance(obj, int):
        return _head(0, obj) if obj >= 0 else _head(1, -1 - obj)
    if isinstance(obj, (bytes, bytearray)):
        return _head(2, len(obj)) + bytes(obj)
    if isinstance(obj, str):
        b = obj.encode('utf-8')
        return _head(3, len(b)) + b
    if isinstance(obj, (list, tuple)):
        return _head(4, len(obj)) + b''.join(encode(x, canonical) for x in obj)
    if isinstance(obj, dict):
        items = [(encode(k, canonical), encode(v, canonical)) for k, v in obj.items()]
        if canonical:
            items.sort(key=lambda kv: kv[0])
            for a, b in zip(items, items[1:]):
                if a[0] == b[0]:
                    raise CBORError('yinelenen harita anahtari')
        return _head(5, len(items)) + b''.join(k + v for k, v in items)
    if isinstance(obj, Tag):
        return _head(6, obj.tag) + encode(obj.value, canonical)
    raise CBORError('desteklenmeyen tur: %s' % type(obj).__name__)


def _read_arg(b, i, ai):
    if ai < 24:
        return ai, i
    if ai == 24:
        n, i2 = b[i], i + 1
        if n < 24:
            raise CBORError('en kisa olmayan bicim')
        return n, i2
    ln = {25: 2, 26: 4, 27: 8}.get(ai)
    if ln is None:
        raise CBORError('belirsiz uzunluk ya da ayrilmis ek bilgi desteklenmez')
    if i + ln > len(b):
        raise CBORError('kesik veri')
    n = int.from_bytes(b[i:i + ln], 'big')
    if n < {2: 0x100, 4: 0x10000, 8: 0x100000000}[ln]:
        raise CBORError('en kisa olmayan bicim')
    return n, i + ln


def _dec(b, i):
    if i >= len(b):
        raise CBORError('kesik veri')
    ib = b[i]
    major, ai = ib >> 5, ib & 0x1F
    i += 1
    if major == 7:
        if ai == 20:
            return False, i
        if ai == 21:
            return True, i
        if ai == 22:
            return None, i
        raise CBORError('desteklenmeyen basit deger/ondalik')
    n, i = _read_arg(b, i, ai)
    if major == 0:
        return n, i
    if major == 1:
        return -1 - n, i
    if major in (2, 3):
        if i + n > len(b):
            raise CBORError('kesik dizgi')
        v = bytes(b[i:i + n])
        return (v if major == 2 else v.decode('utf-8')), i + n
    if major == 4:
        out = []
        for _ in range(n):
            x, i = _dec(b, i)
            out.append(x)
        return out, i
    if major == 5:
        out = {}
        for _ in range(n):
            k, i = _dec(b, i)
            v, i = _dec(b, i)
            kk = k if not isinstance(k, list) else tuple(k)
            if kk in out:
                raise CBORError('yinelenen harita anahtari')
            out[kk] = v
        return out, i
    if major == 6:
        v, i = _dec(b, i)
        return Tag(n, v), i
    raise CBORError('bilinmeyen ana tur')


def decode(b: bytes):
    v, i = _dec(bytes(b), 0)
    if i != len(b):
        raise CBORError('artik bayt')
    return v


def is_canonical(b: bytes) -> bool:
    try:
        return encode(decode(b), canonical=True) == bytes(b)
    except CBORError:
        return False
