# Generated by Django 3.1.3 on 2021-02-24 10:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0013_auto_20200712_1427'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('description', models.CharField(max_length=1000)),
                ('file', models.FileField(upload_to='')),
                ('journal_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.journal')),
                ('login', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
