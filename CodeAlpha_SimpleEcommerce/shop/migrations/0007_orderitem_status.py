from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0006_contactmessage_status_order_approved"),
    ]

    operations = [
        migrations.AddField(
            model_name="orderitem",
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
