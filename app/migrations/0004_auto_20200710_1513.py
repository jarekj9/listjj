# Generated by Django 3.0.8 on 2020-07-10 15:13

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0003_auto_20200710_1512'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Employee',
            new_name='MyUser',
        ),
    ]
