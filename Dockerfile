# Default Apache2 container
FROM ubuntu:latest
# Don't prompt tzdata
ENV DEBIAN_FRONTEND=noninteractive
ARG SERVERNAME=projects.escience.dk
ENV SERVERNAME=$SERVERNAME

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

ARG PROJECTS_DIR=/var/projects

# Setup configuration
# Also enable wsgi and header modules
COPY apache/apache2-http.conf /etc/apache2/sites-available/projects.conf
RUN a2dissite 000-default.conf && \
    a2ensite projects.conf && \
    a2enmod wsgi && \
    a2enmod headers && \
    a2enmod ssl && \
    a2enmod rewrite

# Prepare WSGI launcher script
COPY ./res $PROJECTS_DIR/res
COPY ./apache/app.wsgi $PROJECTS_DIR/wsgi/
COPY ./run.py $PROJECTS_DIR/
RUN mkdir -p $PROJECTS_DIR/persistence && \
    chown root:www-data $PROJECTS_DIR/persistence && \
    chmod 775 -R $PROJECTS_DIR/persistence && \
    chmod 2755 -R $PROJECTS_DIR/wsgi

ENV PROJECTS_ENV_DIR=/etc/projects

# Install the envvars script, code and cleanup
RUN mkdir -p $PROJECTS_ENV_DIR && \
    echo "export ${PROJECTS_ENV_DIR}" >> /etc/apache2/envars
COPY ./projects-envvars-templates.py $PROJECTS_ENV_DIR/projects-envvars.py

# Copy in the source code
COPY . /app
WORKDIR /app

# Install the envvars script, code and cleanup
RUN pip3 install setuptools && \
    pip3 install wheel==0.30.0 && \
    python3 setup.py bdist_wheel && \
    pip3 install -r requirements.txt && \
    pip3 install -r tests/requirements.txt && \
    python3 setup.py install

# Allow www-data to start a process that binds to :80/:443
RUN touch /etc/authbind/byport/80 && \
    touch /etc/authbind/byport/443 && \
    chown www-data /etc/authbind/byport/* && \
    chmod 500 /etc/authbind/byport/*

RUN chown www-data:adm -R /var/log/apache2 && \
    chown www-data:www-data -R /var/run/apache2

RUN rm -r /app
WORKDIR $PROJECTS_DIR

EXPOSE 80

# Ensure that the supervisor directories are there
RUN mkdir -p /var/log/supervisor && \
    mkdir -p /var/run/supervisor

RUN chown www-data:www-data /var/log/supervisor && \
    chown www-data:www-data /var/run/supervisor

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Ensure the supervisord conf uses the www-data user to launch the web server
CMD ["/usr/bin/supervisord"]
