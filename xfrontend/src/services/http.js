
import axios from 'axios'

// Configuración central de comunicación con Django.
const http = axios.create({
    baseURL: '/',
    timeout: 30000,
    withCredentials: true,

    headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': 'application/json',
    },
})

// Obtiene el token CSRF de la cookie de Django.
function obtenerCSRF() {
    const prefijo = 'csrftoken='

    const cookie = document.cookie
        .split(';')
        .map(item => item.trim())
        .find(item => item.startsWith(prefijo))

    if (!cookie) {
        return null
    }

    return decodeURIComponent(
        cookie.substring(prefijo.length)
    )
}

// Interceptor de peticiones.
http.interceptors.request.use(
    config => {
        const metodo = (config.method || 'get').toLowerCase()

        const metodosProtegidos = [
            'post',
            'put',
            'patch',
            'delete',
        ]

        if (metodosProtegidos.includes(metodo)) {
            const token = obtenerCSRF()

            if (token) {
                config.headers['X-CSRFToken'] = token
            }
        }

        return config
    },
    error => Promise.reject(error)
)

// Interceptor de respuestas.
http.interceptors.response.use(
    response => response,

    error => {
        if (error.response) {
            const status = error.response.status

            switch (status) {
                case 400:
                    console.error('Solicitud incorrecta (400).')
                    break

                case 401:
                    console.error('Sesión no autenticada (401).')
                    break

                case 403:
                    console.error(
                        'Acceso denegado o token CSRF inválido (403).'
                    )
                    break

                case 404:
                    console.error('Recurso no encontrado (404).')
                    break

                case 500:
                    console.error('Error interno de Django (500).')
                    break

                default:
                    console.error(`Error HTTP ${status}.`)
            }
        } else if (error.request) {
            console.error(
                'No se recibió respuesta del servidor Django.'
            )
        } else {
            console.error(
                'Error al preparar la petición:',
                error.message
            )
        }

        return Promise.reject(error)
    }
)

export default http
