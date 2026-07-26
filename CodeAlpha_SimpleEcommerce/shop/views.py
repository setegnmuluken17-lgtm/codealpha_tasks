from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Avg, Count, Q, Sum
from django.db.models.functions import TruncMonth
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User

from .forms import CheckoutForm, ContactForm, ProfileForm, RegisterForm, ReviewForm, UserUpdateForm
from .models import Cart, CartItem, Category, ContactMessage, Order, OrderItem, Product, ProductReview, UserNotification, UserProfile, Wishlist


def _products():
    return Product.objects.filter(is_active=True).select_related("category")


def _cart(user):
    return Cart.objects.get_or_create(user=user)[0]


class AdminAwareLoginView(LoginView):
    template_name = "registration/login.html"

    def get_success_url(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return "/dashboard/stats/"
        return super().get_success_url()


def home(request):
    products = _products()
    recent_ids = request.session.get("recently_viewed", [])
    recently_viewed = Product.objects.filter(id__in=recent_ids, is_active=True)
    return render(request, "shop/home.html", {
        "featured": products.filter(is_featured=True)[:8],
        "new_arrivals": products.order_by("-created_at")[:8],
        "offers": products.filter(Q(is_special_offer=True) | Q(discount_percent__gt=0))[:8],
        "trending": products.order_by("-viewed_count", "-sold_count")[:8],
        "best_sellers": products.order_by("-sold_count")[:8],
        "categories": Category.objects.filter(is_active=True)[:12],
        "recently_viewed": recently_viewed,
    })


def product_list(request):
    products = _products()
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")
    sort = request.GET.get("sort", "")
    min_price = request.GET.get("min_price", "")
    max_price = request.GET.get("max_price", "")
    rating = request.GET.get("rating", "")
    availability = request.GET.get("availability", "")
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(brand__icontains=query) | Q(sku__icontains=query))
    if category:
        products = products.filter(category__slug=category)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    if availability == "in":
        products = products.filter(stock__gt=0)
    elif availability == "out":
        products = products.filter(stock=0)
    products = products.annotate(avg_rating=Avg("reviews__rating"))
    if rating:
        products = products.filter(avg_rating__gte=rating)
    if sort == "price_asc":
        products = products.order_by("price")
    elif sort == "price_desc":
        products = products.order_by("-price")
    elif sort == "newest":
        products = products.order_by("-created_at")
    elif sort == "rating":
        products = products.order_by("-avg_rating", "-sold_count")
    paginator = Paginator(products, 8)
    return render(request, "shop/product_list.html", {
        "page_obj": paginator.get_page(request.GET.get("page")),
        "categories": Category.objects.filter(is_active=True),
        "query": query,
        "selected_category": category,
        "sort": sort,
        "min_price": min_price,
        "max_price": max_price,
        "rating": rating,
        "availability": availability,
    })


def categories(request):
    return render(request, "shop/categories.html", {"categories": Category.objects.filter(is_active=True)})


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = _products().filter(category=category)
    return render(request, "shop/category_detail.html", {"category": category, "products": products})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    Product.objects.filter(pk=product.pk).update(viewed_count=product.viewed_count + 1)
    recent_ids = [item for item in request.session.get("recently_viewed", []) if item != product.id]
    request.session["recently_viewed"] = [product.id] + recent_ids[:9]
    recently_viewed = Product.objects.filter(id__in=recent_ids[:10], is_active=True)
    related = _products().filter(category=product.category).exclude(pk=product.pk)[:4]
    is_saved = request.user.is_authenticated and Wishlist.objects.filter(user=request.user, product=product).exists()
    review_form = ReviewForm()
    if request.method == "POST" and request.user.is_authenticated:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            ProductReview.objects.update_or_create(
                product=product,
                user=request.user,
                defaults=review_form.cleaned_data,
            )
            messages.success(request, "Review saved.")
            return redirect("product_detail", pk=product.id)
    return render(request, "shop/product_detail.html", {
        "product": product,
        "related": related,
        "is_saved": is_saved,
        "review_form": review_form,
        "reviews": product.reviews.select_related("user")[:8],
        "recently_viewed": recently_viewed,
    })


