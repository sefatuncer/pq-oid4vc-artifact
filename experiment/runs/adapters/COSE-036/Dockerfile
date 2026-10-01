# a10-cose-036:1 — wolfCOSE @ f907071b10127f3ae2dd7719749a91b039ff04a1 (sürüm yok → CERCEVE son_commit_sha; ÖK madde 14)
# wolfSSL v5.9.2-stable (ac01707f552c) README "Full Build" bayraklarıyla (--enable-mldsa dahil); ortam kaydıyla aynı
# (experiment/environments/hedefler/COSE-036/kur.sh). GitHub anonim git; GPL-3.0: yalnız ölçülür, dağıtılmaz.
# Ölçüm yapılandırması: belgeli derleme makrosu WOLFCOSE_ENABLE_DEPRECATED_ALGS (docs/Macros.md "Deprecated Algorithm IDs
# (RFC 9864)"; Makefile EXTRA_CFLAGS kancası) — batarya ES256'yı RFC 9053 kimliği -7, EdDSA'yı -8 ile taşır. Kod değişmez.
FROM pq-a09-env-c:1.0
ARG WSHA=ac01707f552c611fbd135cc723b2682b3e7f80f2
ARG CSHA=f907071b10127f3ae2dd7719749a91b039ff04a1
RUN mkdir -p /tmp/wolfssl && cd /tmp/wolfssl && git init -q . && git remote add origin https://github.com/wolfSSL/wolfssl.git \
 && git fetch -q --depth 1 origin $WSHA && git checkout -q FETCH_HEAD && test "$(git rev-parse HEAD)" = "$WSHA" \
 && ./autogen.sh >/dev/null && ./configure --prefix=/usr/local --enable-ecc --enable-ed25519 --enable-ed448 --enable-curve25519 \
    --enable-aesgcm --enable-aesccm --enable-sha384 --enable-sha512 --enable-keygen --enable-rsapss --enable-chacha \
    --enable-poly1305 --enable-mldsa --enable-lms --enable-hkdf --enable-aeskeywrap >/tmp/wconf.log 2>&1 \
 && make -j8 >/tmp/wmake.log 2>&1 && make install >/dev/null && ldconfig && rm -rf /tmp/wolfssl
RUN mkdir -p /opt/wolfcose && cd /opt/wolfcose && git init -q . && git remote add origin https://github.com/wolfssl/wolfcose.git \
 && git fetch -q --depth 1 origin $CSHA && git checkout -q FETCH_HEAD && test "$(git rev-parse HEAD)" = "$CSHA" \
 && make -j8 all >/tmp/cmake.log 2>&1 && make clean >/dev/null \
 && make -j8 shared EXTRA_CFLAGS=-DWOLFCOSE_ENABLE_DEPRECATED_ALGS >/tmp/cshared.log 2>&1 \
 && ls -la /opt/wolfcose/*.so*
WORKDIR /opt/a
COPY kopru.c adaptor.py ./
# Köprü yalnız wolfCOSE genel API'sini çağırır; wolfCOSE'un belgeli `make shared` hedefi (Makefile L184) kullanılır.
RUN gcc -std=gnu11 -O2 -shared -fPIC -DHAVE_ANONYMOUS_INLINE_AGGREGATES=1 -DWOLFCOSE_ENABLE_DEPRECATED_ALGS -I/opt/wolfcose/include -I/usr/local/include \
      kopru.c -L/opt/wolfcose -lwolfcose -L/usr/local/lib -lwolfssl -Wl,-rpath,/opt/wolfcose:/usr/local/lib -o /opt/a/libkopru.so \
 && echo "git:f907071b1012" > HEDEF_SURUM \
 && cat kopru.c adaptor.py | sha256sum | cut -d' ' -f1 > ADAPTOR_SHA256 \
 && printf '#!/bin/sh\nexec python3 /opt/a/adaptor.py "$@"\n' > /usr/local/bin/adaptor && chmod +x /usr/local/bin/adaptor
ENV HEDEF_ID=COSE-036
