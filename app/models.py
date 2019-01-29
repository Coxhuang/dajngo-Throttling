from django.db import models
from django.contrib.auth.models import AbstractUser




class UserProfile(AbstractUser):

    age = models.IntegerField(default=1)

