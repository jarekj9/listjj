# Generated by Django 3.0.8 on 2020-07-11 09:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_auto_20200711_0935'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='default_category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.Categories'),
        ),
    ]
