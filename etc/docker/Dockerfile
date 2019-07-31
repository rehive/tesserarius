# FROM wayarmy/alpine-kubectl as kube
FROM alpine:3.7

# COPY --from=kube /usr/bin/kubectl /usr/bin/kubectl

ADD requirements.txt /rehive/tesserarius/requirements.txt
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
    && apk add --no-cache --update python3 \
    && ln -s /usr/include/locale.h /usr/include/xlocale.h \
    && pip3 install --upgrade pip setuptools rdeploy /rehive/tesserarius/ \
    && curl -sSL https://sdk.cloud.google.com | sh \
    && mkdir /opt \
    && mv /root/google-cloud-sdk /opt/ \
    && rm -rf /var/cache/apk/*

ENV PATH $PATH:/opt/google-cloud-sdk/bin
ENV HOME /rehive/

WORKDIR /rehive/tesserarius
