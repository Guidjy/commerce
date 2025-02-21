from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import User, Listing, Bid, Comment
from .forms import CreateListingForm, PlaceBidForm, CommentForm


def index(request):
    listings = Listing.objects.all()
    return render(request, "auctions/index.html", {'listings': listings})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def create_listing(request):
    if request.method == 'POST':
        form = CreateListingForm(request.POST)
        if form.is_valid():
            new_listing = form.save(commit=False)
            new_listing.lister = request.user
            new_listing.save()
            return HttpResponseRedirect(reverse('index'))
    
    else:
        form = CreateListingForm()
        return render(request, 'auctions/create_listing.html', {'form': form})
    

def listing(request, listing_pk):
    if request.method == 'POST':
        if 'bid_submit' in request.POST:
            # submit bid
            pass
            
        elif 'comment_submit' in request.POST:
            # submit comment
            pass
        
        return HttpResponse('0-0')
        
    else:
        listing = Listing.objects.get(pk=listing_pk)
        comments = Comment.objects.filter(listing=listing)
        
        #bids = Bid.objects.filter(listing=listing)
        #highest_bid = bids.aggregate(Max('price'))  # returns {'price__max': Decimal('xx.xx')}
        #highest_bid = highest_bid['price__max']
        #if highest_bid == None:
        #    highest_bid = listing.price

        return render(request, 'auctions/listing.html', {
            'listing': listing,
            'comments': comments,
            'comment_form': CommentForm(),
            'bid_form': PlaceBidForm()
            })
    