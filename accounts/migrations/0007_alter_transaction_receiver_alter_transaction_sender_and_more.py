# Generated by Django 4.2.7 on 2023-12-31 05:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account_create_and_delete', '0001_initial'),
        ('accounts', '0006_alter_account_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='receiver',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_transactions', to='account_create_and_delete.account'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_transactions', to='account_create_and_delete.account'),
        ),
        migrations.DeleteModel(
            name='Account',
        ),
    ]
