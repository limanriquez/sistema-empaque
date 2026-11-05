from django.db import migrations, models
from django.db.models import Q, F


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0009_empleadospuestooperacion'),
        ('personas', '0007_empleado_usuario'),
    ]

    operations = [

        # Las restricciones anteriores ya fueron eliminadas
        # físicamente durante el primer intento de migración.
        # Aquí solamente actualizamos el estado interno de Django.

        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.RemoveConstraint(
                    model_name='operaciondiaria',
                    name='operacion_estado_horas_coherentes',
                ),
                migrations.RemoveConstraint(
                    model_name='operaciondiaria',
                    name='cierre_posterior_a_apertura',
                ),
            ],
        ),

        # El campo iniciada ya existe físicamente en MySQL.
        # Solamente actualizamos el estado de Django.
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AddField(
                    model_name='operaciondiaria',
                    name='iniciada',
                    field=models.BooleanField(
                        default=False,
                        editable=False,
                        verbose_name='Iniciada',
                    ),
                ),
            ],
        ),

        # Nueva restricción de coherencia de estados.
        migrations.AddConstraint(
            model_name='operaciondiaria',
            constraint=models.CheckConstraint(
                condition=(
                    Q(
                        abierta=False,
                        iniciada=False,
                        hora_apertura__isnull=True,
                        hora_cierre__isnull=True,
                    )
                    |
                    Q(
                        abierta=True,
                        iniciada=True,
                        hora_apertura__isnull=False,
                        hora_cierre__isnull=True,
                    )
                    |
                    Q(
                        abierta=False,
                        iniciada=True,
                        hora_apertura__isnull=False,
                        hora_cierre__isnull=False,
                    )
                ),
                name='operacion_estado_horas_coherentes',
            ),
        ),

        # Restricción de fecha de cierre.
        migrations.AddConstraint(
            model_name='operaciondiaria',
            constraint=models.CheckConstraint(
                condition=(
                    Q(hora_cierre__isnull=True)
                    |
                    Q(hora_cierre__gte=F('hora_apertura'))
                ),
                name='cierre_posterior_a_apertura',
            ),
        ),
    ]