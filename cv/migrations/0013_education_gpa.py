from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cv', '0012_award_presenting_organization_cvsubmission_city_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='education',
            name='gpa',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
    ]




