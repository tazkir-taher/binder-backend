from django.db import migrations

def create_interest_categories(apps, schema_editor):
    InterestCategory = apps.get_model('user_profile', 'InterestCategory')
    
    categories = [
        ('hobby', ['Reading', 'Hiking', 'Cooking', 'Gaming', 'Traveling']),
        ('music', ['Pop', 'Rock', 'Classical', 'Jazz', 'Hip Hop']),
        ('sport', ['Football', 'Basketball', 'Tennis', 'Swimming', 'Yoga']),
        ('language', ['English', 'Spanish', 'French', 'Mandarin', 'Arabic']),
        ('pet', ['Dogs', 'Cats', 'Birds', 'Reptiles', 'None']),
    ]
    
    for category, names in categories:
        for name in names:
            InterestCategory.objects.get_or_create(
                name=name,
                category=category
            )

class Migration(migrations.Migration):
    dependencies = [
        ('user_profile', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_interest_categories),
    ]