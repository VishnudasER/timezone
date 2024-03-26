# Generated by Django 5.0.1 on 2024-03-02 17:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_side', '0004_applied_coupon'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryOffer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('percent_offer', models.DecimalField(decimal_places=2, max_digits=5)),
                ('start_date', models.DateField(null=True)),
                ('end_date', models.DateField(null=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin_side.category')),
            ],
        ),
        migrations.CreateModel(
            name='ProductOffer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('percent_offer', models.DecimalField(decimal_places=2, max_digits=5)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin_side.product')),
            ],
        ),
    ]
