import uuid
from django.utils.text import slugify
from unidecode import unidecode


def generate_filename(instance, filename):
    extension = filename.split('.')[-1]
    new_filename = "%s.%s" % (uuid.uuid4(), extension)
    return new_filename



def generate_unique_slug(model_class, title):
    base_slug = slugify(unidecode(title))
    slug = base_slug
    suffix = 1


    while model_class.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{suffix}"
        suffix += 1

    return slug

def filter_by_date_range(queryset, date_field='created_on', start_date=None, end_date=None):
    
    if start_date and end_date:
        filter_args = {f'{date_field}__range': (start_date, end_date)}
        queryset = queryset.filter(**filter_args)
    elif start_date:
        filter_args = {f'{date_field}__gte': start_date}
        queryset = queryset.filter(**filter_args)
    elif end_date:
        filter_args = {f'{date_field}__lte': end_date}
        queryset = queryset.filter(**filter_args)
    
    return queryset


def generate_unique_numeric_otp(model_class):
    while True:
        
        standard_uuid = uuid.uuid4()
        
        hex_uuid = standard_uuid.hex

        numeric_otp = int(hex_uuid[:6], 16)

        otp = str(numeric_otp)[:6]

        try:
            model_class.objects.get(otp=otp)
        except model_class.DoesNotExist:            
            return otp
        
