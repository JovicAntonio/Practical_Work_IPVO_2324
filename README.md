# IIS projekt 2025

## Za REST framework paket

```bash
py -m pip install djangorestframework
```

ili čak i:

```bash
pip install djangorestframework
```

## Pristupni podaci za spajanje na postgres server u pgadminu

```py
DATABASES = {    
   "default": {        
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "<IP adresa docker container-a>",
        "PORT": 5432,
    }
}
```

## Migracije izmjena u Django-u na postgres

Prvo je potrebno, prije nego je i jedan servis dignut preko Docker-a, pokrenuti naredbu:

```sh
docker-compose exec web1 python manage.py makemigrations
```

Nakon pokretanja Docker-a i uspješnog dizanja baze, potrebno je pokrenuti sljedeću naredbu kako bi promjene bile prihvaćene prenesle se na bazu:

```sh
docker-compose exec web1 python manage.py migrate
```
