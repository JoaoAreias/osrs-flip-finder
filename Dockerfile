FROM python:3.10

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY ./build-scripts /tmp/build-scripts
ENV GOOGLE_ANALYTICS_ID=""
RUN ["python", "/tmp/build-scripts/inject_google_analytics.py"]

ENV PORT=8080

COPY . /app
WORKDIR /app

RUN ["chmod", "+x", "/app/entrypoint.sh"]
ENTRYPOINT [ "/bin/bash", "-c", "./entrypoint.sh" ]