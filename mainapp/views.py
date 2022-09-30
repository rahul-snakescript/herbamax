import json
from decimal import Decimal, ROUND_HALF_UP
from django.shortcuts import render
from django.views.generic import TemplateView, DetailView, UpdateView, ListView
from django.shortcuts import redirect
from django.http import JsonResponse
from django.core.urlresolvers import reverse_lazy
from django.core.mail import send_mail
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from carton.cart import Cart
from allauth.account.views import PasswordChangeView
from models import Product, HmUser, SiteConfiguration, CouponCode, Order
from forms import CheckoutForm
from functions import get_tax_for_province


class HomeView(TemplateView):
    template_name = 'mainapp/pages/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['products'] = Product.objects.all()[:3]
        return context


class ContactView(TemplateView):
    template_name = 'mainapp/pages/contact.html'


def cart(request):
    context = {}
    config = SiteConfiguration.get_solo()
    cart_ = Cart(request.session)
    shipping_cost = config.shipping_cost

    context['cart'] = cart_
    context['shipping_cost'] = shipping_cost
    total_and_shipping = cart_.total + shipping_cost
    context['total_and_shipping'] = total_and_shipping
    return render(request, 'mainapp/pages/cart.html', context)


class ProductView(DetailView):
    template_name = 'mainapp/pages/product.html'
    model = Product


class ProductsView(ListView):
    template_name = 'mainapp/pages/products.html'
    model = Product

    def get_queryset(self):
        queryset = super(ProductsView, self).get_queryset()
        if self.request.GET.get('qs'):
            q = self.request.GET.get('qs')
            queryset = queryset.filter(
                Q(title__icontains=q) | Q(short_description__icontains=q) | Q(full_description__icontains=q))
        return queryset


def checkout(request):
    context = {}
    _cart = Cart(request.session)
    if _cart.is_empty:
        return redirect('home')

    config = SiteConfiguration.get_solo()
    shipping_cost = config.shipping_cost

    if request.user.is_authenticated():
        checkout_form = CheckoutForm(instance=request.user)
    else:
        checkout_form = CheckoutForm()

    province = 'ON'

    if request.user.is_authenticated():
        if request.user.s_state:
            province = request.user.s_state

    context['form'] = checkout_form
    context['cart'] = _cart
    context['shipping_cost'] = shipping_cost
    total_and_shipping = _cart.total + shipping_cost
    tax_perc, tax_dollars = get_tax_for_province(province, total_and_shipping)
    context['tax_perc'] = tax_perc
    context['tax_dollars'] = tax_dollars
    context['total_and_shipping'] = total_and_shipping
    context['total_and_shipping_and_tax'] = total_and_shipping + tax_dollars

    MONERIS_TEST = True

    if MONERIS_TEST:
        context['form_action_moneris'] = 'https://esqa.moneris.com/HPPDP/index.php'
        context['ps_store_id'] = '4ZZQDtore2'
        context['hpp_key'] = 'hpP6KOLBO2VT'
    else:  # LIVE
        context['form_action_moneris'] = 'https://www3.moneris.com/HPPDP/index.php'
        context['ps_store_id'] = 'ZG8G712992'
        context['hpp_key'] = 'hp4Z5XGV4BQU'

    return render(request, 'mainapp/pages/checkout.html', context)


"""
DASHBOARD
"""


class DashIndexView(TemplateView):
    template_name = 'mainapp/dashboard/dash_index.html'


class DashOrdersView(ListView):
    template_name = 'mainapp/dashboard/dash_orders.html'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class DashAddressesView(UpdateView):
    template_name = 'mainapp/dashboard/dash_address.html'
    model = HmUser
    fields = ['s_first_name', 's_last_name', 's_phone', 's_country', 's_address', 's_city', 's_state',
              's_zip', 'b_first_name', 'b_last_name', 'b_phone', 'b_country', 'b_address', 'b_city',
              'b_state', 'b_zip']
    success_url = reverse_lazy('dash_addresses')

    def get_object(self, queryset=None):
        return self.request.user


class DashPasswordView(PasswordChangeView):
    template_name = 'mainapp/dashboard/dash_password.html'
    success_url = reverse_lazy('dash_index')


"""
AJAX
"""


def ajax_add_to_cart(request):
    qty = request.GET.get('qty', 1)
    product_id = request.GET.get('product_id')

    try:
        _cart = Cart(request.session)
        _product = Product.objects.get(pk=product_id)
        _cart.add(_product, price=_product.get_total(), quantity=qty)

        return JsonResponse(
            {'error': 0, 'message': 'Added to cart', 'count': _cart.count, 'total': _cart.total})
    except:
        return JsonResponse({'error': 1, 'message': 'Error adding to cart'})


def ajax_remove_from_cart(request):
    product_id = request.GET.get('product_id')

    try:
        _cart = Cart(request.session)
        _config = SiteConfiguration.get_solo()
        _product = Product.objects.get(pk=product_id)

        _cart.remove(_product)

        shipping_cost = _config.shipping_cost
        total_and_shipping = _cart.total + shipping_cost

        return JsonResponse({'error': 0,
                             'message': 'Removed from cart',
                             'count': _cart.count,
                             'total': _cart.total,
                             'total_and_shipping': total_and_shipping})
    except:
        return JsonResponse({'error': 1, 'message': 'Error removing from cart'})


