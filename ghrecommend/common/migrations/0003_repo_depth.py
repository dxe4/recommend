# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_auto_20151121_2034'),
    ]

    operations = [
        migrations.AddField(
            model_name='repo',
            name='depth',
            field=models.IntegerField(default=0),
        ),
    ]
