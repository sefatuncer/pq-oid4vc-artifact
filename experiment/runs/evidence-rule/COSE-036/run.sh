#!/bin/sh
# COSE-036 second attempt: compile and run attempt.c in pq-a09-env-c:1.0 (no network).
# /w/wolfssl-inst: wolfSSL v5.9.2-stable (ac01707f552c) installed with the flags of the installation record.
# /w/build: libwolfcose.a and include/ of wolfCOSE f907071b1012 built with
#           make all EXTRA_CFLAGS=-DWOLFCOSE_ENABLE_DEPRECATED_ALGS
set -e
cd /w
gcc --version | head -1
sha256sum build/libwolfcose.a
gcc -std=gnu11 -Wall -DHAVE_ANONYMOUS_INLINE_AGGREGATES=1 -DWOLFCOSE_ENABLE_DEPRECATED_ALGS \
    -I build/include -isystem wolfssl-inst/include attempt.c build/libwolfcose.a \
    -L wolfssl-inst/lib -lwolfssl -lm -o /tmp/attempt
LD_LIBRARY_PATH=/w/wolfssl-inst/lib /tmp/attempt
# B4 line counts: lines between the markers, blank lines and comment lines excluded
for t in L4m L4c; do
  n=$(awk -v t="$t" '$0 ~ "B4-BEGIN "t {f=1; next} $0 ~ "B4-END "t {f=0} f' attempt.c \
      | grep -vE '^[[:space:]]*$|^[[:space:]]*(/\*|\*|//)' | wc -l)
  echo "B4 lines $t: $n"
done
