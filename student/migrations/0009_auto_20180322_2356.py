# Generated by Django 2.0.3 on 2018-03-22 23:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0008_auto_20180322_2336'),
    ]

    operations = [
        migrations.AlterField(
            model_name='information',
            name='faculty',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='student.Faculty'),
        ),
        migrations.AlterField(
            model_name='information',
            name='major',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='student.Major'),
        ),
    ]