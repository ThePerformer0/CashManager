# Generated by Django 5.0.7 on 2024-09-02 01:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cashmanager', '0005_piecejustificative'),
    ]

    operations = [
        migrations.AlterField(
            model_name='piecejustificative',
            name='fichier',
            field=models.FileField(upload_to='pieces_justificatives/'),
        ),
    ]