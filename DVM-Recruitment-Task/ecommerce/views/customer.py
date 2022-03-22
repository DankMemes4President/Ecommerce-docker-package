from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.shortcuts import redirect, reverse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, View, UpdateView
from ..decorators import customer_required
from ..forms import CustomerSignUpForm, AddItemToCart, AddMoney, AddReview, AddShippingAddress, AddressSelection
from ..models import User, Customer, Item, Vendor, Cart, Review, Order, ShippingAddress, OrderedItems, WishList
from DVM_task3.keyconfig import sendgrid_sender_email
from django.views.generic.edit import FormMixin


class CustomerSignUpView(CreateView):
    model = User
    form_class = CustomerSignUpForm
    template_name = 'ecommerce/customer/signup.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'customer'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('ecommerce:customer_dashboard')


def customer_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, f"You are now logged in as {username}.")
                return redirect("ecommerce:customer_dashboard")
            else:
                messages.error(request, "Invalid username or password")
        else:
            messages.error(request, "Invalid username or password")
    form = AuthenticationForm()
    return render(request, "ecommerce/customer/login.html", context={"form": form})


@method_decorator([login_required, customer_required()], name='dispatch')
class CustomerDashboard(ListView):
    model = Customer
    template_name = 'ecommerce/customer/dashboard.html'

    def get_queryset(self):
        vendors = Vendor.objects.all()
        customer_username = self.request.user.username
        customer = self.request.user.customer
        items = Item.objects.filter()
        balance = self.request.user.customer.money
        queryset = {
            'vendors': vendors,
            'customer_username': customer_username,
            'balance': balance,
            'customer': customer,
            'items': items,
        }
        return queryset


@method_decorator([login_required, customer_required()], name='dispatch')
class CustomerVendorItems(ListView):
    model = User
    template_name = 'ecommerce/customer/vendor_items.html'

    def get_queryset(self, *args, **kwargs):
        user = super(CustomerVendorItems, self).get_queryset(*args, **kwargs)
        user = user.get(username=self.kwargs['vendor'])
        vendor = user.vendor
        items = vendor.item_set.all()
        items = items.order_by('-units_sold')
        balance = self.request.user.customer.money
        customer = self.request.user.customer
        vendors = Vendor.objects.all()
        queryset = {
            'vendors': vendors,
            'items': items,
            'vendor': vendor,
            'balance': balance,
            'customer': customer,
        }
        return queryset


@method_decorator([login_required, customer_required()], name='dispatch')
class CustomerViewItem(CreateView):
    model = Customer
    template_name = 'ecommerce/customer/item_details.html'
    form_class = AddItemToCart

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item = Item.objects.get(item_name=self.kwargs['item'])
        reviews = Review.objects.filter(item_id=item.id)
        vendors = Vendor.objects.all()
        balance = self.request.user.customer.money
        customer = self.request.user.customer
        context['item'] = item
        context['reviews'] = reviews
        context['vendors'] = vendors
        context['balance'] = balance
        context['customer'] = customer

        return context

    def post(self, request, *args, **kwargs):
        customer = self.request.user.customer
        quantity = int(request.POST['quantity'])
        item = Item.objects.get(item_name=self.kwargs['item'])
        stock = item.item_quantity
        if 'add_item' in request.POST:
            if quantity <= stock and (quantity * item.item_cost) <= customer.money:
                if not Cart.objects.filter(customer_id=self.request.user.id, items_id=item.id).exists():
                    Cart.objects.create(customer_id=self.request.user.id, items_id=item.id)
                cart_item = customer.cart_set.get(items_id=item.id)
                cart_item.quantity += quantity
                item.item_quantity -= quantity
                cart_item.total_cost += quantity * item.item_cost
                item.total_cost = item.item_cost * item.item_quantity
                for key, cart_item_2 in enumerate(Cart.objects.filter(customer_id=self.request.user.id)):
                    customer.money -= cart_item_2.total_cost
                item.save()
                if cart_item.quantity > 0:
                    cart_item.save()
                else:
                    cart_item.delete()
                    return redirect('ecommerce:customer_item_details', item)
                return redirect('ecommerce:customer_dashboard')
            else:
                return redirect('ecommerce:customer_item_details', item)
        elif 'wishlist' in request.POST:
            WishList.objects.create(customer=customer, items=item)
            return redirect('ecommerce:customer_dashboard')


