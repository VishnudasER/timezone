# Generated by Django 5.0.1 on 2024-02-07 10:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_address_delete_chat_delete_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='address',
            old_name='zip',
            new_name='zipcode',
        ),
    ]
