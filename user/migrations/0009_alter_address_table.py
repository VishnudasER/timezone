# Generated by Django 5.0 on 2024-02-08 04:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_remove_address_email'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='address',
            table='address',
        ),
    ]