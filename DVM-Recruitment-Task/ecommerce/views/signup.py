from django.views.generic import TemplateView


class SignUp(TemplateView):
    template_name = "ecommerce/registration/signup.html"
