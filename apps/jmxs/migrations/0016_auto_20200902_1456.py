# Generated by Django 3.0.8 on 2020-09-02 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jmxs', '0015_auto_20200902_1456'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jmxs',
            name='jmx_alias',
            field=models.CharField(max_length=200, verbose_name='jmx中文别名'),
        ),
    ]
