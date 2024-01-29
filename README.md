# Practical_Work_IPVO_2324

## Za REST framework paket

```bash
py -m pip install djangorestframework
```

ili cak i:

```bash
pip install djangorestframework
```

## Pristupni podaci na admina

username: antonio/igor

password: jova1234/iggy1234

ili ako korisnik želi, može sam napraviti usera na bazi sa:

```sh
python manage.py createsuperuser
```

U tom slučaju, potrebno je u settings.py promjeniti:

```py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/app/db.sqlite3',
    }
}
```

na:

```py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

Ovom promjenom omogućeno je lokalno povezivanje na bazu u svrhu dodavanja korisnika. Nakon dodavanja, potrebno je vratiti na prethodnu verziju.

## Replikacija podataka

Potrebno je otkomentirati u `docker-compose`-u ovaj dio:

```yml
  postgres:
    image: postgres:latest
    environment:
      POSTGRES_DB: pgdb
      POSTGRES_USER: postgres_user
      POSTGRES_PASSWORD: postgres_password
      PG_HOST: postgres
      PG_PORT: 5432
    volumes:
      - ./postgres_data:/var/lib/postgresql/data
  replication:
    build: .
    depends_on:
      - postgres
    volumes:
      - ./data:/app/data 
    environment:
      - PG_DB=pgdb
      - PG_USER=postgres_user
      - PG_PASSWORD=postgres_password
      - PG_HOST=postgres
      - PG_PORT=5432
```

Po potrebi, ako `docker-compose` ne radi i javlja da je pristup odbijen zbog postgres-a, nakon što se drugi put "zavrti" `docker-compose` potrebno je pokrenuti naredbu ili otkomentirati u Dockerfile-u:

```sh
sudo chmod 777 -R postgres_data/
```

Njom se dodjeljuju najveća prava za sve datoteke potrebne za postgres.

## Dohavacanje datoteka

Na API-ju [http://172.19.0.3/media/upload/11_-_Stream_Processing.pdf](http://172.19.0.3/media/upload/11_-_Stream_Processing.pdf) se za primjer može vidjeti neki od PDF-ova u bazi. Zadnja vrijednost IP adrese se može izmjeniti sa 4 ili 6 obzirom da je osposobljen load balancer.
