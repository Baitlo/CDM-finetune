FROM python:3.8

WORKDIR /packages

RUN wget https://registry.npmmirror.com/-/binary/node/latest-v16.x/node-v16.13.1-linux-x64.tar.gz \
    && tar -xvf node-v16.13.1-linux-x64.tar.gz \
    && mv node-v16.13.1-linux-x64 /usr/local/nodejs \
    && ln -s /usr/local/nodejs/bin/node /usr/local/bin \
    && ln -s /usr/local/nodejs/bin/npm /usr/local/bin \
    && node -v

RUN apt-get update \
    && apt-get install -y texlive-full \
    && pdflatex -v

ARG IM_VER=7.1.1-2
RUN apt-get update && apt-get install -y wget xz-utils build-essential ca-certificates \
    && wget -O ImageMagick.tar.xz https://imagemagick.org/archive/releases/ImageMagick-${IM_VER}.tar.xz \
    && tar -xf ImageMagick.tar.xz \
    && cd ImageMagick-${IM_VER} \
    && ./configure \
    && make -j"$(nproc)" \
    && make install \
    && ldconfig \
    && convert --version


WORKDIR /code

COPY . /code

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt