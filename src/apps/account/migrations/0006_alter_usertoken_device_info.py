# Generated by Django 3.2.16 on 2024-08-11 02:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_usertoken_expiry_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usertoken',
            name='device_info',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]