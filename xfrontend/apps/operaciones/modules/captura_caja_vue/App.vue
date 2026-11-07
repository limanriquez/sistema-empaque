<script setup>
import { ref, onMounted } from 'vue'

import { DxTextBox } from 'devextreme-vue/text-box'
import { DxSelectBox } from 'devextreme-vue/select-box'
import { DxButton } from 'devextreme-vue/button'
import { DxLoadPanel } from 'devextreme-vue/load-panel'
import DxDataGrid, {
    DxColumn,
    DxSelection,
} from 'devextreme-vue/data-grid'
// ============================================
// PARÁMETROS DE LA OPERACIÓN
// ============================================

const operacionDiariaId = ref(null)
const loteEmpaqueId = ref(null)
const variedadId = ref(null)

// ============================================
// INFORMACIÓN DE LA CAJA
// ============================================

const txtCodigoCaptura = ref('')
const txtEstacion = ref('')
const txtEmpleado = ref('')
const txtClaveProducto = ref('')
const txtProductoEmpaque = ref('')
const txtPrecioCaja = ref(null)
const txtCalidad = ref('')
const txtTamano = ref('')
const txtVariedad = ref('')

// ============================================
// TARIMAS
// ============================================

const cmbTarima = ref(null)
const tarimas = ref([])
function seleccionarTarima(e) {
    cmbTarima.value = e.selectedRowKeys[0] ?? null
}
// ============================================
// INDICADOR DE PROCESAMIENTO
// ============================================

const loadPanelVisible = ref(false)

const loadPanelOptions = {
    shading: true,
    showIndicator: true,
    showPane: true,
    message: 'Procesando...',
}

// ============================================
// CONFIGURACIÓN DE CONTROLES
// ============================================

const tarimaOptions = {
    displayExpr: 'codigo_tarima',
    valueExpr: 'id',
    placeholder: 'Seleccionar tarima',
    noDataText: 'Sin tarimas disponibles',
    showClearButton: true,
    searchEnabled: true,
    disabled: true,
}

// ============================================
// FUNCIONES
// ============================================

function cambiarCodigoCaptura(e) {
    const codigo = (e.value || '')
        .replace(/\s/g, '')
        .toUpperCase()
        .substring(0, 8)

    txtCodigoCaptura.value = codigo

    if (e.value !== codigo) {
        e.component.option('value', codigo)
    }
}

function limpiarCampos() {
    txtCodigoCaptura.value = ''
    txtEstacion.value = ''
    txtEmpleado.value = ''
    txtClaveProducto.value = ''
    txtProductoEmpaque.value = ''
    txtPrecioCaja.value = null
    txtCalidad.value = ''
    txtTamano.value = ''
    txtVariedad.value = ''
    cmbTarima.value = null
}

function guardarCaja() {
    // Pendiente: implementar validaciones y guardado.
}

function inicializar() {
    const parametros = document.getElementById('app')

    if (!parametros) {
        return
    }

    operacionDiariaId.value =
        parametros.dataset.operacionDiariaId || null

    loteEmpaqueId.value =
        parametros.dataset.loteEmpaqueId || null

    variedadId.value =
        parametros.dataset.variedadId || null

    limpiarCampos()
}

// ============================================
// CICLO DE VIDA
// ============================================

onMounted(() => {
    inicializar()
})
</script>

<template>
    <div class="captura-caja">

        <!-- INDICADOR DE PROCESAMIENTO -->
        <DxLoadPanel
            v-model:visible="loadPanelVisible"
            :shading="loadPanelOptions.shading"
            :show-indicator="loadPanelOptions.showIndicator"
            :show-pane="loadPanelOptions.showPane"
            :message="loadPanelOptions.message"
        />

        <!-- ENCABEZADO -->
        <div class="captura-header">

            <div class="captura-header-icon">
                <i class="dx-icon-box"></i>
            </div>

            <div>
                <h2>Captura de Caja</h2>
                <p>Registro y asignación de cajas de empaque</p>
            </div>

        </div>

        <!-- ACCIONES -->
        <div class="captura-toolbar">

            <div class="acciones">

                <DxButton
                    text="Limpiar"
                    icon="clear"
                    type="default"
                    width="145"
                    @click="limpiarCampos"
                />

                <DxButton
                    text="Guardar caja"
                    icon="save"
                    type="success"
                    width="165"
                    @click="guardarCaja"
                />

            </div>

        </div>

        <!-- INFORMACIÓN DE LA CAJA -->
        <div class="captura-card">

            <div class="captura-card-header">
                <i class="dx-icon-info"></i>
                <span>Información de la caja</span>
            </div>

            <div class="captura-grid">

                <div class="campo-captura">
                    <label>Código de captura:</label>

                    <DxTextBox
                        :value="txtCodigoCaptura"
                        :read-only="false"
                        :show-clear-button="true"
                        :max-length="8"
                        placeholder="Ejemplo: 01S114"
                        value-change-event="input"
                        @value-changed="cambiarCodigoCaptura"
                    />
                </div>

                <div class="campo-captura">
                    <label>Estación de trabajo:</label>

                    <DxTextBox
                        v-model:value="txtEstacion"
                        :read-only="true"
                    />
                </div>

                <div class="campo-captura">
                    <label>Empleado:</label>

                    <DxTextBox
                        v-model:value="txtEmpleado"
                        :read-only="true"
                    />
                </div>

                <div class="campo-captura">
                    <label>Clave de producto:</label>

                    <DxTextBox
                        v-model:value="txtClaveProducto"
                        :read-only="true"
                    />
                </div>

                <div class="campo-captura">
                    <label>Producto de empaque:</label>

                    <DxTextBox
                        v-model:value="txtProductoEmpaque"
                        :read-only="true"
                    />
                </div>

                <div class="campo-captura">
                    <label>Precio de caja:</label>

                    <DxTextBox
                        v-model:value="txtPrecioCaja"
                        :read-only="true"
                        display-format="$ #,##0.00"
                    />
                </div>

                <div class="campo-captura">
                    <label>Calidad:</label>

                    <DxTextBox
                        v-model:value="txtCalidad"
                        :read-only="true"
                    />
                </div>

                <div class="campo-captura">
                    <label>Tamaño:</label>

                    <DxTextBox
                        v-model:value="txtTamano"
                        :read-only="true"
                    />
                </div>

                <div class="campo-captura">
                    <label>Variedad:</label>

                    <DxTextBox
                        v-model:value="txtVariedad"
                        :read-only="true"
                    />
                </div>

            </div>
        </div>

        <!-- SELECCIÓN DE TARIMA -->
        <div class="captura-card">

            <div class="captura-card-header">
                <i class="dx-icon-box"></i>
                <span>Selección de tarima</span>
            </div>

            <div class="tarima-contenido">

                <DxDataGrid
                    :data-source="tarimas"
                    key-expr="id"
                    :show-borders="true"
                    :show-row-lines="true"
                    :show-column-lines="true"
                    :hover-state-enabled="true"
                    :column-auto-width="true"
                    :selected-row-keys="cmbTarima !== null ? [cmbTarima] : []"
                    @selection-changed="seleccionarTarima"
                    no-data-text="Sin tarimas disponibles"
                >
                    <DxSelection
                        mode="single"
                    />

                    <DxColumn
                        data-field="codigo_tarima"
                        caption="Código de tarima"
                    />

                </DxDataGrid>

            </div>

        </div>

    </div>
</template>
