
import { createApp, ref } from 'vue'
import { DxButton } from 'devextreme-vue/button'

import 'devextreme/dist/css/dx.light.css'
import './hola_mundo_vue.css'

import http from '@/services/http.js'

const App = {
    components: {
        DxButton,
    },

    setup() {
        const mensaje = ref('Vue 3 está funcionando.')
        const respuestaGet = ref('')
        const respuestaPost = ref('')
        const cargandoGet = ref(false)
        const cargandoPost = ref(false)

        async function consultarDjango() {
            cargandoGet.value = true
            respuestaGet.value = ''

            try {
                const { data } = await http.get('/hola_mundo_api/')
                respuestaGet.value = data.mensaje
            } catch (error) {
                respuestaGet.value =
                    error.response?.data?.mensaje ||
                    'Error al consultar Django.'
            } finally {
                cargandoGet.value = false
            }
        }

        async function enviarPost() {
            cargandoPost.value = true
            respuestaPost.value = ''

            try {
                const { data } = await http.post(
                    '/hola_mundo_post_api/',
                    {
                        mensaje: 'Saludos desde Vue 3 mediante Axios.',
                    }
                )

                respuestaPost.value =
                    `${data.mensaje} Dato recibido: ${data.dato_recibido}`
            } catch (error) {
                respuestaPost.value =
                    error.response?.data?.mensaje ||
                    'Error al enviar información a Django.'

                console.error(error)
            } finally {
                cargandoPost.value = false
            }
        }

        return {
            mensaje,
            respuestaGet,
            respuestaPost,
            cargandoGet,
            cargandoPost,
            consultarDjango,
            enviarPost,
        }
    },

    template: `
        <main class="contenedor">
            <h1>Hola Mundo</h1>

            <p>{{ mensaje }}</p>

            <section>
                <h3>Prueba GET</h3>

                <dx-button
                    text="Consultar Django"
                    type="default"
                    :disabled="cargandoGet"
                    @click="consultarDjango"
                />

                <p v-if="respuestaGet">{{ respuestaGet }}</p>
            </section>

            <section>
                <h3>Prueba POST + CSRF</h3>

                <dx-button
                    text="Enviar información a Django"
                    type="success"
                    :disabled="cargandoPost"
                    @click="enviarPost"
                />

                <p v-if="respuestaPost">{{ respuestaPost }}</p>
            </section>
        </main>
    `,
}

createApp(App).mount('#app')
