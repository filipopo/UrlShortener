ARG PY_VER=3.12
ARG BUILD=default

# Build stage
FROM python:${PY_VER}-slim AS base
ARG BUILD

WORKDIR /app

COPY app/requirements.txt app/requirements-mssql.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt && \
    if [ "$BUILD" = "mssql" ]; then \
        pip install --no-cache-dir --upgrade -r requirements-mssql.txt && \
        apt update && apt install -y curl gpg && \
        apt clean && rm -rf /var/lib/apt/lists/* && \
        VER=$(cut -d. -f1 /etc/debian_version) && \
        curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg && \
        curl https://packages.microsoft.com/config/debian/${VER}/prod.list > /etc/apt/sources.list.d/mssql-release.list; \
    fi

COPY app .

RUN echo "python manage.py migrate --noinput && gunicorn --bind 0.0.0.0:8000 urlshortener.wsgi" > start.sh && \
    python manage.py collectstatic --noinput && \ 
    rm -rf webapp/static requirements.txt requirements-mssql.txt

# Deploy stage
FROM python:${PY_VER}-slim AS build_default
ARG PY_VER

WORKDIR /app

COPY --from=base /usr/local/bin/gunicorn /usr/local/bin/gunicorn

COPY --from=base /usr/local/lib/python${PY_VER}/site-packages/ /usr/local/lib/python${PY_VER}/site-packages/

FROM build_default AS build_mssql

ONBUILD COPY --from=base /usr/share/keyrings/microsoft-prod.gpg /usr/share/keyrings/microsoft-prod.gpg

ONBUILD COPY --from=base /etc/apt/sources.list.d/mssql-release.list /etc/apt/sources.list.d/mssql-release.list

ONBUILD RUN apt update && ACCEPT_EULA=y apt install -y unixodbc msodbcsql17 && \
            apt clean && rm -rf /var/lib/apt/lists/*

FROM build_$BUILD

COPY --from=base /app .

EXPOSE 8000

CMD ["sh", "start.sh"]