ARG PY_VER="3.12"

# Build stage
FROM python:${PY_VER}-slim AS base

WORKDIR /app

COPY app .

RUN pip install --no-cache-dir --upgrade -r requirements.txt && \
    python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \ 
    rm -rf webapp/static requirements.txt

# Deploy stage
FROM python:${PY_VER}-slim
ARG PY_VER

WORKDIR /app

COPY --from=base /usr/local/bin/ /usr/local/bin/

COPY --from=base /usr/local/lib/python${PY_VER}/site-packages/ /usr/local/lib/python${PY_VER}/site-packages/

COPY --from=base /app .

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "urlshortener.wsgi"]