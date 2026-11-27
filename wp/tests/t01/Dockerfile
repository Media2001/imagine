# This file is built only by preparer-image.ps1 in its minimal temporary context.
FROM composer:2 AS composer
FROM php:8.2-cli
RUN apt-get update \
    && apt-get install -y --no-install-recommends libonig-dev libxml2-dev unzip python3 \
    && docker-php-ext-install -j2 mbstring dom xml xmlwriter \
    && rm -rf /var/lib/apt/lists/*
COPY --from=composer /usr/bin/composer /usr/local/bin/composer
ENV COMPOSER_ALLOW_SUPERUSER=1 COMPOSER_HOME=/tmp/composer
COPY packages/ /opt/t01/
COPY verifier-image.php /opt/t01/verifier-image.php
RUN set -eu; for package in /opt/t01/*/composer.json; do \
      cd "$(dirname "$package")"; \
      composer install --no-interaction --no-progress --prefer-dist --no-scripts --no-plugins; \
    done; \
    php /opt/t01/verifier-image.php; \
    rm -rf /tmp/composer /root/.composer
LABEL org.imagine.t01-image="1"
USER 65534:65534
ENTRYPOINT ["php"]
CMD ["/opt/t01/verifier-image.php"]
