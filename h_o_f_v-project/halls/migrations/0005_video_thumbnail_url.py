# Generated by Django 2.1.7 on 2019-03-14 04:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('halls', '0004_hall_votes_total'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='thumbnail_url',
            field=models.URLField(default='http://www.bullshit.com'),
            preserve_default=False,
        ),
    ]
