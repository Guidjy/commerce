from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models


class User(AbstractUser):
    # 0-0 peep: https://docs.djangoproject.com/en/5.1/topics/db/examples/many_to_many/
    watchlist = models.ManyToManyField('Listing', blank=True, related_name="watchlist")


class Category(models.Model):
    category = models.CharField(max_length=32)
    
    def __str__(self):
        return f'{self.category}'


class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=280)
    price = models.FloatField()
    image = models.URLField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name='listings')
    creation_date = models.DateTimeField(auto_now_add=True)
    bids_placed = models.IntegerField(default=0)
    open_status = models.BooleanField(default=True)
    lister = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings_created')
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings_won', null=True, blank=True)
    
    def __str__(self):
        return f'\"{self.title}\" posted by {self.lister}'


class Bid(models.Model):
    price = models.FloatField(validators=[
        MinValueValidator(0.01)
    ])
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bids')
    
    def __str__(self):
        return f'${self.price} on {self.listing} by {self.bidder}'
    


class Comment(models.Model):
    comment = models.TextField(max_length=140)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='comments')
    
    def __str__(self):
        return f'{self.commenter} on {self.listing}: {self.comment}'
