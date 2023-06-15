echo "setup template"
sudo service postgresql restart
echo "drop template db: enter db password"
dropdb basic_double_auction -U dbadmin -h localhost -i
echo "create database: enter db password"
createdb -h localhost -U dbadmin -O dbadmin basic_double_auction
source _basic_double_auction/bin/activate
python manage.py migrate
echo "create super user"
python manage.py createsuperuser 
echo "load fixtures"
python manage.py loaddata main.json
echo "setup done"
python manage.py runserver