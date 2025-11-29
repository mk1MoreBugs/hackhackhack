FROM python:3.14.0-slim

WORKDIR /backend

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
 && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./alembic.ini ./
COPY ./migrations ./migrations

COPY ./app ./app

EXPOSE 8080

CMD uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload --proxy-headers
#CMD ["sh", "-c", "ls -la /backend/app/services/ && python3 parse_pdf.py"]

# HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=5 \
# CMD curl -f http://localhost:8080/v1/