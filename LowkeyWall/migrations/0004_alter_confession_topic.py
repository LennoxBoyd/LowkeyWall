# Generated by Django 5.2.3 on 2025-07-08 08:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LowkeyWall', '0003_contactmessage_supportplan'),
    ]

    operations = [
        migrations.AlterField(
            model_name='confession',
            name='topic',
            field=models.CharField(choices=[('Love', 'Love'), ('Career', 'Career'), ('Life', 'Life'), ('Family', 'Family'), ('School', 'School'), ('Other', 'Other'), ('Mental Health', 'Mental Health'), ('Friendship', 'Friendship'), ('Finance', 'Finance'), ('Addiction', 'Addiction'), ('Loneliness', 'Loneliness'), ('Relationships', 'Relationships'), ('Spirituality', 'Spirituality'), ('Success', 'Success'), ('Failure', 'Failure'), ('Secrets', 'Secrets')], max_length=100),
        ),
    ]
