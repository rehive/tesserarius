FROM wayarmy/alpine-kubectl as kube
FROM alpine:3.7

COPY --from=kube /usr/bin/kubectl /usr/bin/kubectl

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
    && apk add --no-cache --update python3 \
    && ln -s /usr/include/locale.h /usr/include/xlocale.h \
    && pip3 install --upgrade pip setuptools rdeploy /rehive/tesserarius/ \
    && curl -sSL https://sdk.cloud.google.com | sh \
    && apk del .build-deps \
    && rm -rf /var/cache/apk/*

ENV PATH $PATH:/root/google-cloud-sdk/bin

RUN mkdir -p /rehive/src /rehive/tesserarius \
    && addgroup -S rehive \
    && adduser -S -g rehive rehive
ENV HOME /rehive
USER rehive
ADD requirements.txt /rehive/tesserarius/requirements.txt
COPY . /rehive/tesserarius


WORKDIR /rehive/src
