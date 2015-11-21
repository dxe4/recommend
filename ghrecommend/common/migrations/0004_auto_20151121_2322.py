# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0003_repo_depth'),
    ]

    operations = [
        migrations.CreateModel(
            name='StargazerRepo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=50)),
                ('stargazers_count', models.IntegerField()),
                ('full_name', models.CharField(max_length=100)),
                ('origin', models.ForeignKey(to='common.Repo')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='stargazerrepo',
            unique_together=set([('origin', 'username', 'full_name')]),
        ),
    ]
