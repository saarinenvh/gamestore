# Generated by Django 2.0.1 on 2018-02-14 16:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('storeapp', '0006_auto_20180203_1857'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='maker',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]