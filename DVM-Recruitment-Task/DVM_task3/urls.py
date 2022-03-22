"""DVM_task3 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from ecommerce.views import ecommerce_home, vendor, customer

handler404 = 'ecommerce.views.ecommerce_home.custom_page_not_found_view'
handler500 = 'ecommerce.views.ecommerce_home.custom_error_view'
handler403 = 'ecommerce.views.ecommerce_home.custom_permission_denied_view'
handler400 = 'ecommerce.views.ecommerce_home.custom_bad_request_view'

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('ecommerce/', include('ecommerce.urls')),
                  # path('vendor/dashboard', default.vendor_dashboard, name='vendor_dashboard'),
                  # path('ecommerce/accounts/', include('django.contrib.auth.urls')),
                  path('ecommerce/accounts/', include('allauth.urls'), name='google_login'),
                  path('ecommerce/accounts/signup/', ecommerce_home.SignUp.as_view(), name='signup'),
                  path('ecommerce/accounts/signup/vendor/', vendor.VendorSignUpView.as_view(), name='vendor_signup'),
                  path('ecommerce/accounts/signup/customer/', customer.CustomerSignUpView.as_view(),
                       name='customer_signup'),
                  path('ecommerce/accounts/login/vendor', vendor.vendor_login, name='vendor_login'),
                  path('ecommerce/accounts/login/customer', customer.customer_login, name='customer_login'),
                  path('ecommerce/accounts/logout', ecommerce_home.user_logout, name='logout'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
