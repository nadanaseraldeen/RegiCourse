# Generated by Django 5.0.4 on 2024-05-12 14:17

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RegiCourse_App', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='students',
            name='email',
            field=models.EmailField(default=django.utils.timezone.now, max_length=254, unique=True),
            preserve_default=False,
        ),
    ]
