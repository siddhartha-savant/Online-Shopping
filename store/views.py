from django.shortcuts import render
from django.http import JsonResponse
from .models import *
import json
import datetime


def store(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cart_items = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        cart_items = order['get_cart_items']

    products = Product.objects.all()
    context = {'products': products, 'cart_items': cart_items}
    return render(request, 'store/store.html', context)


# We will first be checking whether the user is authenticated or not. We are able to write user.customer because of
# the one to one relation we have in models. The get_or_create() is used to query for existing object. If not found,
# then create one. After this, we will get the items attached to our order. order.orderitem_set.all() is used to query
# the child objects (orderitem) by setting the parent value (order). By this function we get all the orderitems for that
# order. The else part is for when the user is not authenticated. For this we have thus given the attribute functions
# get_cart_total and get_cart_items 0 value in a dictionary.
# Note that cart_items variable is added so as to add the quantity of orderitems in the cart feature. We could have done
# this with some javascript, instead we are returning this variable from every view function to their HTML templates
def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cart_items = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        cart_items = order['get_cart_items']
    context = {'items': items, 'order': order, 'cart_items': cart_items}
    return render(request, 'store/cart.html', context)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cart_items = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        cart_items = order['get_cart_items']
    context = {'items': items, 'order': order, 'cart_items': cart_items}
    return render(request, 'store/checkout.html', context)


def update_item(request):
    data = json.loads(request.body)
    product_id = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', product_id)

    customer = request.user.customer
    product = Product.objects.get(id=product_id)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        order_item.quantity = order_item.quantity + 1
    elif action == 'remove':
        order_item.quantity = order_item.quantity - 1

    order_item.save()

    if order_item.quantity <= 0:
        order_item.delete()

    return JsonResponse('Item was added', safe=False)

# Sometimes the total can be send as a string value. Thus float function is used. Also note an if statement is used to
# check whether the total send from the client side to the backend is same or not. This is because, one can easily
# change the total value present in the frontend using javascript. Regardless of this, we are still saving the order
# In that case complete will remain False.
# IMP: Once order.complete will become True, and the page is then successfully redirected to store.html, the value
# present in the red circle will be zero as a new order will be in place. (In the store function we are checking the
# order object and if not present, creating one. As the complete=True for the last order, here a new order object will
# be created because of which the red circle will be zero.
def process_order(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = float(data['userFormData']['total'])
        order.transaction_id = transaction_id

        if total == order.get_cart_total:
            order.complete = True
        order.save()

        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shippingInfo']['address'],
            city=data['shippingInfo']['city'],
            state=data['shippingInfo']['state'],
            zipcode=data['shippingInfo']['zipcode'],

        )

    else:
        print('User is not logged in')
    return JsonResponse('Payment complete', safe=False)
