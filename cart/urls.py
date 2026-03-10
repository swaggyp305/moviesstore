from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='cart.index'),
    path('<int:id>/add/', views.add, name='cart.add'),
    path('clear/', views.clear, name='cart.clear'),
    path('purchase/', views.purchase, name='cart.purchase'),
    path('popularity_map/', views.popularity_map, name = 'cart.popularity_map'),
    path('admin/cart/order/top-purchasers/', views.top_purchasers, name='cart_order_top_purchasers'),
    path('get_movies/', views.near_movies, name='get_movies'),
]