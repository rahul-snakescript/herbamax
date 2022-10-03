"""herbamax_new URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.conf.urls.static import static
from django.conf import settings
from mainapp.views import HomeView, cart, ProductView, checkout, ajax_add_to_cart, ajax_remove_from_cart, \
    ajax_product_change_quantity, ajax_change_tax, ajax_apply_code, DashIndexView, DashOrdersView, DashPasswordView,\
    DashAddressesView, ContactView, ajax_send_contact_form, ProductsView, ajax_create_order
from blog.views import BlogMainPageView, BlogPostView


ajax_patterns = [
    url(r'^add_to_cart/$', ajax_add_to_cart, name='ajax_add_to_cart'),
    url(r'^remove_from_cart/$', ajax_remove_from_cart, name='ajax_remove_from_cart'),
    url(r'^product_change_quantity/$', ajax_product_change_quantity, name='ajax_product_change_quantity'),
    url(r'^change_tax/$', ajax_change_tax, name='ajax_change_tax'),
    url(r'^apply_code/$', ajax_apply_code, name='ajax_apply_code'),
    url(r'^send_contact_form/$', ajax_send_contact_form, name='ajax_send_contact_form'),
    #
    url(r'^create_order/$', ajax_create_order, name='ajax_create_order'),
    # url(r'^send_receipt/$', ajax_send_receipt, name='ajax_send_receipt'),
    # url(r'^delete_item_from_order/$', ajax_delete_item_from_order, name='ajax_delete_item_from_order'),
    # url(r'^change_item_qty_in_order/$', ajax_change_item_qty_in_order, name='ajax_change_item_qty_in_order'),

]

dash_patterns = [
    url(r'^$', login_required(DashIndexView.as_view()), name='dash_index'),
    url(r'^orders/$', login_required(DashOrdersView.as_view()), name='dash_orders'),
    url(r'^password/$', login_required(DashPasswordView.as_view()), name='dash_password'),
    url(r'^addresses/$', login_required(DashAddressesView.as_view()), name='dash_addresses'),
]

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^redactor/', include('redactor.urls')),
    url(r'^accounts/', include('allauth.urls')),

    url(r'^ajax/', include(ajax_patterns)),
    url(r'^dashboard/', include(dash_patterns)),

    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^cart/$', cart, name='cart'),
    url(r'^checkout/$', checkout, name='checkout'),
    url(r'^product/(?P<slug>[-\w]+)/$', ProductView.as_view(), name='product'),
    # url('product/<slug:slug>/', ProductView.as_view(), name='product'),
    url(r'^products/$', ProductsView.as_view(), name='products'),
    url(r'^contact/$', ContactView.as_view(), name='contact'),

    url(r'^blog/$', BlogMainPageView.as_view(), name='blog_main'),
    url(r'^blog/(?P<slug>[-\w]+)/$', BlogPostView.as_view(), name='blog_post'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)\
              + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
