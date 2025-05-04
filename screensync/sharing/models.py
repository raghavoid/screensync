from django.db import models
from django.contrib.auth.models import User
import uuid

class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_rooms')
    password = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    participants = models.ManyToManyField(User, related_name='rooms')
    
    def __str__(self):
        return self.name
    
    @property
    def is_public(self):
        return self.password is None or self.password == ''