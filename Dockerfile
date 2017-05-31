FROM alpine:3.6

MAINTAINER Dave Hall <skwashd@gmail.com>

COPY requirements.txt /tmp

# Install what we need to run this as an iron function.
RUN apk add --no-cache \
    py3-cffi \
    py3-cryptography && \
  pip3 install -r /tmp/requirements.txt && \
  rm /tmp/requirements.txt

COPY task.py /

ENTRYPOINT /task.py