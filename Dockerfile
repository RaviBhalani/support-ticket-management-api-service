FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

ARG ENVIRONMENT=local
COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/${ENVIRONMENT}.txt

COPY . .

RUN chmod +x server.sh

CMD ["./server.sh"]