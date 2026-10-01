# pq-a09-env-elixir:1.0 — Elixir ortamı (yedek adayı JOSE-031 guardian; "Diğer" dil grubu), Adım 9 görev 4a
# Taban: resmî Docker Hub imajı, özetle sabit. apt/apk KULLANILMAZ. Hex ve rebar3 resmî builds.hex.pm'den (anonim).
FROM elixir:1.20.4@sha256:86ff0019e9f70662462d7394406e8dee03ea399fe11825708614b2a5ce5368aa
LABEL pq.adim="a09" pq.gorev="4a" pq.imaj="pq-a09-env-elixir:1.0"
ENV MIX_HOME=/root/.mix HEX_HOME=/root/.hex
RUN set -eux; mix local.hex --force; mix local.rebar --force; echo "SURUM $(elixir --version | tr '\n' ' ')";     echo "SURUM hex $(mix hex.info 2>/dev/null | head -1)"; echo "SURUM erlang-crypto $(erl -noshell -eval 'io:format(\"~p\", [crypto:info_lib()]), halt().')"
