# Generated by Django 3.0.8 on 2020-08-28 18:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UersParams',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('env', models.CharField(max_length=10, verbose_name='环境信息')),
                ('param_name', models.CharField(max_length=100, verbose_name='变量名称')),
                ('param_value', models.CharField(default='', max_length=1000, verbose_name='变量值')),
                ('add_time', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '用户添加的变量',
            },
        ),
    ]
