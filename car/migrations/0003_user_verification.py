# Generated by Django 5.0.7 on 2024-10-01 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('car', '0002_alter_order_total_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='User_Verification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('verficationcode', models.CharField(max_length=6)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
