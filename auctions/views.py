from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import User, Listing, Bid, Comment, Category
from .forms import CreateListingForm, PlaceBidForm, CommentForm


def index(request):
    listings = Listing.objects.all().order_by('-category')
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


@login_required
def create_listing(request):
    if request.method == 'POST':
        form = CreateListingForm(request.POST)
        if form.is_valid():
            new_listing = form.save(commit=False)
            new_listing.lister = request.user
            new_listing.save()
            return redirect('index')
    
    else:
        form = CreateListingForm()
        return render(request, 'auctions/create_listing.html', {'form': form})
    

def listing(request, listing_pk):
    listing = Listing.objects.get(pk=listing_pk)
    
    if request.method == 'POST':
        # place bid
        if 'bid_submit' in request.POST:
            bid_form = PlaceBidForm(request.POST)
            if bid_form.is_valid():
                new_bid = bid_form.save(commit=False)
                if new_bid.price > listing.price:
                    listing.price = new_bid.price
                    listing.bids_placed += 1
                    new_bid.bidder = request.user
                    new_bid.listing = listing
                    new_bid.save()
                    listing.save()
                else:
                    messages.warning(request, 'New bid must be higher than the starting_price/current highest bid')
                return redirect('listing', listing_pk=listing_pk)
                                                
        # close auction
        if 'close_auction_submit' in request.POST:
            bids = Bid.objects.filter(listing=listing)
            highest_bid = bids.last()
            listing.winner = highest_bid.bidder
            listing.open_status = False
            listing.save()
            return redirect('listing', listing_pk=listing_pk)
        
        # make comment
        if 'comment_submit' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.commenter = request.user
                new_comment.listing = listing
                new_comment.save()
                return redirect('listing', listing_pk=listing_pk)
        
    else:
        comments = Comment.objects.filter(listing=listing)

        return render(request, 'auctions/listing.html', {
            'listing': listing,
            'comments': comments,
            'comment_form': CommentForm(),
            'bid_form': PlaceBidForm()
            })
    

@login_required
def watchlist(request):
    if request.method == 'POST': 
        listing = Listing.objects.get(id=request.POST['listing_pk'])
        if listing not in request.user.watchlist.all():
            request.user.watchlist.add(listing)
        else:
            request.user.watchlist.remove(listing)
        
        return redirect('watchlist')

    else:
        watchlist = request.user.watchlist.all()
        return render(request, 'auctions/watchlist.html', {'watchlist': watchlist})
    

def category(request, category_pk):
    category = Category.objects.get(category=category_pk)
    listings = Listing.objects.filter(category=category)
    print(listings)
    return render(request, 'auctions/category.html', {
        'category': category,
        'listings': listings
    })