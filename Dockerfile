FROM python:3.11

COPY src/ /app
WORKDIR /app

RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "-u", "/app/main.py"]