# Generated by Django 2.1.7 on 2019-03-13 22:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('halls', '0003_hall_votes'),
    ]

    operations = [
        migrations.AddField(
            model_name='hall',
            name='votes_total',
            field=models.IntegerField(default=1),
        ),
    ]
