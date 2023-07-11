# multi_user_socket_template
Template for multi user Django Channels experiment.

Setup Guide:
https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-18-04

To start / stop postgresql in WSL2 use the service command:
    sudo service postgresql status
    sudo service postgresql start (or stop)

Create and start Redis Server:
    sudo apt install redis-server
    sudo service redis-server start
    sudo service redis-server status

Create a user for the database:
    sudo -u postgres psql
    CREATE USER dbadmin WITH PASSWORD 'chapmanEsi';
    ALTER USER dbadmin CREATEDB;
    ALTER ROLE dbadmin SET client_encoding TO 'utf8';
    ALTER ROLE dbadmin SET default_transaction_isolation TO 'read committed';
    ALTER ROLE dbadmin SET timezone TO 'UTC';
    CREATE DATABASE basic_double_auction;
    GRANT ALL PRIVILEGES ON DATABASE basic_double_auction TO dbadmin;



local_settings.py:
    Copy local_settings_sample.py to local_settings.py
    local_settings.py is used for local development and will be excluded from the repo.
    Update the database section of this file with the info from your locally run instance of Postgresdb.

Update Python installers:
	sudo add-apt-repository ppa:deadsnakes/ppa
	sudo apt update 
	sudo apt install python3.11
	sudo apt-get install python3.11-distutils

Activate virtual environment and install requirments:
    virtualenv --python=python3.11 _multi_user_socket_template_env
    source _multi_user_socket_template_env/bin/activate
    pip install -U -r requirements.txt

Setup Environment:
sh setup.sh

Run Environment:
python manage.py runserver






