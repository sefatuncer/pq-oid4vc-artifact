# pq-a09-env-elixir:1.0 — Elixir environment (reserve candidate JOSE-031 guardian; language group "Other"), Step 9 task 4a
# Base: official Docker Hub image, pinned by digest. apt/apk are NOT used. Hex and rebar3 from the official builds.hex.pm (anonymous).
FROM elixir:1.20.4@sha256:86ff0019e9f70662462d7394406e8dee03ea399fe11825708614b2a5ce5368aa
LABEL pq.adim="a09" pq.gorev="4a" pq.imaj="pq-a09-env-elixir:1.0"
ENV MIX_HOME=/root/.mix HEX_HOME=/root/.hex
RUN set -eux; mix local.hex --force; mix local.rebar --force; echo "SURUM $(elixir --version | tr '\n' ' ')";     echo "SURUM hex $(mix hex.info 2>/dev/null | head -1)"; echo "SURUM erlang-crypto $(erl -noshell -eval 'io:format(\"~p\", [crypto:info_lib()]), halt().')"
