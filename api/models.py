from django.db import models

# Create your models here.

class Feedback(models.Model):
    response = models.TextField()
    feedback = models.CharField(max_length=10)  # "like" or "dislike"
    created_at = models.DateTimeField(auto_now_add=True)
