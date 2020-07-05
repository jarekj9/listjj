from django.db import models
from django.contrib.auth.models import User

class Categories(models.Model):
    login = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=100)


class Journal(models.Model):
    date = models.DateField()
    login = models.ForeignKey(User, on_delete=models.CASCADE)
    value =  models.FloatField(default=0)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    description = models.CharField(max_length=1000)

def get_upload_path(instance, filename):
    return 'import/{0}/{1}'.format(instance.user.username, filename)

class ImportModel(models.Model):
    file = models.FileField(upload_to='import/')


