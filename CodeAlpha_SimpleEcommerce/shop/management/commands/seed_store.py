from decimal import Decimal
from urllib.parse import quote_plus

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from shop.models import Category, Product


CATEGORY_DATA = {
    "Electronics": ("Laptop, Gaming Laptop, Smartphone, Tablet, Smart Watch, Headphones, Bluetooth Speaker, Power Bank, Camera, Keyboard, Wireless Router, Monitor, Printer, Scanner, External SSD, Drone, Projector, Smart TV, VR Headset, Graphics Tablet", "PC", "https://images.unsplash.com/photo-1498049794561-7780e7231661?auto=format&fit=crop&w=900&q=80"),
    "Accessories": ("Phone Case, Laptop Sleeve, USB Cable, Wireless Mouse, Screen Protector, Desk Mat, Memory Card, USB Hub, Webcam Cover, Cable Organizer, Phone Stand, Stylus Pen, Tablet Cover, Laptop Cooling Pad, Card Reader, Bluetooth Tracker, Tripod Stand, Ring Light, Power Adapter, Cleaning Kit", "Plug", "https://images.unsplash.com/photo-1625961332771-3f40b0e2bdcf?auto=format&fit=crop&w=900&q=80"),
    "Audio": ("Noise Cancelling Headphones, Earbuds, Bluetooth Speaker, Soundbar, Studio Microphone, Portable Radio, DJ Headset, Bookshelf Speaker, Audio Mixer, Wireless Earphones, Subwoofer, Conference Speaker, Podcast Microphone, Audio Interface, Karaoke Mic, Neckband Earphones, Party Speaker, Mini Speaker, Hi-Fi Amplifier, Turntable", "Music", "https://images.unsplash.com/photo-1545454675-3531b543be5d?auto=format&fit=crop&w=900&q=80"),
    "Fashion": ("T-Shirt, Jeans, Jacket, Hoodie, Shirt, Dress, Sweater, Shorts, Skirt, Blazer, Polo Shirt, Cardigan, Tracksuit, Jumpsuit, Coat, Leggings, Scarf, Cap, Belt, Formal Suit", "Shirt", "https://images.unsplash.com/photo-1445205170230-053b83016050?auto=format&fit=crop&w=900&q=80"),
    "Shoes": ("Running Shoes, Sneakers, Leather Shoes, Boots, Sandals, Loafers, Basketball Shoes, Formal Shoes, Hiking Shoes, Slip Ons, Training Shoes, High Heels, Flat Shoes, Soccer Cleats, Work Boots, Kids Sneakers, Canvas Shoes, Oxford Shoes, Beach Slides, Trail Shoes", "Shoe", "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=80"),
    "Watches": ("Smart Watch, Classic Watch, Sport Watch, Leather Watch, Digital Watch, Luxury Watch, Fitness Band, Minimal Watch, Chronograph, Kids Watch, Dive Watch, Pocket Watch, Ceramic Watch, Solar Watch, Hybrid Watch, Rose Gold Watch, Metal Strap Watch, Rubber Strap Watch, Couple Watch, Alarm Watch", "Watch", "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=900&q=80"),
    "Gaming": ("Gaming Keyboard, Gaming Mouse, Gaming Headset, Controller, Gaming Chair, Mouse Pad, Webcam, Microphone, Console Stand, RGB Speaker, PlayStation Console, Xbox Console, Nintendo Console, Gaming Monitor, Capture Card, Racing Wheel, Joystick, VR Controller, Game Storage Case, Cooling Fan", "Game", "https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=900&q=80"),
    "Books": ("Python Book, Business Book, Mystery Novel, History Book, Science Book, Children Book, Cooking Book, Design Book, Poetry Book, Study Planner, Romance Novel, Fantasy Novel, Biography, Travel Guide, Language Book, Math Workbook, Self Help Book, Comic Book, Art Book, Exam Prep Book", "Book", "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=900&q=80"),
    "Beauty": ("Skincare Kit, Lipstick, Perfume, Face Cream, Hair Dryer, Makeup Brush, Sunscreen, Shampoo, Nail Polish, Serum, Face Wash, Conditioner, Body Lotion, Eyeliner, Mascara, Foundation, Hair Straightener, Beard Oil, Bath Bomb, Makeup Palette", "Beauty", "https://images.unsplash.com/photo-1596462502278-27bfdc403348?auto=format&fit=crop&w=900&q=80"),
    "Sports": ("Yoga Mat, Football, Dumbbell Pair, Resistance Bands, Water Bottle, Tennis Racket, Basketball, Training Gloves, Jump Rope, Gym Bag, Boxing Gloves, Skipping Rope, Cycling Helmet, Swim Goggles, Cricket Bat, Badminton Racket, Protein Shaker, Ankle Weights, Fitness Tracker, Soccer Goal Net", "Sport", "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=900&q=80"),
    "Kitchen": ("Blender, Cookware Set, Coffee Maker, Knife Set, Toaster, Air Fryer, Mixing Bowls, Cutting Board, Storage Jars, Electric Kettle, Sandwich Maker, Juicer, Microwave Oven, Kitchen Tongs, Garlic Press, Peeler Set, Colander, Dish Soap Dispenser, Oven Mitts, Measuring Spoons", "Cook", "https://images.unsplash.com/photo-1556911220-bff31c812dba?auto=format&fit=crop&w=900&q=80"),
    "Home & Kitchen": ("Dinner Plate Set, Pressure Cooker, Food Processor, Spice Rack, Frying Pan, Kitchen Scale, Water Filter, Dish Rack, Measuring Cups, Soup Pot, Tea Kettle, Lunch Box, Rice Cooker, Hand Mixer, Bakeware Set, Glass Cups, Serving Tray, Apron Set, Vegetable Chopper, Kitchen Towels", "Kitchen", "https://images.unsplash.com/photo-1556912173-3bb406ef7e77?auto=format&fit=crop&w=900&q=80"),
    "Home & Living": ("Table Lamp, Throw Pillow, Wall Clock, Rug, Bookshelf, Curtains, Plant Pot, Desk Organizer, Blanket, Mirror, Sofa Cover, Bed Sheet Set, Laundry Basket, Candle Holder, Wall Art, Shoe Rack, Storage Box, Floor Lamp, Room Divider, Mattress Protector", "Home", "https://images.unsplash.com/photo-1484154218962-a197022b5858?auto=format&fit=crop&w=900&q=80"),
    "Automotive": ("Car Vacuum, Tire Inflator, Dash Camera, Car Charger, Seat Cover, Floor Mats, Jump Starter, Car Polish, Phone Mount, Tool Kit, Wiper Blades, Air Freshener, Engine Oil, Car Shampoo, Steering Cover, Emergency Kit, Tire Gauge, Brake Cleaner, Roof Rack, Car Organizer", "Car", "https://images.unsplash.com/photo-1542362567-b07e54358753?auto=format&fit=crop&w=900&q=80"),
    "Groceries": ("Organic Coffee, Green Tea, Honey Jar, Olive Oil, Pasta Pack, Breakfast Cereal, Peanut Butter, Mixed Nuts, Brown Rice, Tomato Sauce, Dark Chocolate, Fruit Jam, Oats Pack, Lentils, Chickpeas, Coconut Milk, Granola, Pasta Sauce, Herbal Tea, Cashew Nuts", "Cart", "https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=900&q=80"),
    "Bags": ("Tech Backpack, Tote Bag, Travel Duffel, Laptop Bag, Crossbody Bag, Wallet, School Bag, Gym Sack, Handbag, Camera Bag, Messenger Bag, Shoulder Bag, Makeup Bag, Lunch Bag, Hiking Backpack, Rolling Suitcase, Clutch Bag, Diaper Bag, Sling Bag, Waterproof Dry Bag", "Bag", "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=80"),
    "Toys": ("Building Blocks, Puzzle Set, Toy Car, Plush Bear, Science Kit, Doll House, Board Game, Art Kit, Robot Toy, Outdoor Kite, Remote Control Car, Train Set, Play Kitchen, Water Gun, Baby Rattle, Magnetic Tiles, Action Figure, Clay Set, Kids Tablet, Dinosaur Toy", "Toy", "https://images.unsplash.com/photo-1587654780291-39c9404d746b?auto=format&fit=crop&w=900&q=80"),
}


