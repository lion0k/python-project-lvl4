# Generated by Django 3.2 on 2021-04-27 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0004_alter_tasks_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tasks',
            name='name',
            field=models.CharField(error_messages={'blank': 'ThisFieldCannotBeBlank', 'unique': 'TaskWithThisNameAlreadyExist'}, help_text='HelpTaskFieldText', max_length=150, unique=True, verbose_name='TasksName'),
        ),
    ]