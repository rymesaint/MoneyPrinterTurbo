import { ref } from 'vue'

type Translations = Record<string, string>
type LocaleData = Record<string, { Language: string; Translation: Translations }>

const locales = ref<LocaleData>({})
const currentLocale = ref('en')
const loaded = ref(false)

const LOCALE_CODES = ['en', 'zh', 'de', 'es', 'id', 'pt', 'ru', 'tr', 'vi']

export function useI18n() {
  async function loadLocales() {
    if (loaded.value) return
    const results: LocaleData = {}
    await Promise.all(
      LOCALE_CODES.map(async (code) => {
        try {
          const res = await fetch(`/i18n/${code}.json`)
          if (res.ok) results[code] = await res.json()
        } catch { /* skip */ }
      })
    )
    locales.value = results
    loaded.value = true
  }

  function tr(key: string): string {
    const loc = locales.value[currentLocale.value]
    return loc?.Translation?.[key] ?? key
  }

  function setLocale(code: string) {
    currentLocale.value = code
  }

  function getLocaleList() {
    return Object.entries(locales.value).map(([code, data]) => ({
      code,
      name: data.Language || code,
    }))
  }

  return { tr, setLocale, currentLocale, loadLocales, getLocaleList, loaded }
}
