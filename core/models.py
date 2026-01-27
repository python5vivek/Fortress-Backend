from django.db import models
from django.contrib.auth.models import User




# Create your models here.
class Messages(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='receiver', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.sender} at {self.timestamp}"

class connecteds(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE,related_name="connectionss")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.user1} - {self.user2}"
