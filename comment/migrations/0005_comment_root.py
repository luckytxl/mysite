# Generated by Django 2.0 on 2021-10-28 08:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('comment', '0004_auto_20211028_1617'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='root',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='root_comment', to='comment.Comment'),
        ),
    ]
