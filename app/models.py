from django.db import models
from django.contrib.auth.models import User

class Categories(models.Model):
    login = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=100, unique=True)


class Journal(models.Model):
    date = models.DateField()
    login = models.ForeignKey(User, on_delete=models.CASCADE)
    value =  models.FloatField()
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    description = models.CharField(max_length=1000)


