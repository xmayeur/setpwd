FROM  microservice

COPY requirements.txt /app/requirements.txt
COPY . /app
WORKDIR /app

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

CMD ["/usr/bin/supervisord"]

