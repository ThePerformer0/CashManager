# Generated by Django 4.2.7 on 2024-07-13 02:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cashmanager', '0002_alter_approvisionnement_numero_alter_retrait_numero'),
    ]

    operations = [
        migrations.AlterField(
            model_name='approvisionnement',
            name='montant',
            field=models.DecimalField(decimal_places=2, max_digits=30),
        ),
        migrations.AlterField(
            model_name='retrait',
            name='montant',
            field=models.DecimalField(decimal_places=2, max_digits=30),
        ),
    ]
