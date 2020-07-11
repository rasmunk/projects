# Default Apache2 container
FROM ubuntu:latest
# Don't prompt tzdata
ENV DEBIAN_FRONTEND=noninteractive

ARG SERVER_NAME
ARG APP_NAME
ARG APP_DIR

ENV SERVERNAME=${SERVER_NAME:-projects.escience.dk}
ENV APPNAME=${APP_NAME:-projects}
ENV APPDIR=${APP_DIR:-/var/projects}

RUN apt-get update && apt-get install --no-install-recommends -yq \
    apache2 \
    libapache2-mod-wsgi-py3 \
    python3.7 \
    python3.7-pip \
    python3.7-dev \
    libssl-dev \
    libffi-dev \
    net-tools \
    tzdata \
    ntp \
    ntpdate \
    vim \
    nano \
    authbind \
    supervisor && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/run/apache2

# Setup configuration
# Also enable wsgi and header modules
COPY apache/apache2-http.conf /etc/apache2/sites-available/${APPNAME}.conf
RUN a2dissite 000-default.conf && \
    a2ensite ${APPNAME}.conf && \
    a2enmod wsgi && \
    a2enmod headers && \
    a2enmod ssl && \
    a2enmod rewrite

RUN mkdir ${APPDIR}
# Prepare WSGI launcher script
COPY ./res ${APPDIR}/res
COPY ./apache/app.wsgi ${APPDIR}/wsgi/
COPY ./run.py ${APPDIR}/
RUN mkdir -p ${APPDIR}/persistence && \
    chown root:www-data ${APPDIR}/persistence && \
    chmod 775 -R ${APPDIR}/persistence && \
    chmod 2755 -R ${APPDIR}/wsgi

ENV ENV_DIR=/etc/projects

# Install the envvars script, code and cleanup
RUN mkdir -p $ENV_DIR && \
    echo "export ENV_DIR=${ENV_DIR}" >> /etc/apache2/envvars && \
    echo "export SERVERNAME=${SERVERNAME}" >> /etc/apache2/envvars && \
    echo "ServerName ${SERVERNAME}" >> /etc/apache2/apache2.conf

# Copy in the source code
COPY . /app
WORKDIR /app

# Install the envvars script, code and cleanup
RUN pip3 install setuptools && \
    pip3 install wheel==0.30.0 && \
    python3 setup.py bdist_wheel && \
    pip3 install -r requirements.txt && \
    pip3 install -r projects/tests/requirements.txt && \
    python3 setup.py install

# Allow www-data to start a process that binds to :80/:443
RUN touch /etc/authbind/byport/80 && \
    touch /etc/authbind/byport/443 && \
    chown www-data /etc/authbind/byport/* && \
    chmod 500 /etc/authbind/byport/*

RUN chown www-data:adm -R /var/log/apache2 && \
    chown www-data:www-data -R /var/run/apache2

RUN rm -r /app
WORKDIR ${APPDIR}

EXPOSE 80

# Ensure that the supervisor directories are there
RUN mkdir -p /var/log/supervisor && \
    mkdir -p /var/run/supervisor

RUN chown www-data:www-data /var/log/supervisor && \
    chown www-data:www-data /var/run/supervisor

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Ensure the supervisord conf uses the www-data user to launch the web server
CMD ["/usr/bin/supervisord"]
