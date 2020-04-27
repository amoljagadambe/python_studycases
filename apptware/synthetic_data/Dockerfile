FROM ubuntu:latest

ENV MYSQL_VERSION=5.7
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -yqq \
  apt-utils \
  wget \
  apt-transport-https \
  curl \
  build-essential \
  gcc \
  make \
  supervisor \
  openjdk-8-jre

# Install ES
RUN wget -O - https://packages.elastic.co/GPG-KEY-elasticsearch | apt-key add -
RUN echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | tee -a /etc/apt/sources.list.d/elastic-7.x.list
RUN apt-get update &&  apt-get install -yqq \
  elasticsearch=7.1.1 \
  mysql-server=${MYSQL_VERSION}* \
  python3-pip \
  python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip


WORKDIR /app
ENV PYTHONPATH .

# Install pip requirements
ADD ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# Copy the code/program
ADD  ./commands/ /app/commands/
COPY ./schema/ /app/schema/
ADD ./fixtures/ /app/fixtures/
ADD ./es_data/ /app/es_data/

ENV LC_ALL=C.UTF-8 \
  LANG=C.UTF-8

ADD ./scripts/ /app/scripts/
RUN chmod 755 /app/scripts/*.sh

ADD ./configs/supervisord.conf /etc/supervisord.conf
ADD ./configs/mysql.cnf /etc/mysql/mysql.conf.d/mysqld.cnf
ADD ./configs/elasticsearch.yml /etc/elasticsearch/elasticsearch.yml

# Configure default db
RUN /app/scripts/configure_mysql.sh

EXPOSE 3306 9200 9300

CMD ["/bin/bash", "/app/scripts/startup.sh"]