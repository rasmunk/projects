# Default Apache2 container
FROM ubuntu:latest
# Don't prompt tzdata
ENV DEBIAN_FRONTEND=noninteractive

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
COPY ./projects $PROJECTS_DIR/projects
COPY ./res $PROJECTS_DIR/res
COPY ./projects_base $PROJECTS_DIR/projects_base
COPY ./apache/app.wsgi $PROJECTS_DIR/wsgi/
COPY ./run.py $PROJECTS_DIR/
RUN mkdir -p $PROJECTS_DIR/persistence && \
    chown root:www-data $PROJECTS_DIR/persistence && \
    chmod 775 -R $PROJECTS_DIR/persistence && \
    chmod 2755 -R $PROJECTS_DIR/wsgi

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

RUN rm -r /app
WORKDIR $PROJECTS_DIR

EXPOSE 80

# Prepare supervisord
RUN mkdir -p /var/log/supervisor
# Insert supervisord config -> handles the startup procedure for the image
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
CMD ["/usr/bin/supervisord"]
