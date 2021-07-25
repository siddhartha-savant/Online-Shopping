from django.shortcuts import render
from django.http import JsonResponse
from .models import *
import json
import datetime
from .utils import cookie_cart, cart_data, guest_order


def store(request):
    data = cart_data(request)
    cart_items = data['cart_items']

    products = Product.objects.all()
    context = {'products': products, 'cart_items': cart_items}
    return render(request, 'store/store.html', context)


# We will first be checking whether the user is authenticated or not. We are able to write user.customer because of
# the one to one relation we have in models. The get_or_create() is used to query for existing object. If not found,
# then create one. After this, we will get the items attached to our order. order.orderitem_set.all() is used to query
# the child objects (orderitem) by setting the parent value (order). By this function we get all the orderitems for that
# order. The else part is for when the user is not authenticated. For this we have thus given the attribute functions
# get_cart_total and get_cart_items 0 value in a dictionary. (This is changed afterwards)

# --Description for utils.py cookie_data function--
# Note that cart_items variable is added so as to add the quantity of orderitems in the cart feature. We could have done
# this with some javascript, instead we are returning this variable from every view function to their HTML templates
# For else(guest user), first we will get the cookie in cart variable. Note we need to parse the cookie as it is a
# string. We will parse it into dictionary and save it in cart variable. We are then using a for loop to get the total
# number of items and their total price.
# As we don't have the real items(we are referring cookie and not the database), we will built it from the cookie. We
# check the cart.html and see which values are needed (ex name, price, imageURL, quantity and get_total)
# The reason we have added the try catch in for loop is because, when the product is deleted lets say from the database,
# however earlier you had added the product and a cookie was created using that product, then again when building the
# order from cookie, the item does not exist error will occur.

def cart(request):
    data = cart_data(request)
    cart_items = data['cart_items']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cart_items': cart_items}
    return render(request, 'store/cart.html', context)


def checkout(request):
    data = cart_data(request)
    cart_items = data['cart_items']
    order = data['order']
    items = data['items']

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
# In the else part, we get the name and email from the filled form. We query the email to check whether it matches with
# previous used email ids or not. (Whether the customer i.e. the guest customer who is not registered, has he previously
# used the email mentioned). We can even attach all of their previous orders (to a new user) before they were ever a
# user with us. We are writing the for loop to add the items in the OrderItem database. (Check the models.py of
# OrderItem)

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def process_order(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

    else:
        customer, order = guest_order(request, data)

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
    return JsonResponse('Payment complete', safe=False)
