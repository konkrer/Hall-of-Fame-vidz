# Generated by Django 2.1.7 on 2019-03-13 01:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('halls', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SuggestionVideo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('url', models.URLField()),
                ('youtube_id', models.CharField(max_length=255)),
                ('hall', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='halls.Hall')),
            ],
        ),
    ]
