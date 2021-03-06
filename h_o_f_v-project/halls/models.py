from django.db import models
from django.contrib.auth.models import User


class Hall(models.Model):
	title = models.CharField(max_length=255)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	votes = models.TextField()
	votes_total = models.IntegerField(default=1)

class Video(models.Model):
	title = models.CharField(max_length=255)
	url = models.URLField()
	thumbnail_url = models.URLField()
	youtube_id = models.CharField(max_length=255)
	hall = models.ForeignKey(Hall, on_delete=models.CASCADE)

class SuggestionVideo(models.Model):
	title = models.CharField(max_length=255)
	url = models.URLField()
	youtube_id = models.CharField(max_length=255)
	hall = models.ForeignKey(Hall, on_delete=models.CASCADE)

