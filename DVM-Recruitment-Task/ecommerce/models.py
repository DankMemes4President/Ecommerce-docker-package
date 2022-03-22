from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from PIL import Image


class User(AbstractUser):
    is_vendor = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)


class Vendor(models.Model):

    def __str__(self):
        return self.user.username

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)


def upload_to_vendor_dir(instance, filename):
    return f"{instance.vendor.user.username}/{filename}"


class Item(models.Model):

    def __str__(self):
        # return f"{self.item_name} - {self.item_quantity} @ {self.item_cost}"
        return self.item_name

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=256)
    item_image = models.ImageField(upload_to=upload_to_vendor_dir)
    #item_image = models.ImageField()
    item_description = models.TextField()
    item_quantity = models.PositiveIntegerField()
    item_cost = models.FloatField(default=0, validators=[MinValueValidator(0.0)])
    total_cost = models.FloatField()
    units_sold = models.PositiveIntegerField(default=0)
    
    
    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(Item, self).save()
        img = Image.open(self.item_image.path)
        if img.height > 500 or img.width > 500:
            output_size = (500, 500)
            img.thumbnail(output_size)
            img.save(self.item_image.path)
    

class Review(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    username = models.CharField(max_length=256)
    rating = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(5)])
    review = models.TextField()


class Customer(models.Model):

    def __str__(self):
        return self.user.username

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    money = models.FloatField(default=0, validators=[MinValueValidator(0.0)])


class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    items = models.OneToOneField(Item, on_delete=models.CASCADE, null=True)
    quantity = models.PositiveIntegerField(default=0)
    total_cost = models.FloatField(default=0)


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    address_title = models.CharField(max_length=500)
    address = models.TextField()

    def __str__(self):
        return self.address_title


class Order(models.Model):

    def __str__(self):
        return self.id

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    address = models.TextField(null=False)
    total_cost = models.FloatField(default=0)


class OrderedItems(models.Model):

    def __str__(self):
        return self.item_name

    # Since you are not allowed to order from multiple vendors for now, having a vendor link in ordered items doesn't make sense
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=256)
    item_image = models.ImageField()
    item_description = models.TextField()
    item_quantity = models.PositiveIntegerField()
    item_cost = models.FloatField(default=0, validators=[MinValueValidator(0.0)])
    total_cost = models.FloatField()


class WishList(models.Model):

    def __str__(self):
        return str(self.items)

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    items = models.ForeignKey(Item, on_delete=models.CASCADE)
