# Generated by Django 3.0.8 on 2020-09-02 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jmxs', '0013_remove_jmxs_samplers_info'),
    ]

    operations = [
        migrations.AddField(
            model_name='jmxs',
            name='jmx_alias',
            field=models.CharField(default='', max_length=200, verbose_name='jmx中文别名'),
        ),
    ]