from django.db import models


class ErrorLog(models.Model):
    endpoint = models.TextField(null=True)
    message = models.TextField()
    trace = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
