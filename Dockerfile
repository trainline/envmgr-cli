FROM python:alpine

ADD setup.* README.rst /build/
ADD emcli /build/emcli

RUN \
cd /build && \
python setup.py install && \
rm -rf /build
RUN apk add --no-cache jq

ENTRYPOINT []
CMD ["envmgr"]
