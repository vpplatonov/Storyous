###########
### API ###
###########
FROM python:3.10 as worker

# ODBC MSSQL Debian Linux support
ENV ACCEPT_EULA=Y
RUN curl https://packages.microsoft.com/keys/microsoft.asc | tee /etc/apt/trusted.gpg.d/microsoft.asc
# Debian 12
# curl https://packages.microsoft.com/config/debian/12/prod.list
# with fixed GPG error: The repository 'https://packages.microsoft.com/debian/12/prod bookworm InRelease' is not signed
COPY ./prod.list /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update && apt-get install -y msodbcsql18

# ODBC Debian Linux support
# RUN apt-get update && apt-get -y install g++ unixodbc-dev

ENV BASE_PATH="/home/app"
WORKDIR ${BASE_PATH}
COPY ./app/setup.cfg ${BASE_PATH}
COPY ./app/pyproject.toml ${BASE_PATH}
RUN pip install --upgrade pip && pip install .[mssql-service]

COPY ./app/ ${BASE_PATH}

# verify: $> which python
CMD ["/usr/local/bin/python", "migrations.py"]