FROM python:3.10.2-slim

COPY install-packages.sh ./install-packages.sh
RUN chmod +x ./install-packages.sh
RUN ./install-packages.sh

COPY entrypoint.sh /entrypoint.sh
COPY main.py /main.py

RUN chmod +x entrypoint.sh
RUN chmod +x /main.py

ENTRYPOINT ["/entrypoint.sh"]