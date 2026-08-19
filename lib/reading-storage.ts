export type ReadingStatus = 'Want to Read' | 'Reading' | 'Completed'

export type ReadingRecord = {
  isbn: string
  status: ReadingStatus
  progress: number
  startedAt?: string
  completedAt?: string
  lastReadAt: string
}

const WISHLIST_KEY = 'bookmind:wishlist:v1'
const HISTORY_KEY = 'bookmind:history:v1'

function safeRead<T>(key: string, fallback: T): T {
  if (typeof window === 'undefined') return fallback
  try {
    const value = JSON.parse(window.localStorage.getItem(key) ?? '')
    return value ?? fallback
  } catch {
    return fallback
  }
}

export function readWishlist() {
  const items = safeRead<unknown>(WISHLIST_KEY, [])
  return Array.isArray(items) ? [...new Set(items.filter((item): item is string => typeof item === 'string'))] : []
}

export function writeWishlist(items: string[]) {
  window.localStorage.setItem(WISHLIST_KEY, JSON.stringify([...new Set(items)]))
}

export function readHistory() {
  const records = safeRead<unknown>(HISTORY_KEY, [])
  if (!Array.isArray(records)) return []
  return records.filter((record): record is ReadingRecord => Boolean(record && typeof record === 'object' && 'isbn' in record && 'status' in record && 'progress' in record && 'lastReadAt' in record))
}

export function writeHistory(records: ReadingRecord[]) {
  window.localStorage.setItem(HISTORY_KEY, JSON.stringify(records))
}

export function updateReadingRecord(records: ReadingRecord[], isbn: string, updates: Partial<ReadingRecord>) {
  const now = new Date().toISOString()
  const current = records.find((record) => record.isbn === isbn)
  const progress = Math.max(0, Math.min(100, Math.round(updates.progress ?? current?.progress ?? 0)))
  const status: ReadingStatus = updates.status ?? current?.status ?? 'Reading'
  const next: ReadingRecord = {
    isbn,
    progress: status === 'Completed' ? 100 : progress,
    status,
    startedAt: current?.startedAt ?? (status === 'Reading' ? now : undefined),
    completedAt: status === 'Completed' ? current?.completedAt ?? now : undefined,
    lastReadAt: now,
    ...updates,
  }
  next.progress = next.status === 'Completed' ? 100 : Math.max(0, Math.min(100, Math.round(next.progress)))
  return [next, ...records.filter((record) => record.isbn !== isbn)]
}
