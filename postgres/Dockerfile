FROM postgres:13
WORKDIR /app
COPY ./scripts/db/init.sh /docker-entrypoint-initdb.d
COPY ./scripts/db/dump.sql ./scripts/db/dump.sql
EXPOSE 5432
