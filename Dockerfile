FROM python:3.10

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY . /app
WORKDIR /app

CMD ["streamlit", "run",  "src/main.py", "--server.port", "80"]