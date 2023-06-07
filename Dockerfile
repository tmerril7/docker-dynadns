FROM python:3.9

ARG S6_OVERLAY_VERSION=3.1.0.1
ARG PTB_VERSION=13.15

RUN apt-get install -y xz-utils
ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz /tmp
RUN tar -C / -Jxpf /tmp/s6-overlay-noarch.tar.xz
ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-x86_64.tar.xz /tmp
RUN tar -C / -Jxpf /tmp/s6-overlay-x86_64.tar.xz

ADD /ext /ext
ADD /etc /etc
RUN chmod -R 777 /etc/services.d
RUN chmod -R 777 /etc/cont-init.d
RUN chmod -R 777 /ext
RUN pip install requests python-telegram-bot==${PTB_VERSION}
ENTRYPOINT ["/init"]