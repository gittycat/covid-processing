# Covid mobile clinics Results Processing

Note: This documentation is a work in progress.

The goal of this project is to reduce the delay in reporting test resuls.
The data is currently entered in Excel spreadsheets at external sites.
This will be replaced by a web app at some point. In the mean time,
the following process minimises disruption for the clinical staff (they
stay with the Excel they know) but allows for automation of contacting
the clients.





## Postgresql Setup

### Install psql 
```
brew update
brew install libpq
brew link --force libpq 

echo 'fzfa_EHgMW*axBTE_34P' > ~/.pgpass
source env.sh
```

### Python3 driver
NOTE: I'm installing the binary after issues with compiling from src.
The binary is not recommended for prod.
```
python -m pip install psycopg2-binary
```

### Start db
```
docker-compose -f production.yml up -d
```

### Create db
```
docker exec -it postgres createuser -U postgres starhealth 
docker exec -it postgres createdb -U postgres db

docker exec -i postgres psql -U postgres covid < 00-migration.sql
```

### Seed Data
```
python3 feeddb.py
```

### Utilities
Log inside
```
docker exec -it postgres psql -U postgres covid

````
