// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  ssr: false,
  devtools: { enabled: false },
  nitro: {
    output: {
      publicDir: '../resource/public'
    },
    devProxy: {
      '/api': { target: 'http://127.0.0.1:8080', changeOrigin: true },
      '/tasks': { target: 'http://127.0.0.1:8080', changeOrigin: true },
    }
  },
  app: {
    head: {
      title: 'MoneyPrinterTurbo - AI Video Generator',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'Simply provide a topic or keyword, and MoneyPrinterTurbo will automatically generate video script, materials, subtitles, and background music to synthesize a high-definition short video.' }
      ],
      link: [
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap' }
      ]
    }
  }
})
