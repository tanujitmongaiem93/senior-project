# Generated by Django 2.0.3 on 2018-04-01 23:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0010_auto_20180323_0025'),
    ]

    operations = [
        migrations.AddField(
            model_name='information',
            name='order',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
