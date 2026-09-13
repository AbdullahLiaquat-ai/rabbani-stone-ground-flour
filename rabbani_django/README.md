# Rabbani Stone-Ground Flour — Django Project

A full Django rebuild of the Rabbani Stone-Ground Flour "Route Master" site: a
solar-powered, stone-ground chakki mill in Hasan Abdal, with customer ordering,
public order tracking, a WhatsApp click-to-chat contact flow, and a staff-only
admin dashboard with charts and status filters.

## Features

- **Light-theme, interactive frontend** — hero with a live order tracker and a
  city-to-city delivery fare estimator, both backed by real Django JSON
  endpoints (not hard-coded JS).
- **WhatsApp contact** — the footer, contact page, and a floating action button
  all link straight to `https://wa.me/923185619572` (pre-filled message), so
  a click opens WhatsApp with the mill's number.
- **Role-based customer/admin split**:
  - Customers register/log in, place orders, and track status — the
    customer-facing templates contain **no controls** to edit an order's
    status.
  - Mill staff log in separately at `/mill-admin/login/` and land on a
    dashboard that is the *only* place status can change. The
    `admin_update_status` view is decorated with `user_passes_test` so even a
    direct POST from a non-staff session is rejected (redirects to admin
    login) — verified in testing, not just hidden in the UI.
- **Admin dashboard**, styled after a modern analytics panel:
  - KPI cards: total orders, on-time delivery rate, total revenue.
  - Chart.js line chart of the last 7 days' orders & revenue.
  - Chart.js doughnut chart of orders by status, with a legend.
  - **Status filter tabs** — All / Pending / Milling in Progress / Packed /
    On the Way / Delivered — filtering the order manifest via `?status=`.
  - Per-order status `<select>` that updates instantly via `fetch()` without
    a full page reload.
- **Stone-ground + solar milling** messaging throughout (hero badge, About
  page, "How It Works" step 2, solar tip banner).

## Project structure

```
rabbani_project/        Django settings, root urls
mill/                    Main app
  models.py              Profile, Product, Order, ContactMessage
  constants.py            Cities, WhatsApp number, delivery-fare calculations
  forms.py                Registration, order, contact forms
  views.py                Public pages, auth, my-account, JSON APIs, admin dashboard
  urls.py
  admin.py                Registers models in Django's built-in /admin/ too
  management/commands/seed_mill.py   Seeds catalog + demo accounts + demo orders
templates/mill/          All HTML templates (base.html + one per page)
static/mill/css/style.css
static/mill/js/app.js         Homepage tracker + fare estimator (fetch)
static/mill/js/dashboard.js   Chart.js setup + AJAX status updates
```

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_mill      # flours + demo admin/customer + demo orders
python manage.py runserver
```

Visit **http://127.0.0.1:8000/**.

## Demo credentials

| Role     | Username        | Password     |
|----------|-----------------|--------------|
| Customer | `demo_customer` | `demo12345`  |
| Admin    | `admin`         | `admin123`   |

Admin login is at `/mill-admin/login/` (separate from customer `/login/`).
Django's own admin panel is also available at `/admin/` using the same
`admin` account, for direct data management if needed.

## Re-seeding

`python manage.py seed_mill` clears existing products, demo orders, and the
`admin` / `demo_customer` accounts, then recreates them — safe to re-run any
time to reset the demo data (it does **not** touch other customers you've
registered).

## Notes on the delivery fare logic

`mill/constants.py` has two functions:

- `calculate_route_fare(origin, destination)` — the general two-city
  estimator used by the homepage widget (mirrors the original "From City /
  To City" calculator: Rs. 200 base, +Rs. 250 if either city is Karachi,
  +Rs. 50 if either city is Hasan Abdal, else +Rs. 120).
- `calculate_order_fare(destination_city)` — used by `Order.save()` for real
  orders, since the mill's origin is always Hasan Abdal (Rs. 100 flat for
  local Hasan Abdal delivery, otherwise the route fare from Hasan Abdal).
