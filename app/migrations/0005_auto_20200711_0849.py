# Generated by Django 3.0.8 on 2020-07-11 08:49

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0004_auto_20200710_1513'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='MyUser',
            new_name='Profile',
        ),
    ]
