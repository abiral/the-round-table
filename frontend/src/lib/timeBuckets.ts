/**
 * Group dated items into Today / Yesterday / Last 7 Days / Last 30 Days / Older.
 * Mirrors the BotAI reference sidebar grouping.
 */

export type Bucket = 'Today' | 'Yesterday' | 'Last 7 Days' | 'Last 30 Days' | 'Older'

const BUCKET_ORDER: Bucket[] = ['Today', 'Yesterday', 'Last 7 Days', 'Last 30 Days', 'Older']

function startOfDay(d: Date): Date {
  const x = new Date(d)
  x.setHours(0, 0, 0, 0)
  return x
}

function daysBetween(a: Date, b: Date): number {
  const ms = startOfDay(a).getTime() - startOfDay(b).getTime()
  return Math.round(ms / 86_400_000)
}

export function bucketFor(date: Date, now: Date = new Date()): Bucket {
  const diff = daysBetween(now, date)
  if (diff <= 0) return 'Today'
  if (diff === 1) return 'Yesterday'
  if (diff <= 7) return 'Last 7 Days'
  if (diff <= 30) return 'Last 30 Days'
  return 'Older'
}

export interface Bucketed<T> {
  bucket: Bucket
  items: T[]
}

/**
 * Group items by bucket, preserving the input order within each bucket.
 * Buckets are emitted in the canonical BUCKET_ORDER and empty ones are dropped.
 */
export function groupByBucket<T>(items: T[], getDate: (item: T) => Date): Bucketed<T>[] {
  const now = new Date()
  const map = new Map<Bucket, T[]>()
  for (const item of items) {
    const b = bucketFor(getDate(item), now)
    const arr = map.get(b)
    if (arr) arr.push(item)
    else map.set(b, [item])
  }
  const out: Bucketed<T>[] = []
  for (const bucket of BUCKET_ORDER) {
    const items = map.get(bucket)
    if (items && items.length) out.push({ bucket, items })
  }
  return out
}
