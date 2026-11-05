from django import forms
from django.db.models import Q
from inventarios.models import Material
from .models import ComponenteEmpaque, ProductoEmpaque, OperacionDiaria, LoteEmpaque
from django.core.exceptions import ValidationError

from django.apps import apps
from django.db.models import Sum, Count, Min


# Formulario para registrar y modificar productos de empaque.
# Limpia espacios, normaliza el código a mayúsculas y evita duplicados
# sin distinguir mayúsculas.
# Permite seleccionar el tamaño desde su catálogo.
# El costo y el precio no pueden ser negativos. Que el precio sea
# mayor al costo lo exige el modelo.
class ProductoEmpaqueForm(forms.ModelForm):

    class Meta:
        model = ProductoEmpaque
        fields = (
            "codigo",
            "nombre",
            "descripcion",
            "tamano",
            "costo_empaque",
            "precio_cobro",
            "activo",
        )

    def clean_codigo(self):
        # El código es opcional; vacío se guarda como NULL para que
        # varios productos sin código no choquen con el unique.
        codigo = (self.cleaned_data.get("codigo") or "").strip().upper()

        if not codigo:
            return None

        duplicados = ProductoEmpaque.objects.filter(codigo__iexact=codigo)

        if self.instance.pk:
            duplicados = duplicados.exclude(pk=self.instance.pk)

        if duplicados.exists():
            raise forms.ValidationError(
                "Ya existe un producto de empaque con este código."
            )

        return codigo

    def clean_nombre(self):
        nombre = " ".join(self.cleaned_data["nombre"].split())

        duplicados = ProductoEmpaque.objects.filter(nombre__iexact=nombre)

        if self.instance.pk:
            duplicados = duplicados.exclude(pk=self.instance.pk)

        if duplicados.exists():
            raise forms.ValidationError(
                "Ya existe un producto de empaque con este nombre."
            )

        return nombre

    def clean_costo_empaque(self):
        costo = self.cleaned_data["costo_empaque"]

        if costo < 0:
            raise forms.ValidationError("El costo no puede ser negativo.")

        return costo

    def clean_precio_cobro(self):
        precio = self.cleaned_data["precio_cobro"]

        if precio < 0:
            raise forms.ValidationError("El precio no puede ser negativo.")

        return precio

# Formulario de cada material del BOM, usado en la tabla dentro del
# producto. Solo ofrece materiales activos; al editar conserva el que
# ya tenía la fila aunque se haya desactivado después. Las cantidades
# enteras según la unidad las valida ComponenteEmpaque.clean.
class ComponenteEmpaqueForm(forms.ModelForm):

    class Meta:
        model = ComponenteEmpaque
        fields = ("material", "cantidad_material")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        filtro = Q(activo=True)

        if self.instance.material_id:
            filtro |= Q(pk=self.instance.material_id)

        self.fields["material"].queryset = Material.objects.filter(
            filtro
        ).select_related("unidad_medida")

    def clean_cantidad_material(self):
        cantidad = self.cleaned_data["cantidad_material"]

        if cantidad <= 0:
            raise forms.ValidationError(
                "La cantidad debe ser mayor a cero."
            )

        return cantidad


# Conjunto de materiales del BOM dentro del producto. Exige al menos
# un material, también al borrar filas de un producto ya existente.
class ComponenteEmpaqueFormSet(forms.BaseInlineFormSet):

    def clean(self):
        super().clean()

        # Si hay errores en las filas, se muestran primero esos.
        if any(self.errors):
            return

        con_material = [
            form
            for form in self.forms
            if form.cleaned_data
            and not form.cleaned_data.get("DELETE", False)
            and form.cleaned_data.get("material")
        ]

        if not con_material:
            raise forms.ValidationError(
                "El producto debe tener al menos un material en su BOM."
            )



from django import forms
from django.core.exceptions import ValidationError

from .models import OperacionDiaria


# ==========================================================
# FORMULARIO: OPERACIÓN DIARIA
#
# Permite capturar las observaciones generales de la jornada.
# La creación inicia automáticamente la operación y la
# edición de una operación abierta permite cerrarla.
# ==========================================================

class OperacionDiariaForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = OperacionDiaria
        fields = [
            "observaciones",
        ]

        widgets = {
            "observaciones": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Observaciones de la operación",
            }),
        }

    def clean(self):

        cleaned_data = super().clean()

        # Validar que el usuario tenga un empleado activo asociado.
        if self.request and self.request.user.is_authenticated:

            empleado = getattr(
                self.request.user,
                "perfil_empleado",
                None,
            )

            if empleado is None:
                raise ValidationError(
                    "Tu usuario no tiene un empleado asociado. "
                    "Solicita al administrador que lo vincule."
                )

            if not empleado.activo:
                raise ValidationError(
                    "Tu empleado está inactivo. "
                    "No puedes abrir ni cerrar operaciones."
                )

        # Validar creación.
        if self.instance._state.adding:

            if OperacionDiaria.objects.filter(abierta=True).exists():
                raise ValidationError(
                    "Ya existe una operación abierta. "
                    "Debes cerrarla antes de crear otra."
                )

        # Validar modificación.
        else:

            operacion = OperacionDiaria.objects.filter(
                pk=self.instance.pk
            ).first()

            if operacion is None:
                raise ValidationError(
                    "La operación ya no existe."
                )

            if not operacion.abierta:
                raise ValidationError(
                    "Esta operación ya está cerrada. "
                    "Debes crear una nueva."
                )

        return cleaned_data



# ==========================================================
# FORMULARIO: LOTE DE EMPAQUE
#
# Permite registrar una corrida de producción utilizando
# lotes agrícolas que tengan fruta disponible en bodega.
#
# Las existencias se consultan desde ExistenciaFruta.
# Únicamente se muestran lotes con cajones disponibles
# pertenecientes a un solo cliente.
#
# LoteEmpaque conserva exclusivamente su relación directa
# con LoteHuerta.
#
# El selector muestra:
# - Cliente propietario.
# - Lote agrícola.
# - Huerta.
# - Total de cajones disponibles.
#
# La variedad se limita a las existencias del lote
# agrícola seleccionado y de su propietario.
# ==========================================================

