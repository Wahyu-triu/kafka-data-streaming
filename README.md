# kafka-data-streaming

1. run pip install -r requirements.txt to install required libraries
2. to start kafka image, run : docker-compose -up -d
3. go to query dir
    - create table in postgres using query from postgres.txt
    - create table in clickhouse using query from clickhouse.txt
4. change wal_level in postgres
    - run vi /var/lib/postgresql/data/postgresql.conf
    - default is replica, change to logical. logical decoding requires wal_level logical
3. go to ./scripts, run run producer.py to crawl data
    - if you want to monitor data crawling and ingesting from postgres to clickhouse, run consumer.py
4. run app.py to see dasboard and monitor live data ingestion and gathering insight from the chart