# Generated by Django 3.0.8 on 2020-09-14 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jmxs', '0021_auto_20200911_1107'),
    ]

    operations = [
        migrations.AddField(
            model_name='jmxs',
            name='thread_base_info',
            field=models.TextField(default='', verbose_name='线程组基本信息'),
        ),
    ]
