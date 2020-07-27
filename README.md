# Setup

## Postgresql

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