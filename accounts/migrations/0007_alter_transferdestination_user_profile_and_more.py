# Generated by Django 4.2.7 on 2024-01-01 14:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        ('accounts', '0006_alter_account_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transferdestination',
            name='user_profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.userprofile'),
        ),
        migrations.DeleteModel(
            name='UserProfile',
        ),
    ]
