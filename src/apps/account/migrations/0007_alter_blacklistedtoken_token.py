# Generated by Django 3.2.16 on 2024-08-14 01:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0006_alter_usertoken_device_info'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blacklistedtoken',
            name='token',
            field=models.CharField(max_length=255),
        ),
    ]
