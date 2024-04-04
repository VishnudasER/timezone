# Generated by Django 5.0 on 2024-04-04 03:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0014_alter_order_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='discount_price',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True),
        ),
    ]