from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cv', '0013_education_gpa'),
    ]

    operations = [
        migrations.AddField(
            model_name='certificate',
            name='location',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
        migrations.AddField(
            model_name='professionalexperience',
            name='employment_type',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='professionalexperience',
            name='end_date',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='professionalexperience',
            name='location',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
        migrations.AddField(
            model_name='professionalexperience',
            name='start_date',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='communityinvolvement',
            name='end_date',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='communityinvolvement',
            name='location',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
        migrations.AddField(
            model_name='communityinvolvement',
            name='start_date',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='reference',
            name='relation',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
    ]




