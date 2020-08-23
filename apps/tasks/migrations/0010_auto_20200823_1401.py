# Generated by Django 3.0.8 on 2020-08-23 14:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tasks', '0009_auto_20200821_1551'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tasks',
            name='add_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, verbose_name='用户名'),
        ),
    ]
