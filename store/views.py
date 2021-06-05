from django.shortcuts import render
from django.http import JsonResponse
from .models import *
import json


def store(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'store/store.html', context)


# We will first be checking whether the user is authenticated or not. We are able to write user.customer because of
# the one to one relation we have in models. The get_or_create() is used to query for existing object. If not found,
# then create one. After this, we will get the items attached to our order. order.orderitem_set.all() is used to query
# the child objects (orderitem) by setting the parent value (order). By this function we get all the orderitems for that
# order. The else part is for when the user is not authenticated. For this we have thus given the attribute functions
# get_cart_total and get_cart_items 0 value in a dictionary
def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
    context = {'items': items, 'order': order}
    return render(request, 'store/cart.html', context)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
    context = {'items': items, 'order': order}
    return render(request, 'store/checkout.html', context)


def update_item(request):
    data = json.loads(request.body)
    product_id = data['productId']
    action = data['action']
    print('Action:',action)
    print('Product:',product_id)
    return JsonResponse('Item was added', safe=False)
