# Default Apache2 container
FROM ubuntu:latest
# Don't prompt tzdata
ENV DEBIAN_FRONTEND=noninteractive
ARG SERVER_NAME=projects.escience.dk
ARG APP_NAME=projects
ARG APP_DIR=/var/${APP_NAME}

ENV SERVERNAME=${SERVER_NAME}
ENV APP_DIR=${APP_DIR}

RUN apt-get update && apt-get install --no-install-recommends -yq \
    apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    python3-dev \
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
COPY apache/apache2-http.conf /etc/apache2/sites-available/${APP_NAME}.conf
RUN a2dissite 000-default.conf && \
    a2ensite ${APP_NAME}.conf && \
    a2enmod wsgi && \
    a2enmod headers && \
    a2enmod ssl && \
    a2enmod rewrite

RUN mkdir ${APP_DIR}
# Prepare WSGI launcher script
COPY ./res ${APP_DIR}/res
COPY ./apache/app.wsgi ${APP_DIR}/wsgi/
COPY ./run.py ${APP_DIR}/
RUN mkdir -p ${APP_DIR}/persistence && \
    chown root:www-data ${APP_DIR}/persistence && \
    chmod 775 -R ${APP_DIR}/persistence && \
    chmod 2755 -R ${APP_DIR}/wsgi

ENV ENV_DIR=/etc/projects

# Install the envvars script, code and cleanup
RUN mkdir -p $ENV_DIR && \
    echo "export ENV_DIR=${ENV_DIR}" >> /etc/apache2/envvars && \
    echo "export SERVERNAME=${SERVERNAME}" >> /etc/apache2/envvars && \
    echo "ServerName ${SERVERNAME}" >> /etc/apache2/apache2.conf
COPY ./envvars-templates.py $ENV_DIR/envvars.py

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
WORKDIR ${APP_DIR}

EXPOSE 80

# Ensure that the supervisor directories are there
RUN mkdir -p /var/log/supervisor && \
    mkdir -p /var/run/supervisor

RUN chown www-data:www-data /var/log/supervisor && \
    chown www-data:www-data /var/run/supervisor

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Ensure the supervisord conf uses the www-data user to launch the web server
CMD ["/usr/bin/supervisord"]
