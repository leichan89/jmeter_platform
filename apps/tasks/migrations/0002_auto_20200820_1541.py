# Generated by Django 3.0.8 on 2020-08-20 15:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jmxs', '0010_auto_20200813_1420'),
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tasksdetails',
            name='jmx',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jmxs.Jmxs'),
        ),
    ]
