# Generated by Django 2.2 on 2021-12-16 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='wholesaler',
            field=models.BooleanField(default=False, verbose_name='Статус оптовика'),
        ),
    ]
