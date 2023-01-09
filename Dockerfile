FROM python:3.10

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

ENV GOOGLE_ANALYTICS_ID=""

ENV PORT=8080

COPY . /app
WORKDIR /app

RUN ["chmod", "+x", "/app/entrypoint.sh"]
ENTRYPOINT [ "/bin/bash", "-c", "./entrypoint.sh" ]