@login_required
def cart_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    quantity = max(1, int(request.POST.get("quantity", 1)))
    cart = _cart(request.user)
    item, _ = CartItem.objects.get_or_create(cart=cart, product=product)
    item.quantity = min(product.stock, item.quantity + quantity)
    item.save()
    messages.success(request, "Product added to cart.")
    return redirect(request.POST.get("next") or "cart_detail")


@login_required
def cart_detail(request):
    cart = _cart(request.user)
    return render(request, "shop/cart.html", {"cart": cart, "items": cart.items.select_related("product")})


@login_required
def cart_increase(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.quantity = min(item.product.stock, item.quantity + 1)
    item.save()
    return redirect("cart_detail")


@login_required
def cart_decrease(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if item.quantity <= 1:
        item.delete()
    else:
        item.quantity -= 1
        item.save()
    return redirect("cart_detail")


@login_required
def cart_remove(request, item_id):
    get_object_or_404(CartItem, id=item_id, cart__user=request.user).delete()
    messages.success(request, "Item removed.")
    return redirect("cart_detail")


@login_required
@transaction.atomic
def checkout(request):
    cart = _cart(request.user)
    items = list(cart.items.select_related("product"))
    if not items:
        messages.info(request, "Your cart is empty.")
        return redirect("product_list")
    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total = cart.total
            order.save()
            for item in items:
                if item.product.stock < item.quantity:
                    messages.error(request, f"Only {item.product.stock} {item.product.name} available.")
                    return redirect("cart_detail")
                OrderItem.objects.create(order=order, product=item.product, product_name=item.product.name, price=item.product.final_price, quantity=item.quantity)
                item.product.stock -= item.quantity
                item.product.sold_count += item.quantity
                item.product.save(update_fields=["stock", "sold_count"])
            cart.items.all().delete()
            send_mail(
                subject=f"Order #{order.id} confirmed",
                message=f"Thank you for your order. Total: ${order.total}. Payment method: Cash on Delivery.",
                from_email="orders@codealpha.shop",
                recipient_list=[order.email],
                fail_silently=True,
            )
            messages.success(request, f"Order #{order.id} placed successfully.")
            return redirect("order_detail", order_id=order.id)
    else:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        form = CheckoutForm(initial={
            "full_name": request.user.get_full_name() or request.user.username,
            "email": request.user.email,
            "phone": profile.phone,
            "country": "Kenya",
            "address": profile.address,
            "city": profile.city,
            "payment_method": "cod",
        })
    return render(request, "shop/checkout.html", {"form": form, "items": items, "cart": cart})


@login_required
def order_list(request):
    return render(request, "shop/orders.html", {"orders": request.user.orders.all()})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "shop/order_detail.html", {"order": order})


@login_required
def notification_open(request, notification_id):
    notification = get_object_or_404(UserNotification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save(update_fields=["is_read"])
    return redirect(notification.target_url)


def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        UserProfile.objects.create(user=user, phone=form.cleaned_data["phone"])
        login(request, user)
        messages.success(request, "Account created.")
        return redirect("profile")
    return render(request, "registration/register.html", {"form": form})


@login_required
def profile(request):
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)
    wishlist = Wishlist.objects.filter(user=request.user).select_related("product")[:8]
    return render(request, "shop/profile.html", {"profile": profile_obj, "orders": request.user.orders.all()[:5], "wishlist": wishlist})


@login_required
def edit_profile(request):
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)
    user_form = UserUpdateForm(request.POST or None, instance=request.user)
    profile_form = ProfileForm(request.POST or None, instance=profile_obj)
    if request.method == "POST" and user_form.is_valid() and profile_form.is_valid():
        user_form.save()
        profile_form.save()
        messages.success(request, "Profile updated.")
        return redirect("profile")
    return render(request, "shop/edit_profile.html", {"user_form": user_form, "profile_form": profile_form})


def about(request):
    return render(request, "shop/about.html")


def contact(request):
    form = ContactForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Message sent.")
        return redirect("contact")
    return render(request, "shop/contact.html", {"form": form})