def ajax_product_change_quantity(request):
    product_id = request.GET.get('product_id')
    qty = request.GET.get('qty')

    try:
        _cart = Cart(request.session)
        _config = SiteConfiguration.get_solo()
        _product = Product.objects.get(pk=product_id)

        _cart.set_quantity(_product, quantity=qty)
        shipping_cost = _config.shipping_cost
        total_and_shipping = _cart.total + shipping_cost
        _item = None
        for item in _cart.items:
            if item.product == _product:
                _item = item

        return JsonResponse({'error': 0, 'message': 'Quantity has been changed',
                             'item_qty': _item.quantity,
                             'item_subtotal': _item.subtotal,
                             'total': _cart.total,
                             'total_and_shipping': total_and_shipping,
                             'count': _cart.count})
    except:
        return JsonResponse({'error': 1, 'message': 'error changing quantity'})


def ajax_change_tax(request):
    total = request.GET.get('total')
    province = request.GET.get('province')
    code = request.GET.get('code')

    try:
        total = Decimal(total)
        total_decimal = total.quantize(Decimal('.01'), ROUND_HALF_UP)
        tax_perc, tax_doll = get_tax_for_province(province, total_decimal)
        new_total = total_decimal + tax_doll
        if code:
            try:
                code_obj = CouponCode.objects.filter(code=code).first()
                new_total -= code_obj.discount
            except:
                pass
        return JsonResponse(
            {'error': 0, 'message': 'success', 'tax_perc': tax_perc, 'tax_doll': tax_doll, 'new_total': new_total})
    except:
        return JsonResponse({'error': 1, 'message': 'Error'})


def ajax_apply_code(request):
    total = request.GET.get('total')
    code = request.GET.get('code')

    if code and total:
        try:
            code_obj = CouponCode.objects.get(code=code)
            discount = code_obj.discount
            total = Decimal(total)
            total_decimal = total.quantize(Decimal('.01'), ROUND_HALF_UP)
            if discount < total_decimal:
                new_total = total_decimal - discount
                return JsonResponse({'error': 0, 'message': 'Success.', 'discount': discount, 'new_total': new_total,
                                     'code': code_obj.code})
            else:
                return JsonResponse({'error': 1, 'message': 'Code discount is greater than total.'})
        except CouponCode.DoesNotExist:
            return JsonResponse({'error': 1, 'message': 'Coupon code is invalid.'})
    else:
        return JsonResponse({'error': 1, 'message': 'No code.'})


def ajax_send_contact_form(request):
    name = request.POST.get('name', '')
    email = request.POST.get('email', '')
    phone = request.POST.get('phone', '')
    comments = request.POST.get('comments', '')

    config = SiteConfiguration.get_solo()

    try:
        _message = '''
            Full Name: %s
            Email: %s
            Phone: %s
            Comments: %s
            ''' % (name, email, phone, comments)
        send_mail('HerbaMax Contact Form', _message, email, config.get_email_list())
    except:
        return JsonResponse({'error': 1, 'message': 'Invalid header found.'})
    return JsonResponse({'error': 0, 'message': 'success'})


@csrf_exempt
def ajax_create_order(request):
    try:
        config = SiteConfiguration.get_solo()
        cart_ = Cart(request.session)
        order = Order()
        subtotal = cart_.total
        shipping_cost = config.shipping_cost
        tax_perc, tax_dollars = get_tax_for_province(request.POST.get('bill_state_or_province'), subtotal + shipping_cost)

        order.subtotal = subtotal
        order.shipping_cost = shipping_cost
        order.tax_in_percents = tax_perc
        order.tax_in_dollars = tax_dollars
        #
        _user = None
        if request.user.is_authenticated:
            _user = request.user
        order.user = _user
        #
        order.email = request.POST.get('email')
        order.s_phone = request.POST.get('ship_phone', '-')
        order.s_first_name = request.POST.get('ship_first_name', '-')
        order.s_last_name = request.POST.get('ship_last_name', '-')
        order.s_country = request.POST.get('ship_country', '-')
        order.s_address = request.POST.get('ship_address_one', '-')
        order.s_city = request.POST.get('ship_city', '-')
        order.s_state = request.POST.get('ship_state_or_province', '-')
        order.s_zip = request.POST.get('ship_postal_code', '-')

        order.b_phone = request.POST.get('bill_phone', '-')
        order.b_first_name = request.POST.get('bill_first_name', '-')
        order.b_last_name = request.POST.get('bill_last_name', '-')
        order.b_country = request.POST.get('bill_country', '-')
        order.b_address = request.POST.get('bill_address_one', '-')
        order.b_city = request.POST.get('bill_city', '-')
        order.b_state = request.POST.get('bill_state_or_province', '-')
        order.b_zip = request.POST.get('bill_postal_code', '-')

        order.note = request.POST.get('note', '-')
        #

        ccode_discount = 0
        coupon_code = request.POST.get('coupon_code')
        if coupon_code:
            try:
                coupon = CouponCode.objects.get(code=coupon_code)
            except CouponCode.DoesNotExist:
                pass
            else:
                ccode_discount = coupon.discount
                order.coupon_code = coupon_code
                order.coupon_code_discount = ccode_discount

        #
        _items = []
        for item in cart_.items:
            _items.append({"id": item.product.id, "description": item.product.title, "qty": item.quantity,
                           "price": str(item.price)})
        _items_json = json.dumps(_items)
        order.products = _items_json
        # CALCULATE
        total_should_be = subtotal + shipping_cost + tax_dollars - ccode_discount
        print(total_should_be)
        print(request.POST.get('charge_total'))
        if str(total_should_be) == request.POST.get('charge_total'):
            order.total = total_should_be
            order.save()  # Save order. We need an ID
        return JsonResponse({'error': 0, 'message': 'Order created successfully.', 'order_id': order.id})
    except Exception as e:
        print e
        return JsonResponse({'error': 1, 'message': 'Err creating order.'})
