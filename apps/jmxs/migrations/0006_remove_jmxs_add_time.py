# Generated by Django 3.0.8 on 2020-08-01 18:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jmxs', '0005_auto_20200801_1813'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jmxs',
            name='add_time',
        ),
    ]
