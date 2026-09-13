import json
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Sum
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST, require_GET

from .constants import CITIES, MILL_CITY, WHATSAPP_NUMBER, WHATSAPP_DISPLAY, CONTACT_EMAIL, SHOP_ADDRESS, SHOP_HOURS, whatsapp_link, calculate_route_fare
from .forms import RegisterForm, OrderForm, ContactForm
from .models import Product, Order, Profile


def _is_staff(user):
    return user.is_authenticated and user.is_staff


def _brand_context():
    return {
        'cities': CITIES,
        'mill_city': MILL_CITY,
        'whatsapp_number': WHATSAPP_NUMBER,
        'whatsapp_display': WHATSAPP_DISPLAY,
        'whatsapp_link': whatsapp_link("Hi Rabbani Stone-Ground, I'd like to ask about flour orders."),
        'contact_email': CONTACT_EMAIL,
        'shop_address': SHOP_ADDRESS,
        'shop_hours': SHOP_HOURS,
    }


def home(request):
    context = _brand_context()
    context['products'] = Product.objects.filter(is_available=True)
    context['total_orders'] = Order.objects.count()
    context['delivered_orders'] = Order.objects.filter(status=Order.STATUS_DELIVERED).count()
    context['cities_served'] = len(CITIES)
    return render(request, 'mill/home.html', context)


def about(request):
    return render(request, 'mill/about.html', _brand_context())


def services(request):
    context = _brand_context()
    context['products'] = Product.objects.filter(is_available=True)
    return render(request, 'mill/services.html', context)


def contact(request):
    context = _brand_context()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thanks for reaching out — our team will call you back shortly.")
            form = ContactForm()
    else:
        form = ContactForm()
    context['form'] = form
    return render(request, 'mill/contact.html', context)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('mill:my_account')
    context = _brand_context()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user, phone=form.cleaned_data['phone'], city=form.cleaned_data['city'])
            login(request, user)
            messages.success(request, f"Welcome, {user.first_name or user.username}! Your account is ready.")
            return redirect('mill:my_account')
    else:
        form = RegisterForm()
    context['form'] = form
    return render(request, 'mill/register.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('mill:my_account')
    context = _brand_context()
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('mill:my_account')
        error = 'Incorrect username or password.'
    context['error'] = error
    return render(request, 'mill/login.html', context)


def logout_view(request):
    logout(request)
    return redirect('mill:home')


@login_required
def my_account(request):
    context = _brand_context()
    profile, _ = Profile.objects.get_or_create(user=request.user, defaults={'city': MILL_CITY})

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.customer = request.user
            order.save()
            messages.success(request, f"Order placed! Your tracking ID is {order.tracking_number}.")
            return redirect('mill:my_account')
    else:
        form = OrderForm(initial={'phone': profile.phone, 'destination_city': profile.city})

    context['form'] = form
    context['profile'] = profile
    context['orders'] = Order.objects.filter(customer=request.user).select_related('product')
    return render(request, 'mill/my_account.html', context)


@require_GET
def track_order_api(request):
    tracking_id = request.GET.get('id', '').strip()
    if not tracking_id:
        return JsonResponse({'found': False, 'error': 'Please enter an Order ID.'})
    order = Order.objects.filter(tracking_number__iexact=tracking_id).select_related('product').first()
    if not order:
        return JsonResponse({'found': False, 'error': 'No order found for that tracking ID.'})
    return JsonResponse({
        'found': True,
        'tracking_number': order.tracking_number,
        'product': order.product.name,
        'weight_kg': str(order.weight_kg),
        'city': order.destination_city,
        'status': order.get_status_display(),
        'status_code': order.status,
    })


@require_GET
def estimate_fare_api(request):
    origin = request.GET.get('origin', '').strip()
    destination = request.GET.get('destination', '').strip()
    fare = calculate_route_fare(origin, destination)
    if fare is None:
        return JsonResponse({'ok': False, 'message': 'Select two different cities for an estimate.'})
    return JsonResponse({'ok': True, 'fare': fare, 'message': f'Estimated delivery: Rs. {fare} (includes stone-ground handling)'})


def admin_login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('mill:admin_dashboard')
    context = _brand_context()
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('mill:admin_dashboard')
        elif user is not None:
            error = 'This account does not have mill staff access.'
        else:
            error = 'Invalid admin credentials.'
    context['error'] = error
    return render(request, 'mill/admin_login.html', context)


def admin_logout_view(request):
    logout(request)
    return redirect('mill:admin_login')


@user_passes_test(_is_staff, login_url='mill:admin_login')
def admin_dashboard(request):
    context = _brand_context()

    status_filter = request.GET.get('status', 'ALL')
    orders_qs = Order.objects.select_related('product', 'customer').all()
    if status_filter != 'ALL':
        orders_qs = orders_qs.filter(status=status_filter)

    all_orders = Order.objects.all()
    total_orders = all_orders.count()
    delivered_count = all_orders.filter(status=Order.STATUS_DELIVERED).count()
    on_time_rate = round((delivered_count / total_orders) * 100, 1) if total_orders else 0
    total_revenue = all_orders.aggregate(total=Sum('total_amount'))['total'] or 0

    status_counts = {code: 0 for code, _ in Order.STATUS_CHOICES}
    for row in all_orders.values('status').annotate(count=Count('id')):
        status_counts[row['status']] = row['count']

    today = timezone.now().date()
    trend_labels = []
    trend_revenue = []
    trend_orders = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_orders = all_orders.filter(created_at__date=day)
        trend_labels.append(day.strftime('%d %b'))
        trend_revenue.append(float(day_orders.aggregate(total=Sum('total_amount'))['total'] or 0))
        trend_orders.append(day_orders.count())

    context.update({
        'status_filter': status_filter,
        'status_choices': Order.STATUS_CHOICES,
        'orders': orders_qs[:200],
        'total_orders': total_orders,
        'delivered_count': delivered_count,
        'on_time_rate': on_time_rate,
        'total_revenue': total_revenue,
        'status_counts_json': json.dumps(status_counts),
        'status_labels_json': json.dumps([label for _, label in Order.STATUS_CHOICES]),
        'status_values_json': json.dumps([status_counts[code] for code, _ in Order.STATUS_CHOICES]),
        'trend_labels_json': json.dumps(trend_labels),
        'trend_revenue_json': json.dumps(trend_revenue),
        'trend_orders_json': json.dumps(trend_orders),
    })
    return render(request, 'mill/admin_dashboard.html', context)


@require_POST
@user_passes_test(_is_staff, login_url='mill:admin_login')
def admin_update_status(request, tracking_number):
    order = get_object_or_404(Order, tracking_number=tracking_number)
    new_status = request.POST.get('status')
    valid_codes = dict(Order.STATUS_CHOICES)
    if new_status not in valid_codes:
        return JsonResponse({'ok': False, 'error': 'Invalid status.'}, status=400)
    order.status = new_status
    order.save()
    return JsonResponse({'ok': True, 'status': new_status, 'status_display': valid_codes[new_status]})
