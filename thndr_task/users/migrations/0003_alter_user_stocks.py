# Generated by Django 4.1 on 2022-08-25 00:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_stocks'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='stocks',
            field=models.JSONField(default=dict),
        ),
    ]