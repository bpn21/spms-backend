# Generated by Django 3.2.16 on 2024-09-06 03:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0009_usertoken_refresh_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertoken',
            name='valid',
            field=models.BooleanField(default=True),
        ),
    ]