@login_required
def wishlist_toggle(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    saved = Wishlist.objects.filter(user=request.user, product=product)
    if saved.exists():
        saved.delete()
        messages.info(request, "Removed from wishlist.")
    else:
        Wishlist.objects.create(user=request.user, product=product)
        messages.success(request, "Saved to wishlist.")
    next_url = request.POST.get("next")
    if next_url:
        return redirect(next_url)
    return redirect("product_detail", pk=product.id)


@login_required
def wishlist(request):
    items = Wishlist.objects.filter(user=request.user).select_related("product", "product__category")
    return render(request, "shop/wishlist.html", {"items": items})


@login_required
def wishlist_move_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = _cart(request.user)
    item, _ = CartItem.objects.get_or_create(cart=cart, product=product)
    item.quantity = min(product.stock, item.quantity + 1)
    item.save()
    Wishlist.objects.filter(user=request.user, product=product).delete()
    messages.success(request, "Moved product to cart.")
    return redirect("cart_detail")


@login_required
def review_delete(request, review_id):
    review = get_object_or_404(ProductReview, id=review_id, user=request.user)
    product_id = review.product_id
    review.delete()
    messages.success(request, "Review deleted.")
    return redirect("product_detail", pk=product_id)


def search_suggestions(request):
    query = request.GET.get("q", "").strip()
    results = []
    if query:
        results = list(_products().filter(name__icontains=query).values("id", "name")[:8])
    return JsonResponse({"results": results})


def _is_admin_user(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def _require_dashboard_admin(request):
    if not _is_admin_user(request.user):
        messages.error(request, "Access denied. Admin users only.")
        return redirect("home")
    return None


@login_required
def admin_stats(request):
    denied = _require_dashboard_admin(request)
    if denied:
        return denied

    admin_query = request.GET.get("admin_q", "").strip()
    active_orders = Order.objects.select_related("user").prefetch_related("items").exclude(status__in=["delivered", "cancelled"])
    recent_orders = active_orders[:10]
    recent_users = User.objects.order_by("-date_joined")[:10]
    contact_messages = ContactMessage.objects.order_by("-created_at")[:10]
    recent_reviews = ProductReview.objects.select_related("user", "product").order_by("-created_at")[:10]
    low_stock_products = Product.objects.select_related("category").filter(is_active=True, stock__lt=5).order_by("stock", "name")[:10]
    low_stock_count = Product.objects.filter(is_active=True, stock__lt=5).count()

    stats = {
        "users": User.objects.count(),
        "products": Product.objects.count(),
        "categories": Category.objects.count(),
        "orders": Order.objects.count(),
        "revenue": Order.objects.exclude(status="cancelled").aggregate(total=Sum("total"))["total"] or 0,
        "pending_orders": Order.objects.filter(status="pending").count(),
        "processing_orders": Order.objects.filter(status="processing").count(),
        "shipped_orders": Order.objects.filter(status="shipped").count(),
        "delivered_orders": Order.objects.filter(status="delivered").count(),
        "cancelled_orders": Order.objects.filter(status="cancelled").count(),
        "messages": ContactMessage.objects.count(),
        "reviews": ProductReview.objects.count(),
        "low_stock": low_stock_count,
    }
    order_months = list(
        Order.objects.annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(order_count=Count("id"), revenue=Sum("total"))
        .order_by("month")
    )
    user_months = list(
        User.objects.annotate(month=TruncMonth("date_joined"))
        .values("month")
        .annotate(user_count=Count("id"))
        .order_by("month")
    )
    status_rows = list(Order.objects.values("status").annotate(total=Count("id")).order_by("status"))
    status_labels = dict(Order.STATUS_CHOICES)
    chart_data = {
        "salesLabels": [row["month"].strftime("%b %Y") for row in order_months if row["month"]],
        "salesData": [row["order_count"] for row in order_months if row["month"]],
        "revenueLabels": [row["month"].strftime("%b %Y") for row in order_months if row["month"]],
        "revenueData": [float(row["revenue"] or 0) for row in order_months if row["month"]],
        "userLabels": [row["month"].strftime("%b %Y") for row in user_months if row["month"]],
        "userData": [row["user_count"] for row in user_months if row["month"]],
        "statusLabels": [status_labels.get(row["status"], row["status"].title()) for row in status_rows],
        "statusData": [row["total"] for row in status_rows],
    }
    search_results = None
    if admin_query:
        order_filter = Q(full_name__icontains=admin_query) | Q(email__icontains=admin_query) | Q(phone__icontains=admin_query)
        if admin_query.isdigit():
            order_filter |= Q(id=int(admin_query))
        search_results = {
            "orders": Order.objects.filter(order_filter).order_by("-created_at")[:5],
            "products": Product.objects.filter(Q(name__icontains=admin_query) | Q(brand__icontains=admin_query) | Q(sku__icontains=admin_query)).select_related("category")[:5],
            "users": User.objects.filter(Q(username__icontains=admin_query) | Q(email__icontains=admin_query) | Q(first_name__icontains=admin_query) | Q(last_name__icontains=admin_query)).order_by("-date_joined")[:5],
        }
    notification_count = (
        Order.objects.filter(status="pending").count()
        + ContactMessage.objects.filter(status="new").count()
        + low_stock_count
    )
    return render(
        request,
        "shop/admin_stats.html",
        {
            "stats": stats,
            "recent_orders": recent_orders,
            "recent_users": recent_users,
            "contact_messages": contact_messages,
            "recent_reviews": recent_reviews,
            "low_stock_products": low_stock_products,
            "notification_count": notification_count,
            "chart_data": chart_data,
            "admin_query": admin_query,
            "search_results": search_results,
        },
    )


@login_required
def admin_order_detail(request, order_id):
    denied = _require_dashboard_admin(request)
    if denied:
        return denied
    order = get_object_or_404(Order.objects.select_related("user").prefetch_related("items__product"), id=order_id)
    subtotal = sum(item.subtotal for item in order.items.all())
    shipping_fee = order.total - subtotal
    return render(request, "shop/admin_order_detail.html", {
        "order": order,
        "subtotal": subtotal,
        "shipping_fee": shipping_fee,
    })


@login_required
@transaction.atomic
def admin_order_status(request, order_id, status):
    denied = _require_dashboard_admin(request)
    if denied:
        return denied
    valid_statuses = {choice[0] for choice in Order.STATUS_CHOICES}
    if status not in valid_statuses:
        messages.error(request, "Invalid order status.")
        return redirect("admin_order_detail", order_id=order_id)
    order = get_object_or_404(Order, id=order_id)
    order.status = status
    order.save(update_fields=["status"])
    messages.success(request, f"Order #{order.id} updated to {order.get_status_display()}.")
    return redirect("admin_order_detail", order_id=order.id)


@login_required
@transaction.atomic
def admin_order_item_status(request, item_id):
    denied = _require_dashboard_admin(request)
    if denied:
        return denied
    item = get_object_or_404(OrderItem.objects.select_related("order"), id=item_id)
    status = request.POST.get("status", "")
    valid_statuses = {choice[0] for choice in OrderItem.STATUS_CHOICES}
    if status not in valid_statuses:
        messages.error(request, "Invalid product status.")
        return redirect("admin_order_detail", order_id=item.order_id)
    item.status = status
    item.save(update_fields=["status"])

    if status != "pending":
        UserNotification.objects.get_or_create(
            user=item.order.user,
            source_key=f"order-item:{item.id}:{status}",
            defaults={
                "title": "Ordered status",
                "message": item.get_status_display(),
                "target_url": f"/orders/{item.order_id}/",
                "icon": "fa-truck-fast" if status == "shipped" else "fa-circle-check" if status == "delivered" else "fa-circle-xmark" if status == "cancelled" else "fa-box",
            },
        )

    item_statuses = list(item.order.items.values_list("status", flat=True))
    if item_statuses and len(set(item_statuses)) == 1 and item_statuses[0] in {choice[0] for choice in Order.STATUS_CHOICES}:
        item.order.status = item_statuses[0]
        item.order.save(update_fields=["status"])
    elif item.order.status == "pending" and status in {"approved", "processing", "shipped"}:
        item.order.status = status
        item.order.save(update_fields=["status"])

    messages.success(request, f"{item.product_name} status updated to {item.get_status_display()}.")
    return redirect("admin_order_detail", order_id=item.order_id)


@login_required
def admin_contact_message_action(request, message_id, action):
    denied = _require_dashboard_admin(request)
    if denied:
        return denied
    contact_message = get_object_or_404(ContactMessage, id=message_id)
    if action == "delete":
        contact_message.delete()
        messages.success(request, "Contact message deleted.")
    elif action in {"read", "replied", "closed"}:
        contact_message.status = action
        contact_message.save(update_fields=["status"])
        messages.success(request, f"Contact message marked as {contact_message.get_status_display()}.")
    else:
        messages.error(request, "Invalid contact message action.")
    return redirect("admin_stats")
