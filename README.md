# Spatial Query Service

# Install SILREC Project
```
 cd projects/party_hire
 git clone https://github.com/jmushtaq/party_hire.git
 cd party_hire

 virtualenv venv
 . venv/bin/activate

 pip install -r requirements.txt
```

# Setup DB (in schema silrec)
```
NOTE - for restore (migration from silrec_v2):
File 'silrec_v3_backup.sql' has:
1. replaced references to SCHEMA 'public' with 'silrec'
2. set search_path=silrec;

psql -h localhost -p 5432 -U postgres -W -f utils/party_hire_dev.sql
OR
psql -h localhost -p 5432 -U dev -d party_hire_dev -W -f /path/to/party_hire_dev_backup.sql
```

# Create the migrations
```
./manage.py makemigrations
./manage.py migrate

# Load dummy categories, items and images
./manage.py load_dummy_data
./manage.py load_item_images
```

## Add in .env
```

## Add in .env
```
DEBUG=True
DATABASE_URL="postgis://<dev_user>:<dev_pw>@localhost:5432/db_name"
SECRET_KEY=your-secret-key-here
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_PUBLIC_KEY=your-stripe-public-key

```


./manage.py shell_plus
u = User.objects.create(email='firstname.lastname@dbca.wa.go.au', username='username', first_name='Firstname', last_name='Lastname')

u.set_password('pw')
u.is_staff=True
u.is_superuser=True
u.save()

./manage.py collectstatic --noinput
./manage.py runserver 0.0.0.0:8002
```
