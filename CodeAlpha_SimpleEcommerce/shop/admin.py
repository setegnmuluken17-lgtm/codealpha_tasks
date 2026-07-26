from django.contrib import admin
from django.contrib.auth.models import User

from .models import Cart, CartItem, Category, ContactMessage, Order, OrderItem, Product, ProductReview, UserNotification, UserProfile, Wishlist


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "icon", "is_active", "created_at")
    list_filter = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "brand", "sku", "price", "discount_percent", "stock", "sold_count", "viewed_count", "availability", "is_featured", "is_special_offer")
    list_filter = ("category", "is_active", "is_featured", "is_special_offer")
    list_editable = ("price", "stock", "is_featured", "is_special_offer")
    search_fields = ("name", "description", "brand", "sku")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "product_name", "price", "quantity", "subtotal")
    fields = ("product", "product_name", "price", "quantity", "subtotal", "status")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ("id", "user", "full_name", "phone", "total", "payment_method", "status", "created_at")
    list_filter = ("status", "payment_method", "created_at")
    list_editable = ("status",)
    search_fields = ("full_name", "email", "phone", "user__username")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "city")
    search_fields = ("user__username", "user__email", "phone", "city")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "name", "email", "status", "created_at")
    list_filter = ("status", "created_at")
    list_editable = ("status",)
    search_fields = ("subject", "name", "email", "message")


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("product__name", "user__username", "comment")


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "created_at")
    search_fields = ("user__username", "product__name")


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "message", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("user__username", "title", "message", "source_key")


admin.site.site_header = "CodeAlpha Shop Admin"
admin.site.site_title = "CodeAlpha Shop Admin"
admin.site.index_title = "Admin Dashboard"
