# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repo',
            name='description',
            field=models.CharField(max_length=500, null=True, blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='repo',
            unique_together=set([('full_name', 'username')]),
        ),
    ]
