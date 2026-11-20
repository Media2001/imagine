# Public preparation only. Runtime has no download, bootstrap entrypoint or TCP listener.
ARG BASE_IMAGE
FROM ${BASE_IMAGE}
ENV DEBIAN_FRONTEND=noninteractive PYTHONDONTWRITEBYTECODE=1
RUN printf '#!/bin/sh\nexit 101\n' > /usr/sbin/policy-rc.d && chmod 755 /usr/sbin/policy-rc.d \
 && apt-get update \
 && apt-get install --no-install-recommends -y python3 bash ca-certificates php8.2-cli php8.2-fpm php8.2-mysql php8.2-curl php8.2-mbstring php8.2-xml php8.2-zip mariadb-server \
 && rm -rf /var/lib/apt/lists/* /var/lib/mysql/* /var/www/html/* \
 && mkdir -p /opt/staging /var/www/html /run/mysqld /run/staging-fpm \
 && chown 33:33 /var/www/html /run/staging-fpm \
 && dpkg-query -W > /opt/staging/packages.tsv
COPY worker/ /opt/staging/
COPY assets/ /opt/staging/assets/
RUN chmod 755 /opt/staging/entry.py /opt/staging/serve \
 && for name in importer neutraliser anonymiser verifier bascule novamira worker-bridge; do ln -s entry.py /opt/staging/$name; done \
 && for file in /opt/staging/*.php; do php -l "$file"; done \
 && python3 -B /opt/staging/test_worker.py
USER 33:33
WORKDIR /var/www/html
ENTRYPOINT ["/opt/staging/worker-bridge"]
