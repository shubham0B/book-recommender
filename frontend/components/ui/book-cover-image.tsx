'use client'

import React, { useState, useEffect } from 'react'

interface BookCoverImageProps {
  isbn?: string
  thumbnail?: string
  title: string
  author?: string
  genre?: string
  className?: string
  alt?: string
  onCoverFailed?: () => void
}

const GENRE_PALETTES: Record<string, { bg: string; accent: string; spine: string }> = {
  'Science Fiction': { bg: 'linear-gradient(135deg, #020617 0%, #0f172a 50%, #1e3a8a 100%)', accent: '#60a5fa', spine: '#030712' },
  'Fantasy': { bg: 'linear-gradient(135deg, #1e1035 0%, #3b0764 50%, #581c87 100%)', accent: '#c084fc', spine: '#120721' },
  'Mystery': { bg: 'linear-gradient(135deg, #0b0f19 0%, #1e1b4b 50%, #312e81 100%)', accent: '#818cf8', spine: '#05070d' },
  'Thriller': { bg: 'linear-gradient(135deg, #1c0404 0%, #450a0a 50%, #7f1d1d 100%)', accent: '#f87171', spine: '#0f0202' },
  'Horror': { bg: 'linear-gradient(135deg, #09090b 0%, #18181b 50%, #27272a 100%)', accent: '#e4e4e7', spine: '#000000' },
  'Romance': { bg: 'linear-gradient(135deg, #2a0418 0%, #500724 50%, #831843 100%)', accent: '#f472b6', spine: '#17010c' },
  'Self Development': { bg: 'linear-gradient(135deg, #022c22 0%, #064e3b 50%, #047857 100%)', accent: '#34d399', spine: '#011712' },
  'Psychology': { bg: 'linear-gradient(135deg, #042f2e 0%, #134e4a 50%, #0f766e 100%)', accent: '#2dd4bf', spine: '#021817' },
  'Philosophy': { bg: 'linear-gradient(135deg, #261502 0%, #451a03 50%, #78350f 100%)', accent: '#fbbf24', spine: '#140a01' },
  'History': { bg: 'linear-gradient(135deg, #1c1917 0%, #292524 50%, #44403c 100%)', accent: '#d6d3d1', spine: '#0c0a09' },
  'Biography': { bg: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%)', accent: '#94a3b8', spine: '#080d17' },
  'Fiction': { bg: 'linear-gradient(135deg, #081b33 0%, #172554 50%, #1e3a8a 100%)', accent: '#93c5fd', spine: '#040d1a' },
  'Nonfiction': { bg: 'linear-gradient(135deg, #09131f 0%, #0f172a 50%, #1e293b 100%)', accent: '#cbd5e1', spine: '#04090f' },
  'Young Adult': { bg: 'linear-gradient(135deg, #2e022f 0%, #4a044e 50%, #701a75 100%)', accent: '#e879f9', spine: '#170118' },
  "Children's Fiction": { bg: 'linear-gradient(135deg, #0f2e29 0%, #115e59 50%, #0d9488 100%)', accent: '#5eead4', spine: '#071714' },
  "Children's Nonfiction": { bg: 'linear-gradient(135deg, #1e293b 0%, #0369a1 50%, #0284c7 100%)', accent: '#38bdf8', spine: '#0b1320' },
}

export function GeneratedBookCover({
  title,
  author,
  genre = 'Fiction',
  className = '',
}: {
  title: string
  author?: string
  genre?: string
  className?: string
}) {
  const palette = GENRE_PALETTES[genre || 'Fiction'] || GENRE_PALETTES['Fiction']
  const cleanTitle = (title || 'Untitled Book').trim()
  const cleanAuthor = (author || 'Renowned Author').trim()

  return (
    <div
      className={`relative overflow-hidden select-none flex flex-col justify-between p-4 shadow-lg border border-white/10 ${className}`}
      style={{
        background: palette.bg,
        aspectRatio: '2/3',
        minHeight: '220px',
      }}
    >
      {/* 3D Spine effect shadow on the left */}
      <div
        className="absolute left-0 top-0 bottom-0 w-4 pointer-events-none"
        style={{
          background: 'linear-gradient(to right, rgba(0,0,0,0.6) 0%, rgba(255,255,255,0.15) 30%, rgba(0,0,0,0.3) 70%, transparent 100%)',
        }}
      />

      {/* Decorative inner frame */}
      <div className="absolute inset-2 border border-amber-400/30 rounded pointer-events-none" />
      <div className="absolute inset-3 border border-amber-400/15 rounded pointer-events-none" />

      {/* Top Genre Badge */}
      <div className="relative z-10 text-center pt-1">
        <span
          className="inline-block px-2.5 py-0.5 text-[10px] font-bold tracking-widest uppercase rounded-full border border-amber-400/40 bg-black/40 text-amber-300 shadow-sm"
        >
          {genre || 'LITERATURE'}
        </span>
      </div>

      {/* Center Title */}
      <div className="relative z-10 text-center my-auto px-1">
        <h3
          className="text-white font-serif font-bold text-sm sm:text-base leading-tight tracking-wide drop-shadow-[0_2px_4px_rgba(0,0,0,0.8)] line-clamp-3"
          style={{ fontFamily: "'Cinzel', 'Playfair Display', Georgia, serif" }}
        >
          {cleanTitle}
        </h3>
        <div className="w-10 h-0.5 bg-amber-400/60 mx-auto my-2 rounded-full" />
      </div>

      {/* Bottom Author */}
      <div className="relative z-10 text-center pb-1">
        <p className="text-slate-200 text-[11px] sm:text-xs font-sans font-semibold tracking-wider uppercase drop-shadow-[0_1px_3px_rgba(0,0,0,0.8)] line-clamp-1">
          {cleanAuthor}
        </p>
      </div>
    </div>
  )
}

