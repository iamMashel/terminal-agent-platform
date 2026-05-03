export default defineNuxtConfig({
  compatibilityDate: '2026-05-03',
  devtools: { enabled: true },
  runtimeConfig: {
    public: {
      apiBaseUrl: 'http://localhost:8000',
    },
  },
  typescript: {
    strict: true,
  },
})
