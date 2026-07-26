from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("shop/", views.product_list, name="product_list"),
    path("categories/", views.categories, name="categories"),
    path("categories/<slug:slug>/", views.category_detail, name="category_detail"),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
    path("wishlist/", views.wishlist, name="wishlist"),
    path("wishlist/<int:product_id>/", views.wishlist_toggle, name="wishlist_toggle"),
    path("wishlist/<int:product_id>/move-to-cart/", views.wishlist_move_to_cart, name="wishlist_move_to_cart"),
    path("reviews/<int:review_id>/delete/", views.review_delete, name="review_delete"),
    path("search/suggestions/", views.search_suggestions, name="search_suggestions"),
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/increase/<int:item_id>/", views.cart_increase, name="cart_increase"),
    path("cart/decrease/<int:item_id>/", views.cart_decrease, name="cart_decrease"),
    path("cart/remove/<int:item_id>/", views.cart_remove, name="cart_remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("orders/", views.order_list, name="order_list"),
    path("orders/<int:order_id>/", views.order_detail, name="order_detail"),
    path("notifications/<int:notification_id>/", views.notification_open, name="notification_open"),
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("contact/", views.contact, name="contact"),
    path("dashboard/stats/", views.admin_stats, name="admin_stats"),
    path("dashboard/orders/<int:order_id>/", views.admin_order_detail, name="admin_order_detail"),
    path("dashboard/orders/<int:order_id>/status/<str:status>/", views.admin_order_status, name="admin_order_status"),
    path("dashboard/order-items/<int:item_id>/status/", views.admin_order_item_status, name="admin_order_item_status"),
    path("dashboard/messages/<int:message_id>/<str:action>/", views.admin_contact_message_action, name="admin_contact_message_action"),
]
