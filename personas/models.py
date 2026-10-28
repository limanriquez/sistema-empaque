from django.db import models

from django.db import models


class Persona(models.Model):

    id = models.BigAutoField(primary_key=True)

    class TipoPersona(models.IntegerChoices):
        FISICA = 1, "Persona física"
        MORAL = 2, "Persona moral"

    tipo_persona = models.PositiveSmallIntegerField(
        choices=TipoPersona.choices,
        default=TipoPersona.FISICA,
        verbose_name="Tipo de persona",
    )

    # Identificadores fiscales y personales
    curp = models.CharField(
        max_length=18,
        unique=True,
        null=True,
        blank=True,
        verbose_name="CURP",
    )

    rfc = models.CharField(
        max_length=13,
        unique=True,
        null=True,
        blank=True,
        verbose_name="RFC",
    )

    # Datos de persona física
    nombres = models.CharField(
        max_length=150,
        blank=True,
        default="",
        verbose_name="Nombre(s)",
    )

    apellido_paterno = models.CharField(
        max_length=60,
        blank=True,
        default="",
        verbose_name="Apellido paterno",
    )

    apellido_materno = models.CharField(
        max_length=60,
        blank=True,
        default="",
        verbose_name="Apellido materno",
    )

    # Datos de persona moral
    razon_social = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Razón social",
    )

    nombre_comercial = models.CharField(
        max_length=150,
        blank=True,
        default="",
        verbose_name="Nombre comercial",
    )

    # Control del registro maestro
    activo = models.BooleanField(
        default=True,
        verbose_name="Registro activo",
        help_text=(
            "Indica si el registro maestro está habilitado "
            "para utilizarse en el sistema. No representa la "
            "baja de un cliente, proveedor o empleado."
        ),
    )

    creado_en = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación",
    )

    class Meta:
        db_table = "personas_persona"
        verbose_name = "Persona"
        verbose_name_plural = "Personas"
        ordering = [
            "id",
        ]

    def __str__(self):
        if self.tipo_persona == self.TipoPersona.FISICA:
            nombre = " ".join(
                filter(
                    None,
                    [
                        self.nombres.strip(),
                        self.apellido_paterno.strip(),
                        self.apellido_materno.strip(),
                    ],
                )
            )
            return nombre or f"Persona física #{self.pk}"

        return (
            self.nombre_comercial.strip()
            or self.razon_social.strip()
            or f"Persona moral #{self.pk}"
        )


class Direccion(models.Model):

    id = models.BigAutoField(primary_key=True)

    class TipoDireccion(models.IntegerChoices):
        PARTICULAR = 1, "Particular"
        FISCAL = 2, "Fiscal"
        TRABAJO = 3, "Trabajo"
        ENTREGA = 4, "Entrega"
        OTRA = 5, "Otra"

    persona = models.ForeignKey(
        "personas.Persona",
        on_delete=models.PROTECT,
        related_name="direcciones",
    )

    tipo_direccion = models.PositiveSmallIntegerField(
        choices=TipoDireccion.choices,
        default=TipoDireccion.PARTICULAR,
    )

    calle = models.CharField(max_length=150, blank=True, default="")
    numero_exterior = models.CharField(max_length=20, blank=True, default="")
    numero_interior = models.CharField(max_length=20, blank=True, default="")
    colonia = models.CharField(max_length=100, blank=True, default="")
    codigo_postal = models.CharField(max_length=10, blank=True, default="")
    localidad = models.CharField(max_length=100, blank=True, default="")
    municipio = models.CharField(max_length=100, blank=True, default="")
    estado = models.CharField(max_length=100, blank=True, default="")
    pais = models.CharField(max_length=60, default="México")
    referencias = models.TextField(blank=True, default="")

    es_principal = models.BooleanField(default=False)
    activa = models.BooleanField(default=True)

    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "personas_direccion"

    def __str__(self):
        return ", ".join(filter(None, [
            self.calle,
            self.numero_exterior,
            self.colonia,
            self.municipio,
        ])) or f"Dirección {self.id}"



class Telefono(models.Model):

    id = models.BigAutoField(primary_key=True)

    class TipoTelefono(models.IntegerChoices):
        MOVIL = 1, "Móvil"
        OFICINA = 2, "Oficina"
        OTRO = 3, "Otro"

    persona = models.ForeignKey(
        "personas.Persona",
        on_delete=models.PROTECT,
        related_name="telefonos",
    )

    tipo_telefono = models.PositiveSmallIntegerField(
        choices=TipoTelefono.choices,
        default=TipoTelefono.MOVIL,
    )

    numero = models.CharField(max_length=25)

    activo = models.BooleanField(default=True)

    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "personas_telefono"

    def __str__(self):
        return self.numero


# Registra la información laboral de una persona física.
# Relaciona a la persona con su puesto, NSS, sueldo diario,
# fecha de ingreso y estado laboral, sin duplicar sus datos personales.
class Empleado(models.Model):

    persona = models.OneToOneField(
        "personas.Persona",
        on_delete=models.PROTECT,
        related_name="empleado",
        verbose_name="Persona",
    )

    nss = models.CharField(
        max_length=11,
        blank=True,
        default="",
        verbose_name="Número de Seguridad Social",
        help_text="Opcional. Captura los 11 dígitos del NSS del IMSS.",
    )

    puesto = models.ForeignKey(
        "catalogos.Puesto",
        on_delete=models.PROTECT,
        related_name="empleados",
        verbose_name="Puesto",
    )

    sueldo_diario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Sueldo diario",
    )

    fecha_ingreso = models.DateField(
        verbose_name="Fecha de ingreso",
    )

    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
    )

    class Meta:
        db_table = "personas_empleado"
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"
        ordering = ["persona__id"]

    def __str__(self):
        return f"Empleado {self.pk} - {self.persona}"


# Relaciona a un empleado con los conceptos extras que tiene asignados.
# Cada asignación conserva su propio monto y puede eliminarse sin
# eliminar al empleado ni al concepto del catálogo.
class EmpleadoExtra(models.Model):

    empleado = models.ForeignKey(
        "personas.Empleado",
        on_delete=models.CASCADE,
        related_name="extras",
        verbose_name="Empleado",
    )

    concepto_extra = models.ForeignKey(
        "catalogos.ConceptoExtra",
        on_delete=models.PROTECT,
        related_name="asignaciones_empleados",
        verbose_name="Concepto extra",
    )

    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Monto asignado",
    )

    class Meta:
        db_table = "personas_empleado_extra"
        verbose_name = "Extra del empleado"
        verbose_name_plural = "Extras del empleado"
        constraints = [
            models.UniqueConstraint(
                fields=["empleado", "concepto_extra"],
                name="uq_empleado_concepto_extra",
            ),
        ]

        # Representa el concepto extra asignado al empleado.
    def __str__(self):
        return f"{self.empleado} - {self.concepto_extra}"

