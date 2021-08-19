FROM python:3.8-slim

RUN apt update &&\
	apt install -y tini &&\
	rm -r /var/lib/apt/* /var/cache/apt/*

COPY requirements.txt /app/requirements.txt
COPY server.py /app/server.py
COPY init.sh /init.sh

RUN chmod +x /init.sh
RUN pip install -r /app/requirements.txt

ENTRYPOINT ["tini", "--"]
CMD ["bash", "/init.sh"]
