# Generated by Django 3.0.8 on 2020-08-24 18:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0012_auto_20200824_1817'),
    ]

    operations = [
        migrations.CreateModel(
            name='FlowTaskAggregateReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=1000, verbose_name='Label')),
                ('samplers', models.CharField(max_length=1000, verbose_name='样本名称')),
                ('average_req', models.CharField(max_length=100, verbose_name='平均值')),
                ('median_req', models.CharField(max_length=100, verbose_name='中位数')),
                ('line90_req', models.CharField(max_length=100, verbose_name='90%百分位')),
                ('line95_req', models.CharField(max_length=100, verbose_name='95%百分位')),
                ('line99_req', models.CharField(max_length=100, verbose_name='99%百分位')),
                ('min_req', models.CharField(max_length=100, verbose_name='最小值')),
                ('max_req', models.CharField(max_length=100, verbose_name='最大值')),
                ('error_rate', models.CharField(max_length=100, verbose_name='异常比例')),
                ('tps', models.CharField(max_length=100, verbose_name='吞吐量')),
                ('recieved_per', models.CharField(max_length=100, verbose_name='每秒从服务器端接收到的数据量')),
                ('flow', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tasks.TaskFlow')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tasks.Tasks', verbose_name='任务id')),
            ],
            options={
                'verbose_name': 'jtl转换为csv聚合报告',
                'verbose_name_plural': 'jtl转换为csv聚合报告',
            },
        ),
    ]