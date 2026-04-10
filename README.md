# Spatial Query Service

# Install SILREC Project
```
 cd /var/www
 git clone https://github.com/dbca-wa/silrec.git
 cd silrec

 virtualenv venv
 . venv/bin/activate

 pip install -r requirements.txt 
```
     
## Add in .env
```
DEBUG=True
DATABASE_URL="postgis://<dev_user>:<dev_pw>@localhost:5432/db_name"
#
TZ=Australia/Perth
EMAIL_HOST="smtp.corporateict.domain"
DEFAULT_FROM_EMAIL='no-reply@dbca.wa.gov.au'
NOTIFICATION_EMAIL='first.last@dbca.wa.gov.au'
NON_PROD_EMAIL='first.last@dbca.wa.gov.au'
PRODUCTION_EMAIL=False
EMAIL_INSTANCE='DEV'
SECRET_KEY="ThisisNotRealKey"
SITE_PREFIX='silrec-dev'
SITE_DOMAIN='dbca.wa.gov.au'
OSCAR_SHOP_NAME='Conservation and Ecosystem Management'
BPAY_ALLOWED=False
ENABLE_DJANGO_LOGIN=True
ENABLE_WEB=True
ENABLE_CRON=False
CSRF_COOKIE_SECURE=False
SESSION_COOKIE_SECURE=False
SECURE_CROSS_ORIGIN_OPENER_POLICY="same-origin" # None
CSRF_TRUSTED_ORIGINS=['https://silrec-uat.dbca.wa.gov.au']
SHOW_MENUS=True
PGSQL_OPTIONS={}
SHOW_DEBUG_TOOLBAR=False

```


# Setup DB (in schema silrec)
```
NOTE - for restore (migration from silrec_v2):
File 'silrec_v3_backup.sql' has:
1. replaced references to SCHEMA 'public' with 'silrec'
2. set search_path=silrec;

psql -h localhost -p 5432 -U postgres -W -f silrec_test1.sql
psql -h localhost -p 5432 -U dev -d silrec_test1 -W -f /path/to/silrec_v3_backup.sql
```

## Add in .env
```
./manage.py shell_plus
u = User.objects.create(email='firstname.lastname@dbca.wa.go.au', username='jawaidm', first_name='Firstname', last_name='Lastname')

In [2]:  u.set_password('pw')
In [5]:  u.is_staff=True
In [10]: u.save()

./manage.py runserver 0.0.0.0:8002
```
