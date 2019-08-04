FROM wayarmy/alpine-kubectl as kube
FROM alpine/helm:2.14.3 as helm2
FROM alpine:3.7

COPY --from=kube /usr/bin/kubectl /usr/bin/kubectl
COPY --from=helm2 /usr/bin/helm /usr/bin/helm

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
    && apk add --no-cache --update python python3 git bash \
    && ln -s /usr/include/locale.h /usr/include/xlocale.h \
    && pip3 install --upgrade pip setuptools rdeploy \
    && curl -sSL https://sdk.cloud.google.com | sh \
    && mkdir /opt \
    && mv /root/google-cloud-sdk /opt/ \
    && rm -rf /var/cache/apk/* \
    && apk del .build-deps

ENV HOME /rehive/
ENV PATH $PATH:/opt/google-cloud-sdk/bin

COPY ./var/.config/gcloud /rehive/.config

RUN set -ex \
    && addgroup -S rehive \
    && git clone https://github.com/tesserarius/service-template /rehive/template \
    && adduser -S -G rehive -h /rehive rehive \
    && mkdir -p /rehive/.kube \
    && chown -R rehive:rehive /rehive/.config \
    && chown -R rehive:rehive /rehive/template \
    && chown -R rehive:rehive /rehive/.kube

USER rehive

WORKDIR /rehive/template