@method_decorator([login_required, customer_required()], name='dispatch')
class CustomerAddMoney(UpdateView):
    model = Customer
    template_name = 'ecommerce/customer/money.html'
    form_class = AddMoney

    def get_object(self, queryset=None):
        customer = self.request.user.customer
        return customer

    def get_success_url(self):
        return reverse('ecommerce:customer_dashboard')


@method_decorator([login_required, customer_required()], name='dispatch')
class CustomerCart(ListView, FormMixin):
    model = Cart
    template_name = 'ecommerce/customer/cart.html'
    form_class = AddressSelection

    def get_form_kwargs(self):
        kwargs = super(CustomerCart, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_queryset(self):
        user = self.request.user
        customer = user.customer
        items = customer.cart_set.all()
        balance = customer.money
        vendors = Vendor.objects.all()
        cart_items = customer.cart_set.all()
        cart_total = 0
        cart_total_items = 0
        for it in cart_items:
            cart_total += it.total_cost
            cart_total_items += 1

        # address_selected = AddressSelection()
        queryset = {
            'items': items,
            'customer': customer,
            'balance': balance,
            'vendors': vendors,
            'cart_total': cart_total,
            'cart_total_items': cart_total_items,
            # 'address_selected': address_selected,
        }
        return queryset

    def post(self, request, *args, **kwargs):
        customer = self.request.user.customer
        money = customer.money
        cart_items = customer.cart_set.all()
        address_id = request.POST['address_title']
        if customer.shippingaddress_set.filter(id=address_id).exists():
            address = customer.shippingaddress_set.filter(id=address_id)[0].address
            order = Order.objects.create(customer=customer, address=address)
        else:
            messages.error(request, f"You did not select and Address. Please select or create a new one.")
            redirect('ecommerce:customer_shipping_address')
        vendors = []
        for cart in cart_items:
            item = Item.objects.get(item_name=cart.items)
            vendor = User.objects.get(id=item.vendor_id).vendor
            if vendor not in vendors:
                vendors.append(vendor)
            quantity = cart.quantity
            money -= cart.total_cost
            if money >= 0:
                customer.money = money
                ordered_item = OrderedItems.objects.create(vendor=vendor, order=order, item_name=cart.items.item_name,
                                                           item_image=cart.items.item_image,
                                                           item_description=cart.items.item_description,
                                                           item_quantity=cart.quantity,
                                                           item_cost=cart.items.item_cost,
                                                           total_cost=cart.total_cost)
                item.units_sold += quantity
                order.total_cost += ordered_item.total_cost
                cart.delete()
                order.save()
                item.save()
                customer.save()
            else:
                return redirect('ecommerce:customer_cart')

        for vendor in vendors:
            inventory = [f'{order.address}']
            for key, elem in enumerate(order.ordereditems_set.all()):
                if elem.vendor == vendor:
                    inventory.append(f'{elem.item_name} : {elem.item_quantity} @ {elem.total_cost}')
            send_mail(
                f'Order ID {order.id} Received',
                f'{inventory}',
                f'{sendgrid_sender_email}',
                [vendor.user.email],
                fail_silently=False,
            )

        return redirect('ecommerce:customer_cart_checkout')


@method_decorator([login_required, customer_required()], name='dispatch')
class CustomerCartItemsEdit(CreateView):
    model = Cart
    template_name = 'ecommerce/customer/cart_item_edit.html'
    form_class = AddItemToCart

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.request.user.customer
        item = Item.objects.get(item_name=self.kwargs['item'])
        cart_item = customer.cart_set.get(items_id=item.id)
        vendors = Vendor.objects.all()
        balance = customer.money
        context['customer'] = customer
        context['items'] = cart_item
        context['vendors'] = vendors
        context['balance'] = balance
        return context

    def post(self, request, *args, **kwargs):
        customer = self.request.user.customer
        quantity = int(request.POST['quantity'])
        item = Item.objects.get(item_name=self.kwargs['item'])
        cart_item = customer.cart_set.get(items_id=item.id)
        cart_item.quantity -= quantity
        item.item_quantity += quantity
        cart_item.total_cost = cart_item.quantity * item.item_cost
        item.save()
        cart_item.save()
        if cart_item.quantity > 0:
            return redirect('ecommerce:customer_cart')
        else:
            cart_item.delete()
            if customer.cart_set.all():
                return redirect('ecommerce:customer_cart')
            else:
                return redirect('ecommerce:customer_dashboard')

    def get_success_url(self):
        return reverse('ecommerce:customer_cart')


@method_decorator([login_required, customer_required()], name='dispatch')
class CustomerCheckout(View):
    model = Cart
    template_name = 'ecommerce/customer/checkout.html'

    def get(self, request):
        return render(request, 'ecommerce/customer/checkout.html')


@method_decorator([login_required, customer_required()], name='dispatch')
class CustomerItemReview(CreateView):
    model = Review
    template_name = 'ecommerce/customer/add_review.html'
    form_class = AddReview

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item = Item.objects.get(item_name=self.kwargs['item'])
        vendors = Vendor.objects.all()
        balance = self.request.user.customer.money
        customer = self.request.user.customer
        context['item'] = item
        context['vendors'] = vendors
        context['balance'] = balance
        context['customer'] = customer
        return context

    def post(self, request, *args, **kwargs):
        item = Item.objects.get(item_name=self.kwargs['item'])
        rating = request.POST['rating']
        review = request.POST['review']
        if Order.objects.filter(customer_id=self.request.user.id, ordereditems__item_name=item.item_name).exists():
            if not Review.objects.filter(username=self.request.user.customer, item_id=item.id).exists():
                Review.objects.create(username=self.request.user.customer, rating=rating, review=review,
                                      item_id=item.id)
            else:
                messages.error(request, 'Item already reviewed')
        else:
            messages.error(request, 'You haven\'t ordered this item yet')
        return redirect('ecommerce:customer_item_details', item)

    def get_success_url(self):
        return redirect('ecommerce:customer_item_details')


@method_decorator([login_required, customer_required()], name='dispatch')
class CustomerViewPrevOrders(ListView):
    model = Order
    template_name = 'ecommerce/customer/view_orders.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        customer = self.request.user.customer
        orders = Order.objects.filter(customer_id=self.request.user.id)
        vendors = Vendor.objects.all()
        balance = customer.money
        context = {
            'is_customer': customer.user.is_customer,
            'customer': customer,
            'orders': orders,
            'vendors': vendors,
            'balance': balance,
        }
        return context


@method_decorator([login_required, customer_required()], name='dispatch')
class CustomerShippingAddress(CreateView):
    model = ShippingAddress
    template_name = 'ecommerce/customer/address.html'
    form_class = AddShippingAddress

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.request.user.customer
        addresses = customer.shippingaddress_set.all()
        vendors = Vendor.objects.all()
        balance = customer.money
        context['customer'] = customer
        context['addresses'] = addresses
        context['vendors'] = vendors
        context['balance'] = balance
        return context

    def post(self, request, *args, **kwargs):
        address_title = request.POST['address_title']
        address = request.POST['address']
        ShippingAddress.objects.create(customer_id=self.request.user.id, address=address, address_title=address_title)
        return redirect('ecommerce:customer_dashboard')


@method_decorator([login_required, customer_required()], name='dispatch')
class CustomerWishList(ListView):
    model = WishList
    template_name = 'ecommerce/customer/wishlist.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        customer = self.request.user.customer
        vendors = Vendor.objects.all()
        balance = customer.money
        items = WishList.objects.filter(customer=customer)

        context = {
            'customer': customer,
            'vendors': vendors,
            'balance': balance,
            'items': items,
        }
        return context

    def post(self, request):
        if 'delete' in request.POST:
            customer = request.user.customer
            item = WishList.objects.filter(customer=customer,
                                           items_id=Item.objects.get(item_name=request.POST['delete']).id)
            item.delete()
            return redirect('ecommerce:customer_wishlist')
