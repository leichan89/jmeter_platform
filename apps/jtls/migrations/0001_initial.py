# Generated by Django 3.0.8 on 2020-08-20 18:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tasks', '0004_auto_20200820_1744'),
    ]

    operations = [
        migrations.CreateModel(
            name='JtlsSummary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jtl_url', models.CharField(max_length=100, verbose_name='生成的汇总的jtl地址')),
                ('add_time', models.DateTimeField(auto_now_add=True)),
                ('flow', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tasks.TaskFlow')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tasks.Tasks', verbose_name='关联的任务id')),
            ],
            options={
                'verbose_name': 'jtl汇总表',
                'verbose_name_plural': 'jtl汇总表',
            },
        ),
    ]
