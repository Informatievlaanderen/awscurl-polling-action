FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install --no-install-recommends -y python3.8 python3-pip python3.8-dev curl && \
    pip --no-cache-dir install --upgrade pip && \
    pip --no-cache-dir install setuptools wheel && \
    pip --no-cache-dir install awscurl

COPY entrypoint.sh /entrypoint.sh
COPY main.py /main.py

RUN chmod +x /main.py

ENTRYPOINT ["/entrypoint.sh"]