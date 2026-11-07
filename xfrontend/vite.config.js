
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const raiz = dirname(fileURLToPath(import.meta.url))

export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, raiz, '')

    const aplicacion = env.APP
    const modulo = env.MODULE

    if (!aplicacion || !modulo) {
        throw new Error(
            'Debes definir APP y MODULE para ejecutar o compilar una pantalla.'
        )
    }

    const carpetaModulo = resolve(
        raiz,
        `apps/${aplicacion}/modules/${modulo}`
    )

    const archivoEntrada = resolve(
        carpetaModulo,
        `${modulo}.html`
    )

    const djangoProxy = {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        cookieDomainRewrite: 'localhost',
    }

    return {
        base: './',

        plugins: [vue()],

        resolve: {
            alias: {
                vue: 'vue/dist/vue.esm-bundler.js',
                '@': resolve(raiz, 'src'),
                '@apps': resolve(raiz, 'apps'),
            },
        },

        server: {
            proxy: {
                '^/get_': djangoProxy,
                '^/patch_': djangoProxy,
                '^/obtener_': djangoProxy,
                '^/api': djangoProxy,
                '^/hola_mundo_api': djangoProxy,
            },
        },

        build: {
            outDir: resolve(
                raiz,
                `../${aplicacion}/static/${aplicacion}`
            ),

            emptyOutDir: false,

            rollupOptions: {
                input: archivoEntrada,

                output: {
                    entryFileNames: `js/${modulo}.js`,
                    chunkFileNames: 'js/[name].js',

                    assetFileNames: (assetInfo) => {
                        const nombre = assetInfo.name || ''

                        if (nombre.endsWith('.css')) {
                            return `css/${modulo}.css`
                        }

                        if (/\.(woff2?|ttf|eot|otf)$/.test(nombre)) {
                            return 'fonts/[name][extname]'
                        }

                        return 'assets/[name][extname]'
                    },
                },
            },
        },
    }
})
