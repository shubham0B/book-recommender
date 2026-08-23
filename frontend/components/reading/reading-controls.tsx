'use client'

import { BookCheck, BookOpen, Heart, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import type { ReadingRecord, ReadingStatus } from '@/lib/reading-storage'

export function WishlistButton({ active, onToggle, compact = false }: { active: boolean; onToggle: () => void; compact?: boolean }) {
  return <Button type="button" variant={active ? 'default' : 'outline'} size={compact ? 'icon' : 'default'} onClick={onToggle} aria-pressed={active} aria-label={active ? 'Remove from wishlist' : 'Add to wishlist'}>{<Heart data-icon={compact ? undefined : 'inline-start'} className={active ? 'fill-current' : undefined} />}{!compact && (active ? 'Wishlisted' : 'Add to Wishlist')}</Button>
}

export function ReadingProgress({ value }: { value: number }) {
  return <div className="flex flex-col gap-2"><div className="flex items-center justify-between text-xs"><span className="text-muted-foreground">Reading progress</span><strong>{value}%</strong></div><div className="h-2 overflow-hidden rounded-full bg-secondary" role="progressbar" aria-valuenow={value} aria-valuemin={0} aria-valuemax={100}><div className="h-full rounded-full bg-accent transition-all duration-500" style={{ width: `${value}%` }} /></div></div>
}

export function ReadingControls({ record, onStart, onProgress, onStatus, onRemove }: { record?: ReadingRecord; onStart: () => void; onProgress: (value: number) => void; onStatus: (status: ReadingStatus) => void; onRemove?: () => void }) {
  if (!record) return <Button type="button" onClick={onStart}><BookOpen data-icon="inline-start" />Start Reading</Button>
  return <div className="flex flex-col gap-4"><ReadingProgress value={record.progress} /><div className="flex flex-wrap items-center gap-2"><select aria-label="Reading status" value={record.status} onChange={(event) => onStatus(event.target.value as ReadingStatus)} className="h-9 rounded-lg border border-border bg-background px-3 text-sm"><option>Want to Read</option><option>Reading</option><option>Completed</option></select><label className="flex items-center gap-2 text-sm"><span>Progress</span><input aria-label="Reading progress percentage" type="range" min="0" max="100" step="5" value={record.progress} onChange={(event) => onProgress(Number(event.target.value))} disabled={record.status === 'Completed'} className="accent-accent" /></label>{record.status !== 'Completed' && <Button type="button" size="sm" variant="secondary" onClick={() => onStatus('Completed')}><BookCheck data-icon="inline-start" />Complete</Button>}{onRemove && <Button type="button" size="icon-sm" variant="ghost" onClick={onRemove} aria-label="Remove from reading history"><Trash2 /></Button>}</div></div>
}
