from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200)

    def __str__(self):
        return self.name


# Note: The image field was added later then the other fields. Before adding the field, we had already created product
# objects in the database. Thus as we are now adding the field we need to make null=True to ensure that we
# don't get any errors. Also it is to further safeguard us from times when the image for the corresponding product will
# be unavailable.

# Note: When an image will be added through the database, the added image will just be thrown in the root directory
# and won't be at a specific location like in static/images. For this, we need to configure accordingly by going into
# settings.py then add MEDIA_ROOT and MEDIA_URL to render these images. We'll then need to import static and settings
# in urls
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField()
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name

# We are creating a function named imageURL that is used to safeguard us from the error which we might face in
# store.html when product doesn't have an image url. (We safeguard it by rendering an empty string)
# For this we will use a property decorator so that it can be accessed as an attribute.
# The product.image.url looks at the url pattern

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url


# Customer will have a many to one relationship with order object that means that customer can have multiple orders.
# complete field is to indicate whether the cart is open or ite closed.If its open, ie if value is false we can continue
# to add items to the cart. If its true, it is a closed cart and we cannot add items to it.
# Also we have set the on_delete value to NULL and not delete. This is because if the customer gets deleted we don't
# want to delete the order, we just want to set the customer value to NULL

# The many-to-one relationship is as follows: There can be Many orders from One customer.
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True)

    def __str__(self):
        return str(self.id)

# The Class OrderItem is in general the entity that will be added to the cart.
# Items that need to be added to our order. We are using many to one field for product attribute. Also for order
# attribute we will be using many to one field. date_added is the date when the orderitem is added to the cart(order)
# Order is our cart and order item is the item within our cart. Cart can have multiple order items therefore ForeignKey
# is used.
# The Many-to-One relationship in this case is as follows: There can be Many OrderItems from One Product
# (Ex. Many OrderItems from one Toothbrush(Product)).
# Similarly, there can be Many OrderItems from one Order
class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.name


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)
    state = models.CharField(max_length=200, null=False)
    zipcode = models.CharField(max_length=200, null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address

