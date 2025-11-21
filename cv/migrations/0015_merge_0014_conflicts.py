from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cv', '0014_add_fields_experience_community_certificate_reference'),
        ('cv', '0014_auto_add_missing_fields'),
    ]

    operations = [
        # This is a merge migration to resolve parallel 0014 heads.
    ]




