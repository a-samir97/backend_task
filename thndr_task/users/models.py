from django.db import models

class User(models.Model):
    """
        class responsible for holdling user information  
    """
    full_name = models.CharField(max_length=256)
    balance = models.FloatField()
    stocks = models.JSONField(default=dict)