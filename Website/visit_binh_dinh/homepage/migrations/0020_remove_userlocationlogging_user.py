# Generated by Django 5.0.2 on 2024-05-11 05:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0019_alter_usersearchlogging_username'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userlocationlogging',
            name='user',
        ),
    ]
