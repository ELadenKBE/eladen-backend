# Generated by Django 4.2 on 2023-06-07 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0002_alter_good_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='good',
            name='manufacturer',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
