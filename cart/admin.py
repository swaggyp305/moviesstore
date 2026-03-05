from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.db.models import Count, Sum
from django.contrib.admin.views.decorators import staff_member_required
from .models import Order, Item

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total', 'date']
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('top-purchasers/', 
                 self.admin_site.admin_view(self.top_purchasers_view),
                 name='cart_order_top_purchasers'),
        ]
        return custom_urls + urls
    
    def top_purchasers_view(self, request): 
        """View to show top purchasers"""
        # Get all users with their total movies purchased
        top_users = Order.objects.values(
            'user__username'
        ).annotate(
            total_purchased=Count('item__id')
        ).order_by('-total_purchased')
        
        max_total = top_users[0]['total_purchased'] if top_users else 0
        
        context = {
            'top_users': top_users,
            'max_total': max_total,
            'opts': self.model._meta,
        }
        return render(request, 'admin/cart/order/top_purchasers.html', context)

admin.site.register(Order, OrderAdmin)
admin.site.register(Item)