# Generated by Django 5.2.3 on 2025-07-18 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("LowkeyWall", "0009_alter_confession_feeling"),
    ]

    operations = [
        migrations.AddField(
            model_name="confession",
            name="session_owner",
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name="confession",
            name="message",
            field=models.TextField(max_length=2000),
        ),
    ]
