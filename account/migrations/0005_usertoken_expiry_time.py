# Generated by Django 3.2.16 on 2024-08-06 03:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_alter_usertoken_device_info'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertoken',
            name='expiry_time',
            field=models.DateTimeField(blank=True, null=True, unique=True),
        ),
    ]