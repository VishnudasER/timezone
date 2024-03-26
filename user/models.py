from django.db import models
from django.contrib.auth.models import User 
# Create your models here.

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,default=1)  
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    address1 = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    zipcode = models.IntegerField(null=True, blank=True)
    phone = models.BigIntegerField(null=True, blank=True)


    class Meta:
        db_table = 'address'
        
class Post(models.Model):
    post_heading = models.CharField(max_length=200)
    post_text = models.TextField()
    def __str__(self):     
        return str(self.post_heading)

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete = models.CASCADE)