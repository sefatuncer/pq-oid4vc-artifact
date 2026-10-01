# a10-jose-031:1 — guardian 2.5.0 (doğrulamayı erlang-jose 1.11.12'ye devreder); hex.pm anonim, mix.lock ile sabit
FROM pq-a09-env-elixir:1.0
WORKDIR /opt/a
ENV MIX_ENV=prod
COPY mix.exs mix.lock ./
RUN mix deps.get --check-locked && mix deps.compile
COPY lib lib
RUN mix compile && echo "2.5.0" > HEDEF_SURUM \
 && cat lib/*.ex | sha256sum | cut -d' ' -f1 > ADAPTOR_SHA256 \
 && printf '#!/bin/sh\ncd /opt/a && exec mix run --no-compile --no-deps-check -e "A10.Adaptor.main(System.argv())" -- "$@"\n' > /usr/local/bin/adaptor && chmod +x /usr/local/bin/adaptor
ENV HEDEF_ID=JOSE-031
