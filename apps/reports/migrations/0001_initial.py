# Generated by Django 3.0.8 on 2020-08-19 11:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('jtls_summary', '0001_initial'),
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reports',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report_url', models.CharField(max_length=100, verbose_name='报告地址')),
                ('add_time', models.DateTimeField(auto_now_add=True)),
                ('jtl_summary', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jtls_summary.JtlsSummary', verbose_name='汇总的jtlid')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tasks.Tasks', verbose_name='关联的任务id')),
            ],
            options={
                'verbose_name': '报告表',
                'verbose_name_plural': '报告表',
            },
        ),
    ]
