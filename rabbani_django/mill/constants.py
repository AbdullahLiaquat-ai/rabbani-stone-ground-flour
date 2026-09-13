MILL_CITY = 'Hasan Abdal'

CITIES = [
    'Hasan Abdal',
    'Lahore',
    'Karachi',
    'Islamabad',
    'Rawalpindi',
    'Multan',
    'Faisalabad',
]

WHATSAPP_NUMBER = '923185619572'
WHATSAPP_DISPLAY = '0318-5619572'
CONTACT_EMAIL = 'info@rabbaniflour.pk'
SHOP_ADDRESS = 'Shop no 12, Business Square, opposite Khawaja Nagar Darbar, Hasan Abdal'
SHOP_HOURS = 'Mon–Sat: 9 AM – 7 PM'


def whatsapp_link(message=None):
    base = f'https://wa.me/{WHATSAPP_NUMBER}'
    if message:
        from urllib.parse import quote
        return f'{base}?text={quote(message)}'
    return base


def calculate_route_fare(origin, destination):
    """Generic two-city delivery estimate, used by the public homepage estimator."""
    if not origin or not destination or origin == destination:
        return None
    base = 200
    if origin == 'Karachi' or destination == 'Karachi':
        extra = 250
    elif origin == MILL_CITY or destination == MILL_CITY:
        extra = 50
    else:
        extra = 120
    return base + extra


def calculate_order_fare(destination_city):
    """Delivery fare from the mill in Hasan Abdal to a customer's city."""
    if destination_city == MILL_CITY:
        return 100
    fare = calculate_route_fare(MILL_CITY, destination_city)
    return fare if fare is not None else 250
