# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0004_auto_20151121_2322'),
    ]

    operations = [
        migrations.CreateModel(
            name='StargazerProfiles',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=50)),
                ('origin', models.ForeignKey(to='common.Repo')),
            ],
        ),
    ]
