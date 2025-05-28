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
    
    existing_object = model_class.objects.filter(title=title).first()
    if existing_object:
        return existing_object.slug
    
    while model_class.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{suffix}"
            suffix += 1

    return slug
