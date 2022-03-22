import xlwt
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render, reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView
from xlwt import Workbook

from ..decorators import vendor_required
from ..forms import VendorSignupForm, AddItem
from ..models import User, Vendor, Item, Order, OrderedItems


# @login_required
# @vendor_required
# for functions

# @method_decorator([login_required, vendor_required], name='dispatch')
# for classes


class VendorSignUpView(CreateView):
    model = User
    form_class = VendorSignupForm
    template_name = 'ecommerce/vendor/signup.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'vendor'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('ecommerce:vendor_dashboard')


def vendor_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("ecommerce:vendor_dashboard")
            else:
                messages.error(request, "Invalid username or password")
        else:
            messages.error(request, "Invalid username or password")
    form = AuthenticationForm()
    return render(request, "ecommerce/vendor/login.html", context={"form": form})


@method_decorator([login_required, vendor_required()], name='dispatch')
class VendorDashboard(ListView):
    model = Vendor
    template_name = 'ecommerce/vendor/dashboard.html'

    def get_queryset(self):
        user = User.objects.get(username=self.request.user.username)
        vendor = user.vendor
        items = vendor.item_set.all()
        queryset = {
            'items': items,
            'vendor': vendor,
        }
        return queryset


@method_decorator([login_required, vendor_required()], name='dispatch')
class VendorAddItems(CreateView):
    model = Vendor
    template_name = 'ecommerce/vendor/add_items.html'
    form_class = AddItem

    def post(self, request, *args, **kwargs):
        vendor = self.request.user.vendor
        item_name = request.POST['item_name']
        item_image = request.FILES.get('item_image', False)
        item_description = request.POST['item_description']
        item_quantity = int(request.POST['item_quantity'])
        item_cost = float(request.POST['item_cost'])
        total_cost = item_cost * item_quantity
        if vendor.item_set.filter(item_name=item_name).exists():
            return redirect('ecommerce:vendor_add_items')
        else:
            Item.objects.create(item_name=item_name, item_image=item_image, item_description=item_description,
                                item_quantity=item_quantity, item_cost=item_cost,
                                total_cost=total_cost, vendor_id=request.user.id)
            return redirect('ecommerce:vendor_dashboard')


@method_decorator([login_required, vendor_required()], name='dispatch')
class VendorEditItems(UpdateView):
    model = Vendor
    template_name = 'ecommerce/vendor/add_items.html'
    form_class = AddItem

    def get_object(self, *args, **kwargs):
        vendor = self.request.user.vendor
        item = vendor.item_set.get(item_name=self.kwargs['item'])
        return item

    def get_success_url(self, *args, **kwargs):
        return reverse('ecommerce:vendor_dashboard')

    def post(self, request, *args, **kwargs):
        vendor = self.request.user.vendor
        item = vendor.item_set.get(item_name=self.kwargs['item'])
        if 'delete' in request.POST:
            item.delete()
        elif 'add' in request.POST:
            item.item_quantity = request.POST['item_quantity']
            item.save()
        return redirect('ecommerce:vendor_dashboard')


@method_decorator([login_required, vendor_required()], name='dispatch')
class VendorViewOrders(ListView):
    model = Order
    template_name = 'ecommerce/vendor/received_orders.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        user = self.request.user
        vendor = self.request.user.vendor
        orders = Order.objects.all().filter(ordereditems__vendor_id=user.id)
        ordered_items = OrderedItems.objects.filter(vendor_id=vendor.user.id)
        context = {
            'user': user,
            'vendor': vendor,
            'ordered_items': ordered_items,
            'orders': orders,
        }
        return context


@login_required
@vendor_required
def vendor_order_generate_csv(request):
    wb = Workbook()
    sheet = wb.add_sheet('Sheet 1')
    style = xlwt.easyxf('font : bold 1')
    sheet.write(0, 0, 'Order ID', style)
    sheet.write(0, 1, 'Item Name', style)
    sheet.write(0, 2, 'Units Sold', style)
    sheet.write(0, 3, 'Customer', style)

    for y, item in enumerate(OrderedItems.objects.filter(vendor_id=request.user.id)):
        sheet.write(y + 1, 0, item.order_id)
        sheet.write(y + 1, 1, item.item_name)
        if Item.objects.filter(item_name=item.item_name).exists():
            sheet.write(y + 1, 2, Item.objects.get(item_name=item.item_name).units_sold)
        else:
            sheet.write(y + 1, 2, 'N/A')
        sheet.write(y + 1, 3, item.order.customer.user.username)

    wb.save('media/test.xls')
    with open('media/test.xls', 'rb') as excel:
        file = excel.read()
    response = HttpResponse(file, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Sales_Report.xls'
    return response
