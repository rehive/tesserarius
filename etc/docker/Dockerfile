FROM alpine:3.7

ADD requirements.txt /rehive/tesserarius/requirements.txt
COPY . /rehive/tesserarius

RUN set -ex \
    && apk add --no-cache --virtual \
        .build-deps \
        g++ \
        python3-dev \
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
    && pip3 install --upgrade pip setuptools \
    && pip3 install rdeploy cookiecutter \
    && pip3 install --no-cache-dir -r /rehive/tesserarius/requirements.txt \
    && pip3 install /rehive/tesserarius/ \
    && cookiecutter --no-input https://github.com/rehive/service-framework \
    && apk del .build-deps \
    && rm -rf /var/cache/apk/*

RUN mkdir -p /rehive/src /rehive/tesserarius \
    && addgroup -S rehive \
    && adduser -S -g rehive rehive
ENV HOME /rehive
USER rehive

WORKDIR /rehive/src
ENTRYPOINT ["tesserarius"]
