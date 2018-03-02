FROM  microservice

COPY requirements.txt /app/requirements.txt
COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

CMD ["/usr/bin/supervisord"]

