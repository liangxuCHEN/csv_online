# Generated by Django 2.0.3 on 2018-03-17 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mywork', '0002_auto_20180317_0951'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authtablemodel',
            name='auth_detail',
            field=models.CharField(max_length=256, null=True),
        ),
    ]
