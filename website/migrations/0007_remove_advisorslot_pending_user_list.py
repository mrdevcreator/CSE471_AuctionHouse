# Generated by Django 5.0.2 on 2024-03-17 16:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0006_advisorslot_total_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='advisorslot',
            name='pending_user_list',
        ),
    ]
