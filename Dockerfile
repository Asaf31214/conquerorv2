FROM python:3.12-slim

WORKDIR /app

COPY server/requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY server /app/

EXPOSE 8000

CMD python scripts.py start-server

