'use client'

import React, { useState, useEffect } from 'react'
import { getFallbackCover } from '@/lib/book-data'

interface BookCoverImageProps {
  isbn?: string
  thumbnail?: string
  title: string
  author?: string
  genre?: string
  className?: string
  alt?: string
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
}: BookCoverImageProps & { onCoverFailed?: () => void }) {
  const cleanIsbn = (isbn || '').replace(/[^0-9X]/gi, '').trim()
  const hasValidIsbn = cleanIsbn.length >= 9 && cleanIsbn !== '0'

  // Build candidate URL list in priority order
  const candidates: string[] = []

  // 1. Direct thumbnail from dataset / API
  if (
    thumbnail &&
    thumbnail.startsWith('http') &&
    !thumbnail.includes('placeholder.svg') &&
    !thumbnail.includes('cover-not-found') &&
    !thumbnail.startsWith('data:image/svg')
  ) {
    candidates.push(thumbnail)
  }

  // 2. High-speed Google Books Content CDN by ISBN (No rate limits, high uptime)
  if (hasValidIsbn) {
    candidates.push(`https://books.google.com/books/content?vid=ISBN${cleanIsbn}&printsec=frontcover&img=1&zoom=1`)
  }

  // 3. OpenLibrary Large Cover by ISBN
  if (hasValidIsbn) {
    candidates.push(`https://covers.openlibrary.org/b/isbn/${cleanIsbn}-L.jpg?default=false`)
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

  const fallbackSvg = getFallbackCover(title, author, genre)
  
  // Only use synthetic SVG if onCoverFailed is NOT provided (e.g. hero/detail decorative places)
  if (!onCoverFailed) {
    candidates.push(fallbackSvg)
  }

  const [currentIndex, setCurrentIndex] = useState(0)

  // Reset index if the book changes
  useEffect(() => {
    setCurrentIndex(0)
  }, [isbn, thumbnail, title])

  // If no candidates exist at all and failure handler is provided, trigger failure
  useEffect(() => {
    if (candidates.length === 0 && onCoverFailed) {
      onCoverFailed()
    }
  }, [candidates.length, onCoverFailed])

  const handleNextCandidate = () => {
    if (currentIndex < candidates.length - 1) {
      setCurrentIndex((prev) => prev + 1)
    } else if (onCoverFailed) {
      onCoverFailed()
    }
  }

  const currentSrc = candidates[currentIndex] || (onCoverFailed ? 'data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=' : fallbackSvg)

  return (
    <img
      src={currentSrc}
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
