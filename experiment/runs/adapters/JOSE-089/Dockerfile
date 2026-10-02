# a10-jose-089:1 — json-jwt 1.17.2 (Gemfile.lock = experiment/environments/targets/JOSE-089/output, CHECKSUMS included)
FROM pq-a09-env-ruby:1.0
WORKDIR /opt/a
COPY Gemfile Gemfile.lock ./
RUN bundle config set --local path vendor/bundle && bundle config set --local lockfile_checksums true \
 && bundle config set --local frozen true && bundle install && bundle exec ruby -e 'puts Gem.loaded_specs["json-jwt"].version' > HEDEF_SURUM
COPY adaptor.rb ortak.rb ./
RUN sha256sum adaptor.rb ortak.rb | sha256sum | cut -d' ' -f1 > ADAPTOR_SHA256 \
 && printf '#!/bin/sh\ncd /opt/a && exec bundle exec ruby /opt/a/adaptor.rb "$@"\n' > /usr/local/bin/adaptor && chmod +x /usr/local/bin/adaptor
ENV HEDEF_ID=JOSE-089
