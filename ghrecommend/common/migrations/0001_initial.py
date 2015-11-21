# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Repo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stargazers_url', models.CharField(max_length=500)),
                ('stargazers_count', models.IntegerField()),
                ('full_name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=500)),
                ('username', models.CharField(max_length=50)),
            ],
        ),
    ]
