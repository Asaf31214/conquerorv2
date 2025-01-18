FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000

ENV ENVIRONMENT=CLOUD
CMD uvicorn main:app --host 0.0.0.0 --port $PORT

