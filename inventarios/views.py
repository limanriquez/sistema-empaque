from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from inventarios.serializer import *
from rest_framework import viewsets
from django.http import JsonResponse,HttpResponse
from django.template.loader import render_to_string

class CatalogoElementoInventarioViewSet(viewsets.ModelViewSet):
    queryset = CatalogoElementoInventario.objects.all()
    serializer_class = CatalogoElementoInventarioSerializer

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class DepartamentoViewSet(viewsets.ModelViewSet):
    queryset = Departamento.objects.all()
    serializer_class = DepartamentoSerializer

class ElementoInventarioViewSet(viewsets.ModelViewSet):
    queryset = ElementoInventario.objects.all()
    serializer_class = ElementoInventarioSerializer

class InventarioViewSet(viewsets.ModelViewSet):
    queryset = Inventario.objects.all()
    serializer_class = InventarioSerializer


@login_required()
def inventario(request):
	return render(request, 'inventarios/inventario.html',{
			'title':"Inventario"})

@login_required()
def inventarioVue(request):
	return render(request, 'inventarios/inventario-vue.html',{
			'title':"Inventario VUE"})

@login_required()
def inventarioExistente(request):
	inventario_json = []
	inventarios = Inventario.objects.all().select_related('Categoria','Departamento').prefetch_related('elementosInventario')
	for inventario in inventarios:
		tmp = {
			'Id': inventario.Id,
            'NoInventario': inventario.NoInventario,
            'Descripcion': inventario.Descripcion,	
			'Observaciones': inventario.Observaciones,
            'Ubicacion': inventario.Ubicacion,
            'FechaAdquisicion':inventario.FechaAdquisicion,
            'PrecioAdquisicion':inventario.Precio,
            'IdCategoria':inventario.Categoria.Id,
            'IdDepartamento':inventario.Departamento.Id,
            'Categoria':inventario.Categoria.Descripcion,
            'Departamento':inventario.Departamento.Descripcion,
            'URL':inventario.URL
		}
		inventario_json.append(tmp)
	return JsonResponse(inventario_json, safe = False)
    
@login_required()
def elementosInventario(request,IdInventario):
	elementosInventario_json = []
	inventario = Inventario.objects.get(pk = IdInventario)
	elementosInventario = inventario.elementosInventario.all().select_related('Categoria')

	for elementoInventario in elementosInventario:
		tmp = {
			'Id': elementoInventario.Id,
            'Caracteristica': elementoInventario.Categoria.Descripcion,	
			'Descripcion': elementoInventario.Descripcion,	
		}
		elementosInventario_json.append(tmp)
	return JsonResponse(elementosInventario_json, safe = False)

from weasyprint import HTML
from weasyprint.fonts import FontConfiguration

def export_pdf(request,IdInventario):
    inventario = Inventario.objects.select_related('Categoria','Departamento').prefetch_related('elementosInventario').get(pk=IdInventario)
    arreglo = []
    elementosInventario = inventario.elementosInventario.all().select_related('Categoria')
    for elementoInventario in elementosInventario:
        arreglo.append(elementoInventario)
    
    precio = 0
    if inventario.Precio is not None:
        precio = inventario.Precio
    fechaAdquisicion = ""
    if inventario.FechaAdquisicion is not None:
        fechaAdquisicion = inventario.FechaAdquisicion

    context = {
			'Id': inventario.Id,
            'NoInventario': inventario.NoInventario,
            'Descripcion': inventario.Descripcion,	
			'Observaciones': inventario.Observaciones,
            'Ubicacion': inventario.Ubicacion,
            'FechaAdquisicion':inventario.FechaAdquisicion,
            'PrecioAdquisicion':precio,
            'IdCategoria':inventario.Categoria.Id,
            'IdDepartamento':inventario.Departamento.Id,
            'Categoria':inventario.Categoria.Descripcion,
            'Departamento':inventario.Departamento.Descripcion,
            'URL':inventario.URL,
            'lista':arreglo
		}
    html = render_to_string("inventario/reporte.html", context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "inline; report.pdf"

    font_config = FontConfiguration()
    HTML(string=html).write_pdf(response, font_config=font_config)

    return response