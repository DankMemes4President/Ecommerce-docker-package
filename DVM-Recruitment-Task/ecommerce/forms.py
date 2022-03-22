from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from .models import User, Vendor, Customer, Item, Cart, Review, ShippingAddress


class VendorSignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_vendor = True
        user.save()
        vendor = Vendor.objects.create(user=user)
        vendor.save()
        return user


class CustomerSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_customer = True
        user.save()
        customer = Customer.objects.create(user=user)
        customer.save()
        return user


class AddItem(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['item_name', 'item_image', 'item_description', 'item_quantity', 'item_cost']


class AddItemToCart(forms.ModelForm):
    class Meta:
        model = Cart
        fields = ['quantity']


class AddMoney(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['money']


class AddReview(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'review']


class AddShippingAddress(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['address_title', 'address']


class AddressSelection(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(AddressSelection, self).__init__(*args, **kwargs)
        self.fields['address_title'].queryset = ShippingAddress.objects.filter(customer__user=self.request.user)

    class Meta:
        model = ShippingAddress
        fields = ['address_title']

    address_title = forms.ModelChoiceField(queryset=None, widget=forms.Select)
