#!/bin/sh

sudo -i -u postgres

admin


echo "Se conecto como postgres"

createdb systemscript

psql -d systemscript -U postgres

\dt

DROP SCHEMA public CASCADE;

CREATE SCHEMA public;

GRANT ALL ON SCHEMA public TO postgres;

GRANT ALL ON SCHEMA public TO public;

pwd

ls

pg_restore -U postgres -d dbprueba -1 backup.sql

psql -d dbprueba -U postgres

\dt




sudo apt install python3-pip
pip3 --version
python -m venv virtual-env
source virtual-env/bin/activate 
pip install -r requirements.txt

python manage.py collectstatic
sudo systemctl daemon-reload
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
file /run/gunicorn.sock
sudo systemctl status gunicorn
sudo ln -s /etc/nginx/sites-available/proyecto /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
sudo ufw delete allow 8000
sudo ufw allow 'Nginx Full'

