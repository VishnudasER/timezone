# Generated by Django 5.0 on 2024-04-02 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0014_like_post_delete_samplemodel_like_post'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
