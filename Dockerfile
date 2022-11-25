FROM python:3.10

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

ENV PORT=8080

COPY . /app
WORKDIR /app

ENTRYPOINT [ "/bin/bash", "-c", "./entrypoint.sh" ]