from django.db import models

# Create your models here.
class Repo(models.Model):
    '''
    depth:
        0 starred by you
        1 starred by someone who starred the same repo as you
        2 should not happen, to avoid too many requests

    stargazers_count:
        preferably procss < 500 (or even less) for 2 reasons:
            a) avoid too many requests
            b) avoid noise from popular libraries being starred by anyone
    '''
    stargazers_url = models.CharField(max_length=500)
    stargazers_count = models.IntegerField()
    full_name = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True, null=True)
    username = models.CharField(max_length=50)
    depth = models.IntegerField(default=0)

    class Meta:
        unique_together = ['full_name', 'username']


class StargazerProfiles(models.Model):
    username = models.CharField(max_length=50)
    origin = models.ForeignKey(Repo, related_name="stargazer_origin")

    class Meta:
        unique_together = ['origin', 'username']


class StargazerRepo(models.Model):
    origin = models.ForeignKey(Repo, related_name="stargazer_repo_origin")
    username = models.CharField(max_length=50)
    stargazers_count = models.IntegerField()
    full_name = models.CharField(max_length=100)

    class Meta:
        unique_together = ['origin', 'username', 'full_name']