def product_image(product_name, category_name, variant=1):
    query = quote_plus(product_name.replace(" ", ","))
    lock = sum(ord(char) for char in f"{product_name}{category_name}{variant}")
    return f"https://loremflickr.com/900/700/{query}/all?lock={lock}"


class Command(BaseCommand):
    help = "Seed 12 categories and at least 120 products."

    def handle(self, *args, **options):
        created_products = 0
        for category_index, (category_name, (product_names, icon, image)) in enumerate(CATEGORY_DATA.items(), start=1):
            category, _ = Category.objects.update_or_create(
                name=category_name,
                defaults={
                    "slug": slugify(category_name),
                    "description": f"Handpicked {category_name.lower()} products with discounts, ratings, and fast checkout.",
                    "icon": icon,
                    "image_url": image,
                    "is_active": True,
                },
            )
            for product_index, product_name in enumerate([name.strip() for name in product_names.split(",")], start=1):
                sku = f"{slugify(category_name).upper()[:4]}-{product_index:03d}"
                base_price = Decimal(18 + category_index * 7 + product_index * 4)
                discount = [0, 5, 10, 15, 20, 25, 30][(category_index + product_index) % 7]
                Product.objects.update_or_create(
                    sku=sku,
                    defaults={
                        "name": product_name,
                        "category": category,
                        "brand": f"{category_name.split()[0]}Pro",
                        "description": f"Premium {product_name.lower()} from the {category_name} collection. Built for daily use with a modern store experience.",
                        "specifications": f"Brand: {category_name.split()[0]}Pro\nCategory: {category_name}\nWarranty: 12 months\nCondition: New",
                        "price": base_price,
                        "discount_percent": discount,
                        "stock": 8 + (product_index * 3) % 45,
                        "is_featured": product_index in (1, 2, 3),
                        "is_special_offer": discount >= 15,
                        "sold_count": (category_index * product_index * 7) % 140,
                        "viewed_count": (category_index * product_index * 11) % 240,
                        "image_url": product_image(product_name, category_name, 1),
                        "image_url_2": product_image(product_name, category_name, 2),
                        "image_url_3": product_image(product_name, category_name, 3),
                        "is_active": True,
                    },
                )
                created_products += 1

        User = get_user_model()
        admin_user, _ = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@example.com"},
        )
        admin_user.email = "admin@example.com"
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.set_password("Admin@12345")
        admin_user.save()

        self.stdout.write(self.style.SUCCESS(f"Store data ready: {len(CATEGORY_DATA)} categories and {created_products} products."))
        self.stdout.write(self.style.SUCCESS("Admin login: username=admin password=Admin@12345 email=admin@example.com"))
