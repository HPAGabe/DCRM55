# Generated by Django 5.0.6 on 2024-06-30 05:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0007_remove_customerrecord_customer_paid_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerrecord',
            name='email',
            field=models.EmailField(max_length=100),
        ),
    ]
