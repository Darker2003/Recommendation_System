# Generated by Django 5.0.3 on 2024-04-22 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0011_userlocationlogging_usersearchlogging'),
    ]

    operations = [
        migrations.AddField(
            model_name='locationdatabase',
            name='slug',
            field=models.SlugField(default='', unique=True),
        ),
    ]
