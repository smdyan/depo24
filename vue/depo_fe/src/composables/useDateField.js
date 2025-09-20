import { ref, computed } from 'vue'

function normalizeDate(d) {
  if (!(d instanceof Date)) return null
  const nd = new Date(d)
  nd.setHours(0, 0, 0, 0)
  return nd
}

export function useDateField(initial = new Date()) {
  const date = ref(normalizeDate(initial))
  const dateStr = computed({
    get: () => {
      const d = date.value
      return d ? d.toISOString().split('T')[0] : ''
    },
    set: (val) => {
      date.value = val ? normalizeDate(new Date(val)) : null
    }
  })

  return { date, dateStr }
}