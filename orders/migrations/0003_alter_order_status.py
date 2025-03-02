# Generated by Django 4.0.4 on 2025-02-05 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_alter_orderitem_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('P', 'pending'), ('C', 'completed'), ('X', 'cancelled')], default='P', max_length=1),
        ),
    ]
