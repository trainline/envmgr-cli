FROM python:alpine

ADD setup.* README.rst /build/
ADD emcli /build/emcli

RUN \
cd /build && \
python setup.py install && \
rm -rf /build

ENTRYPOINT []
CMD ["envmgr"]
