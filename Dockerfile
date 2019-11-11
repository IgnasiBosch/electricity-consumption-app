FROM alpine:3.10

ARG SERVICE_USER="app-user"
ARG VER_PYTHON="3.7"
ARG VER_PIP="19.1.1"
ARG VER_PIPENV="2018.11.26"


# Install main packages.
RUN set -o nounset -o errexit -o xtrace -o verbose \
    && apk add --no-cache \
        bash \
        curl \
        vim \
        ca-certificates \
        libffi-dev \
        python3 \
    && python3 --version \
    && python3 -c "import os, sys;assert sys.version.startswith(os.environ.get('VER_PYTHON'))"

COPY files/s6-overlay-amd64.tar.gz.sha512 /tmp

RUN set -o nounset -o errexit -o xtrace -o verbose \
    && cd /tmp \
    && curl -sSL -O https://github.com/just-containers/s6-overlay/releases/download/v1.19.1.1/s6-overlay-amd64.tar.gz \
    && sha512sum -c s6-overlay-amd64.tar.gz.sha512 \
    && tar zxf s6-overlay-amd64.tar.gz -C / \
    && rm s6-overlay-amd64.tar.gz \
    \
    # - user/group config
    && addgroup -S -g 5000 ${SERVICE_USER} \
    && adduser -D -S -h /app -s /sbin/nologin -G ${SERVICE_USER} -u 5000 ${SERVICE_USER}

ENV S6_BEHAVIOUR_IF_STAGE2_FAILS=2 \
    SVC_DIR=/etc/services.d



# Install python dependencies.

WORKDIR /app
COPY Pipfile /app/Pipfile
COPY Pipfile.lock /app/Pipfile.lock
RUN set -o nounset -o errexit -o xtrace -o verbose \
    && apk add --no-cache --virtual .fetch-deps \
        python3-dev \
        gcc \
        g++ \
        musl-dev \
        make \
    && pip3 install \
        pip==${VER_PIP} \
        pipenv==${VER_PIPENV} \
        envtpl==0.6.0 \
    && pipenv install --dev --system --deploy \
    && apk del -q --purge .fetch-deps


WORKDIR /app
COPY . /app

RUN set -o nounset -o errexit -o xtrace -o verbose \
    \
    && addgroup -S app_user \
    && adduser -D -S -h /app -s /sbin/nologin -G app_user app_user \
    \
    && mkdir ${SVC_DIR}/app \
    && cp files/app-run.sh ${SVC_DIR}/app/run

ENTRYPOINT /init
