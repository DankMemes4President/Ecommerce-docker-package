#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi
python DVM-Recruitment-Task/manage.py makemigrations ecommerce
python DVM-Recruitment-Task/manage.py migrate --noinput
python DVM-Recruitment-Task/manage.py collectstatic --no-input --clear
exec "$@"

