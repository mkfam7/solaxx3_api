# Generated by Django 4.2.6 on 2023-12-03 14:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("solax_registers", "0002_alter_minutestatsrecord_inverter_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="lastminutestatsrecord",
            name="inverter_status",
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]