from django.db import models

# Create your models here.
class Greeting(models.Model):
    when = models.DateTimeField("date created", auto_now_add=True)


class Categories(models.Model):
    category = models.CharField(max_length=100, unique=True)
    
class Journal(models.Model):
    when = models.DateTimeField("date created", auto_now_add=True)
    login = models.CharField(max_length=30)
    value =  models.FloatField()
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    description = models.CharField(max_length=1000)
    

