import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogos', '0011_alter_conceptonomina_tipo'),
        ('personas', '0008_empleado_tipo_remuneracion'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.RemoveField(
                    model_name='empleadoextra',
                    name='concepto_extra',
                ),
                migrations.AddField(
                    model_name='empleadoextra',
                    name='concepto',
                    field=models.ForeignKey(
                        to='catalogos.conceptonomina',
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='asignaciones_empleados',
                        verbose_name='Concepto de nómina',
                        null=True,
                        blank=True,
                    ),
                ),
            ],
        ),
    ]