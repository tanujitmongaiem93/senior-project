# Generated by Django 2.0.2 on 2018-02-21 15:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0003_auto_20180216_0641'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendance',
            name='information',
        ),
        migrations.AddField(
            model_name='information',
            name='attendance',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='student.Attendance'),
        ),
    ]
