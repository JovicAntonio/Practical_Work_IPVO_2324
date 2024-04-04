# Practical_Work_IPVO_2324

## Za REST framework paket

```bash
py -m pip install djangorestframework
```

ili cak i:

```bash
pip install djangorestframework
```

## Pristupni podaci na pgadmin

```py
PGADMIN_DEFAULT_EMAIL: pgadmin@gmail.com
PGADMIN_DEFAULT_PASSWORD: pgAdmin_Pa55w0rd
```

## Pristupni podaci za spajanje na postgres server u pgadminu

```py
DATABASES = {    
   "default": {        
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "postgres",
        "PORT": 5432,
    }
}
```

## Migracije izmjena u Django-u na postgres

Prvo je potrebno, prije nego je i jedan servis dignut preko Docker-a, pokrenuti naredbu:

```sh
python manage.py makemigrations
```

Nakon pokretanja Docker-a i uspješnog dizanja baze, potrebno je pokrenuti sljedeću naredbu kako bi promjene bile prihvaćene prenesle se na bazu:

```sh
docker-compose exec web python manage.py migrate
```

## Dizanje servisa nakon prvog postavljanja

Nakon prvog postavljanja, postgres i pgadmin promijene dopuštenja na svim datotekama u postgres_data i pgadmin_data mapama pa `docker-compose` ne može dignuti servise zbog čega javi error. Prije `docker-compose`-a potrebno je pokrenuti naredbe:

```sh
sudo chown -R 1000:1000 ./pgadmin_data/ 
sudo chown -R 1000:1000 ./postgres_data/
```

Nakon toga servisi se normalno dižu.
