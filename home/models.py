from django.db import models

# Create your models here.


class EntryLIST(models.Model):
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    full_name = models.CharField(max_length=200, blank=True, null=True)
    phone_number = models.CharField(max_length=11, blank=True, null=True)

    def __str__(self):
        return self.full_name
