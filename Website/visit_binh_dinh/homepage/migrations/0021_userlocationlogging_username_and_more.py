# Generated by Django 5.0.2 on 2024-05-11 06:06

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0020_remove_userlocationlogging_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='userlocationlogging',
            name='username',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='usersearchlogging',
            name='username',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