export function BookCoverImage({
  isbn,
  thumbnail,
  title,
  author,
  genre,
  className = '',
  alt,
  onCoverFailed,
}: BookCoverImageProps) {
  const cleanIsbn = (isbn || '').replace(/[^0-9X]/gi, '').trim()
  const hasValidIsbn = cleanIsbn.length >= 9 && cleanIsbn !== '0'

  // Build candidate URL list in priority order
  const candidates: string[] = []

  // 1. Direct thumbnail from dataset / API (skip placeholders and broken Amazon links)
  if (
    thumbnail &&
    thumbnail.startsWith('http') &&
    !thumbnail.includes('placeholder.svg') &&
    !thumbnail.includes('cover-not-found') &&
    !thumbnail.startsWith('data:image/svg')
  ) {
    candidates.push(thumbnail)
  }

  // 2. OpenLibrary Large Cover by ISBN (high uptime, CDN cached, no hotlink blocks)
  if (hasValidIsbn) {
    candidates.push(`https://covers.openlibrary.org/b/isbn/${cleanIsbn}-L.jpg?default=false`)
  }

  // 3. High-speed Google Books Content CDN by ISBN
  if (hasValidIsbn) {
    candidates.push(`https://books.google.com/books/content?vid=ISBN${cleanIsbn}&printsec=frontcover&img=1&zoom=1`)
  }

  // 4. OpenLibrary Medium Cover by ISBN
  if (hasValidIsbn) {
    candidates.push(`https://covers.openlibrary.org/b/isbn/${cleanIsbn}-M.jpg?default=false`)
  }

  // 5. Backend Dynamic Cover Proxy
  if (title) {
    const backendUrl = `https://book-recommender-6cy9.onrender.com/api/books/cover?title=${encodeURIComponent(title)}&author=${encodeURIComponent(author || '')}&isbn=${encodeURIComponent(cleanIsbn || '')}`
    candidates.push(backendUrl)
  }

  const [currentIndex, setCurrentIndex] = useState(0)
  const [useFallbackComponent, setUseFallbackComponent] = useState(false)

  // Reset state when book props change
  useEffect(() => {
    setCurrentIndex(0)
    setUseFallbackComponent(candidates.length === 0)
  }, [isbn, thumbnail, title])

  const handleNextCandidate = () => {
    if (currentIndex < candidates.length - 1) {
      setCurrentIndex((prev) => prev + 1)
    } else {
      setUseFallbackComponent(true)
      if (onCoverFailed) {
        onCoverFailed()
      }
    }
  }

  // If all image links failed or none exist, render the gorgeous inline custom cover
  if (useFallbackComponent || candidates.length === 0) {
    return (
      <GeneratedBookCover
        title={title}
        author={author}
        genre={genre}
        className={className}
      />
    )
  }

  return (
    <img
      src={candidates[currentIndex]}
      alt={alt || `Cover of ${title}`}
      className={className}
      loading="lazy"
      onLoad={(e) => {
        const img = e.currentTarget
        // Detect 1x1 transparent GIFs returned by OpenLibrary on missing covers
        // Detect 128x170 "No Image Available" placeholder returned by Google Books
        if (
          (img.naturalWidth <= 2 || img.naturalHeight <= 2) ||
          (img.naturalWidth === 128 && img.naturalHeight === 170)
        ) {
          handleNextCandidate()
        }
      }}
      onError={() => {
        handleNextCandidate()
      }}
    />
  )
}
