ARG PY_VER=3.13
ARG BUILD=default

# Build stage
FROM python:${PY_VER}-slim AS base_default

WORKDIR /opt

COPY app/requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY app .

RUN python manage.py collectstatic --noinput && \ 
    apt update && apt install --no-install-recommends -y minify && \
    minify -r prod_static -o . && \
    apt clean && rm -rf /var/lib/apt/lists/* webapp/static requirements*.txt


FROM base_default AS base_mssql

ONBUILD COPY app/requirements-mssql.txt .

ONBUILD RUN pip install --no-cache-dir --upgrade -r requirements-mssql.txt && \
    apt update && apt install --no-install-recommends -y curl gpg && \
    apt clean && rm -rf /var/lib/apt/lists/* requirements*.txt && \
    VER=$(cut -d. -f1 /etc/debian_version) && \
    curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg && \
    curl https://packages.microsoft.com/config/debian/${VER}/prod.list > /etc/apt/sources.list.d/mssql-release.list


FROM base_default AS base_nginx

ONBUILD COPY compose/default.conf.template /home/default

ONBUILD RUN sed -i 's/${WEB_HOST}/http:\/\/127.0.0.1:8000/' /home/default


FROM base_$BUILD AS base

# Deploy stage
FROM python:${PY_VER}-slim AS build_default

ARG PY_VER

WORKDIR /opt

COPY --from=base /usr/local/bin/gunicorn /usr/local/bin/gunicorn

COPY --from=base /usr/local/lib/python${PY_VER}/site-packages/ /usr/local/lib/python${PY_VER}/site-packages/


FROM build_default AS build_mssql

ONBUILD COPY --from=base /usr/share/keyrings/microsoft-prod.gpg /usr/share/keyrings/microsoft-prod.gpg

ONBUILD COPY --from=base /etc/apt/sources.list.d/mssql-release.list /etc/apt/sources.list.d/mssql-release.list

# FixMe: remove libgssapi-krb5-2 once microsoft updates mssql-django & msodbcsql17
ONBUILD RUN apt update && ACCEPT_EULA=y apt install --no-install-recommends -y libgssapi-krb5-2 msodbcsql17 unixodbc && \
    apt clean && rm -rf /var/lib/apt/lists/*


FROM build_default AS build_nginx

ONBUILD ENV BUILD=nginx

ONBUILD RUN apt update && apt install --no-install-recommends -y nginx && \
    apt clean && rm -rf /var/lib/apt/lists/*

ONBUILD COPY --from=base /home/default /etc/nginx/sites-available/default


FROM build_$BUILD

COPY --from=base /opt .

EXPOSE 80 8000

CMD ["sh", "start.sh"]