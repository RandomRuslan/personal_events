FROM postgres:12.2
LABEL DESCRIPTION="pePostgreSQL"

ARG PSQL_DIR="/usr/local/pgsql"

COPY /initdb.d ./docker-entrypoint-initdb.d

RUN mkdir $PSQL_DIR \
    && chown postgres:postgres $PSQL_DIR

RUN apt-get update \
    && apt-get install -y vim

USER postgres

#RUN initdb \
#    && echo "host all all 0.0.0.0/0 trust" >> $PGDATA/pg_hba.conf \
#    && pg_ctl start

ENTRYPOINT ["docker-entrypoint.sh"]
EXPOSE 5432
CMD ["postgres"]
