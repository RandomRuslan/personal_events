FROM postgres:12.2
LABEL DESCRIPTION="pePostgreSQL"

ARG PSQL_DIR="/usr/local/pgsql"

COPY /initdb.d ./docker-entrypoint-initdb.d

RUN mkdir $PSQL_DIR \
    && chown postgres:postgres $PSQL_DIR

RUN apt-get update \
    && apt-get install -y vim

USER postgres

ENTRYPOINT ["docker-entrypoint.sh"]
EXPOSE 5432
CMD ["postgres"]
