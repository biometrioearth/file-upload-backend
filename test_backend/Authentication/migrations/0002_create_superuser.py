import os 

from django.db import migrations


def forwards(apps, schema_editor):
    from test_backend.Authentication.models import User

    if schema_editor.connection.alias != 'default':
        return
    
    User.objects.create_superuser(
        username=os.environ.get("TEST_SUPERUSER","admin"),
        password=os.environ.get("TEST_SUPERUSER_PASS","admin")
    )

def backwards(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('Authentication','0001_initial'),
    ]

    operations = [
        migrations.RunPython(forwards,backwards),
    ]