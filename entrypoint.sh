# install new requirements if any
pip install -r requirements.txt

# run new migrations
python manage.py migrate

# start app
python manage.py runserver 0.0.0.0:7070