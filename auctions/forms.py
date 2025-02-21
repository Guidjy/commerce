from django.forms import ModelForm
from .models import Listing, Bid, Comment



class CreateListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'price', 'category', 'image']
        

class PlaceBidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['price']
        

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
