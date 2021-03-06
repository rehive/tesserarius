FROM wayarmy/alpine-kubectl as kube
FROM alpine:3.7

COPY --from=kube /usr/bin/kubectl /usr/bin/kubectl
COPY . /rehive/tesserarius

RUN set -ex \
    && apk add --no-cache --virtual \
        .build-deps \
        g++ \
        python3-dev \
        curl \
        which \
        bash \
        py3-virtualenv \
        libffi-dev \
        openssl-dev \
        make \
        libc-dev \
        musl-dev \
        linux-headers \
        pcre-dev \
        zlib-dev \
        jpeg-dev \
        gfortran \
        git \
        curl-dev \
    && apk add --no-cache --update python3 git bash \
    && ln -s /usr/include/locale.h /usr/include/xlocale.h \
    && pip3 install --upgrade pip setuptools rdeploy /rehive/tesserarius/ \
    && curl -sSL https://sdk.cloud.google.com | sh \
    && mkdir /opt \
    && mv /root/google-cloud-sdk /opt/ \
    && rm -rf /var/cache/apk/* \
    && apk del .build-deps

ENV HOME /rehive/
ENV PATH $PATH:/opt/google-cloud-sdk/bin

RUN set -ex \
    && addgroup -S rehive \
    && adduser -S -G rehive -h /rehive rehive \
    && mkdir -p /rehive/.kube /rehive/tesserarius/var/tesserarius \
    && chown -R rehive:rehive /rehive/.kube \
    && chown -R rehive:rehive /rehive/tesserarius

COPY --chown=rehive:rehive ./var/.config/gcloud /rehive/.config

USER rehive

WORKDIR /rehive/tesserarius
