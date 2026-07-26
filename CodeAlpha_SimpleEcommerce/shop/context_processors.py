from .models import Cart, Category, ContactMessage, Order, Product, UserNotification, Wishlist


def store_context(request):
    count = 0
    admin_new_orders = []
    admin_new_messages = []
    user_notifications = []
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        count = sum(item.quantity for item in cart.items.all())
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        if request.user.is_staff or request.user.is_superuser:
            admin_new_orders = Order.objects.filter(status="pending").order_by("-created_at")[:6]
            admin_new_messages = ContactMessage.objects.filter(status="new").order_by("-created_at")[:6]
            admin_notification_count = (
                Order.objects.filter(status="pending").count()
                + ContactMessage.objects.filter(status="new").count()
                + Product.objects.filter(is_active=True, stock__lt=5).count()
            )
        else:
            admin_notification_count = 0
            user_notifications = UserNotification.objects.filter(user=request.user, is_read=False)[:8]
    else:
        wishlist_count = 0
        admin_notification_count = 0
    return {
        "nav_categories": Category.objects.filter(is_active=True)[:8],
        "cart_item_count": count,
        "wishlist_count": wishlist_count,
        "admin_notification_count": admin_notification_count,
        "admin_new_orders": admin_new_orders,
        "admin_new_messages": admin_new_messages,
        "user_notification_count": UserNotification.objects.filter(user=request.user, is_read=False).count() if request.user.is_authenticated else 0,
        "user_notifications": user_notifications,
    }
