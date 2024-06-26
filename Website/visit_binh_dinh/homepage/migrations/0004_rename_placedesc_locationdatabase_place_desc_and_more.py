# Generated by Django 5.0.2 on 2024-03-04 06:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0003_alter_userdatabase_phone'),
    ]

    operations = [
        migrations.RenameField(
            model_name='locationdatabase',
            old_name='placedesc',
            new_name='place_desc',
        ),
        migrations.RenameField(
            model_name='locationdatabase',
            old_name='placeid',
            new_name='place_id',
        ),
        migrations.RenameField(
            model_name='locationdatabase',
            old_name='placename',
            new_name='place_name',
        ),
        migrations.CreateModel(
            name='commentreview',
            fields=[
                ('comment_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('comment_text', models.TextField()),
                ('comment_date', models.DateTimeField(auto_now_add=True)),
                ('content', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='homepage.locationdatabase')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='homepage.userdatabase')),
            ],
        ),
    ]
