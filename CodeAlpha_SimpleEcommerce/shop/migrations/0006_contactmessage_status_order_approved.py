from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0005_category_icon_order_country_product_image_url_2_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="contactmessage",
            name="status",
            field=models.CharField(
                choices=[
                    ("new", "New"),
                    ("read", "Read"),
                    ("replied", "Replied"),
                    ("closed", "Closed"),
                ],
                default="new",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("approved", "Approved"),
                    ("processing", "Processing"),
                    ("shipped", "Shipped"),
                    ("delivered", "Delivered"),
                    ("cancelled", "Cancelled"),
                ],
                default="pending",
                max_length=20,
            ),
        ),
    ]
