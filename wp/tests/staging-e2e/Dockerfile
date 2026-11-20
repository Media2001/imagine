ARG BASE_IMAGE=debian:bookworm-slim
FROM ${BASE_IMAGE}
LABEL org.imagine.synthetic-e2e="true"
# Public prerequisites only: no WordPress install/import during image build.
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    ca-certificates curl unzip python3 mariadb-server mariadb-client \
    php-cli php-mysql php-xml php-mbstring php-curl php-zip php-gd \
    && rm -rf /var/lib/apt/lists/*
COPY public/ /opt/public/
RUN cd /opt/public && sha256sum -c SHA256SUMS \
    && mkdir -p /opt/wordpress /opt/woocommerce /opt/e2e /report /run/mysqld \
    && unzip -q wordpress.zip -d /opt/wordpress \
    && unzip -q woocommerce.zip -d /opt/woocommerce \
    && cp wp-cli.phar /usr/local/bin/wp && chmod 755 /usr/local/bin/wp \
    && php -v > /opt/public/php-version.txt \
    && dpkg-query -W > /opt/public/packages.tsv
# No EXPOSE, no VOLUME, no server, no download at runtime.
CMD ["sleep", "infinity"]
