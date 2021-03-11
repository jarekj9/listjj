from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save


class Categories(models.Model):
    login = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=100)

    def __str__(self):
        return self.category


class Journal(models.Model):
    date = models.DateField()
    login = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.FloatField(default=0)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    description = models.CharField(max_length=1000)

class Attachment(models.Model):
    journal_id = models.ForeignKey(Journal, on_delete=models.CASCADE)
    login = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    description = models.CharField(max_length=1000)
    file = models.FileField()
    file_name = models.CharField(max_length=100)

    def __str__(self):
        return str(self.pk)


def get_upload_path(instance, filename):
    return "import/{0}/{1}".format(instance.user.username, filename)


class ImportModel(models.Model):
    file = models.FileField(upload_to="import/")


##################################################################### USER PROFILE:
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    default_category = models.ForeignKey(
        Categories, on_delete=models.DO_NOTHING, null=True, default=None
    )


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
