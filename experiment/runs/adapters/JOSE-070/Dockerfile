# a10-jose-070:1 — firebase/php-jwt (composer.lock = experiment/environments/targets/JOSE-070/output; dist zips from Packagist/GitHub, anonymous)
FROM pq-a09-env-php:1.0
WORKDIR /opt/a
COPY composer.json composer.lock ./
RUN composer install --no-progress --prefer-dist --optimize-autoloader  && php -r '$l=json_decode(file_get_contents("composer.lock"),true); foreach($l["packages"] as $p) if($p["name"]=="firebase/php-jwt") echo ltrim($p["version"],"v");' > HEDEF_SURUM
COPY adaptor.php ortak.php ./
RUN sha256sum adaptor.php ortak.php | sha256sum | cut -d' ' -f1 > ADAPTOR_SHA256  && printf '#!/bin/sh\nexec php /opt/a/adaptor.php "$@"\n' > /usr/local/bin/adaptor && chmod +x /usr/local/bin/adaptor
ENV HEDEF_ID=JOSE-070
