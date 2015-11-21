from django.db import models

# Create your models here.
class Repo(models.Model):
    stargazers_url = models.CharField(max_length=500)
    stargazers_count = models.IntegerField()
    full_name = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True, null=True)
    username = models.CharField(max_length=50)

    class Meta:
        unique_together = ['full_name', 'username']
