# Installation
https://django-oscar.readthedocs.io/en/latest/internals/getting_started.html

## Add Countries
```
python manage.py oscar_populate_countries

# Keep only Australia (for checkout/shipping)
Country.objects.exclude(printable_name__icontains='Australia').delete()
(248, {'address.Country': 248})

Country.objects.all()
<QuerySet [<Country: Australia>]>
```

## Add Pipeline
```
OSCAR_INITIAL_ORDER_STATUS = 'Pending'
OSCAR_INITIAL_LINE_STATUS = 'Pending'
OSCAR_ORDER_STATUS_PIPELINE = {
    'Pending': ('Being processed', 'Cancelled',),
    'Being processed': ('Processed', 'Cancelled',),
    'Cancelled': (),
}
```