class LoteEmpaqueForm(forms.ModelForm):

    class Meta:
        model = LoteEmpaque

        fields = [
            "lote_huerta",
            "variedad",
            "observaciones",
        ]

        widgets = {
            "lote_huerta": forms.Select(),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        ExistenciaFruta = apps.get_model(
            "inventarioFruta",
            "ExistenciaFruta",
        )

        LoteHuerta = apps.get_model(
            "fruticultura",
            "LoteHuerta",
        )

        Cliente = apps.get_model(
            "personas",
            "Cliente",
        )

        Variedad = apps.get_model(
            "fruticultura",
            "Variedad",
        )

        # --------------------------------------------------
        # 1. CONSULTAR EXISTENCIAS AGRUPADAS POR LOTE
        # --------------------------------------------------

        resumen = (
            ExistenciaFruta.objects
            .filter(cantidad_cajones__gt=0)
            .values("lote_huerta_id")
            .annotate(
                total_cajones=Sum("cantidad_cajones"),
                total_clientes=Count(
                    "cliente_id",
                    distinct=True,
                ),
                cliente_id_unico=Min("cliente_id"),
            )
            .filter(total_clientes=1)
        )

        resumen_por_lote = {
            registro["lote_huerta_id"]: registro
            for registro in resumen
        }

        lote_ids = list(resumen_por_lote.keys())

        # --------------------------------------------------
        # 2. CONSULTAR LOTES AGRÍCOLAS DISPONIBLES
        # --------------------------------------------------

        lotes = (
            LoteHuerta.objects
            .filter(
                pk__in=lote_ids,
                activo=True,
            )
            .select_related("huerta")
        )

        # --------------------------------------------------
        # 3. CONSULTAR CLIENTES PROPIETARIOS
        # --------------------------------------------------

        cliente_ids = [
            registro["cliente_id_unico"]
            for registro in resumen_por_lote.values()
        ]

        clientes = {
            cliente.pk: cliente
            for cliente in Cliente.objects.filter(
                pk__in=cliente_ids
            ).select_related("persona")
        }

        # --------------------------------------------------
        # 4. CONSTRUIR OPCIONES DEL SELECTOR
        # --------------------------------------------------

        opciones = [
            ("", "---------"),
        ]

        for lote in lotes:

            datos = resumen_por_lote[lote.pk]

            cliente = clientes.get(
                datos["cliente_id_unico"]
            )

            if not cliente:
                continue

            etiqueta = (
                f"{cliente} | "
                f"{lote.nombre} | "
                f"{lote.huerta} | "
                f"{datos['total_cajones']:,} cajones disponibles"
            )

            opciones.append(
                (str(lote.pk), etiqueta)
            )

        # El queryset conserva la validación de ModelChoiceField.
        self.fields["lote_huerta"].queryset = (
            lotes.filter(
                pk__in=[
                    int(valor)
                    for valor, etiqueta in opciones
                    if valor
                ]
            )
        )

        # El widget muestra las etiquetas construidas arriba.
        self.fields["lote_huerta"].choices = opciones

        # --------------------------------------------------
        # 5. DETERMINAR EL LOTE SELECCIONADO
        # --------------------------------------------------

        lote_id = None

        if self.is_bound:

            lote_id = self.data.get(
                self.add_prefix("lote_huerta")
            )

        elif self.instance.pk:

            lote_id = self.instance.lote_huerta_id

        try:
            lote_id = int(lote_id) if lote_id else None

        except (TypeError, ValueError):
            lote_id = None

        # --------------------------------------------------
        # 6. INICIALIZAR VARIEDADES
        # --------------------------------------------------

        variedades = Variedad.objects.none()

        # --------------------------------------------------
        # 7. FILTRAR VARIEDADES DEL LOTE SELECCIONADO
        # --------------------------------------------------

        if lote_id:

            datos = resumen_por_lote.get(lote_id)

            if datos:

                variedades_ids = (
                    ExistenciaFruta.objects
                    .filter(
                        lote_huerta_id=lote_id,
                        cliente_id=datos["cliente_id_unico"],
                        cantidad_cajones__gt=0,
                    )
                    .values_list(
                        "variedad_id",
                        flat=True,
                    )
                    .distinct()
                )

                variedades = Variedad.objects.filter(
                    pk__in=variedades_ids,
                    activo=True,
                )

        self.fields["variedad"].queryset = variedades

    # ======================================================
    # VALIDACIÓN FINAL
    # ======================================================

    def clean(self):

        cleaned_data = super().clean()

        lote = cleaned_data.get("lote_huerta")
        variedad = cleaned_data.get("variedad")

        if not lote:
            return cleaned_data

        ExistenciaFruta = apps.get_model(
            "inventarioFruta",
            "ExistenciaFruta",
        )

        # --------------------------------------------------
        # 1. VERIFICAR EXISTENCIAS ACTUALES
        # --------------------------------------------------

        resumen = list(
            ExistenciaFruta.objects
            .filter(
                lote_huerta_id=lote.pk,
                cantidad_cajones__gt=0,
            )
            .values("cliente_id")
            .annotate(
                total_cajones=Sum("cantidad_cajones"),
            )
        )

        if not resumen:

            self.add_error(
                "lote_huerta",
                "El lote agrícola ya no tiene fruta disponible.",
            )

            return cleaned_data

        # --------------------------------------------------
        # 2. VALIDAR PROPIETARIO ÚNICO
        # --------------------------------------------------

        if len(resumen) > 1:

            self.add_error(
                "lote_huerta",
                "El lote agrícola tiene existencias de varios "
                "clientes. No es posible determinar un propietario único.",
            )

            return cleaned_data

        # --------------------------------------------------
        # 3. VALIDAR VARIEDAD DISPONIBLE
        # --------------------------------------------------

        if variedad:

            existe_variedad = (
                ExistenciaFruta.objects
                .filter(
                    lote_huerta_id=lote.pk,
                    cliente_id=resumen[0]["cliente_id"],
                    variedad_id=variedad.pk,
                    cantidad_cajones__gt=0,
                )
                .exists()
            )

            if not existe_variedad:

                self.add_error(
                    "variedad",
                    "La variedad seleccionada ya no tiene "
                    "existencias disponibles para este lote.",
                )

        return cleaned_data