# Generated by Django 4.1.6 on 2023-02-10 19:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="document",
            name="id",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
