# Generated by Django 4.2b1 on 2023-03-21 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("snippetstests", "0008_filterablesnippet"),
    ]

    operations = [
        migrations.AddField(
            model_name="filterablesnippet",
            name="some_date",
            field=models.DateField(auto_now=True),
        ),
    ]