from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from movies.models import Movie
from .utils import calculate_cart_total
from .models import Order, Item
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum
from django.contrib.admin.views.decorators import staff_member_required
from math import radians, sin, cos, pow, atan2, sqrt

def spherical_distance(lat1, lon1, lat2, lon2):
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    diff_lat = lat2 - lat1
    diff_lon = lon2 - lon1
    a = pow(sin(diff_lat/2), 2) + cos(lat1)*cos(lat2)*pow(sin(diff_lon/2), 2)
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    earth_radius = 3959
    return c * earth_radius

def index(request):
    cart_total = 0
    movies_in_cart = []
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())
    if (movie_ids != []):
        movies_in_cart = Movie.objects.filter(id__in=movie_ids)
        cart_total = calculate_cart_total(cart, movies_in_cart)
    template_data = {}
    template_data['title'] = 'Cart'
    template_data['movies_in_cart'] = movies_in_cart
    template_data['cart_total'] = cart_total
    return render(request, 'cart/index.html',
        {'template_data': template_data})

def add(request, id):
    get_object_or_404(Movie, id=id)
    cart = request.session.get('cart', {})
    cart[id] = request.POST['quantity']
    request.session['cart'] = cart
    return redirect('home.index')

def add_to_cart(request, id):
    get_object_or_404(Movie, id=id)
    cart = request.session.get('cart', {})
    cart[id] = request.POST['quantity']
    request.session['cart'] = cart
    return redirect('cart.index')

def clear(request):
    request.session['cart'] = {}
    return redirect('cart.index')

@login_required
def purchase(request):
    latitude = request.GET.get('latitude', 0)
    longitude = request.GET.get('longitude', 0)
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())
    if (movie_ids == []):
        return redirect('cart.index')
    movies_in_cart = Movie.objects.filter(id__in=movie_ids)
    cart_total = calculate_cart_total(cart, movies_in_cart)
    order = Order()
    order.user = request.user
    order.total = cart_total
    order.save()
    for movie in movies_in_cart:
        item = Item()
        item.movie = movie
        item.price = movie.price
        item.order = order
        item.quantity = cart[str(movie.id)]
        item.latitude = latitude
        item.longitude = longitude
        item.save()
        
        movie.orders_num += int(item.quantity)
        movie.save()
        
    request.session['cart'] = {}
    template_data = {}
    template_data['title'] = 'Purchase confirmation'
    template_data['order_id'] = order.id
    return render(request, 'cart/purchase.html',
        {'template_data': template_data})

@staff_member_required
def top_purchasers(request):
    top_users = (
        Order.objects.values('user__username')
        .annotate(total_spent=Sum('total'))
        .order_by('-total_spent')[:10]
    )
    return JsonResponse({'top_purchasers': list(top_users)})

def popularity_map(request):
    template_data = {}
    template_data['title'] = 'Local Popularity Map'
    return render(request, 'cart/popularity_map.html',
    {'template_data': template_data})

def near_movies(request):
    cur_lat = request.GET.get('latitude', 0)
    cur_lon = request.GET.get('longitude', 0)
    template_data = {}
    items = Item.objects.all()
    movie_dict = dict()
    for item in items:
        dist = spherical_distance(float(cur_lat), float(cur_lon), float(item.latitude), float(item.longitude))
        if (dist <= 50):
            if item.movie in movie_dict:
                movie_dict[item.movie] += item.quantity
            else:
                movie_dict[item.movie] = item.quantity
    pop_movie = "No movies around you"
    pop_quant = 0
    for movie in movie_dict:
        if movie_dict[movie] > pop_quant:
            pop_quant = movie_dict[movie]
            pop_movie = movie.name
    template_data['pop_movie'] = pop_movie
    template_data['pop_quant'] = pop_quant
    print(pop_movie)
    print(pop_quant)
    return JsonResponse(template_data)
