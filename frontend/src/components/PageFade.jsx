import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'

export default function PageFade({ children }) {
  const location = useLocation()

  useEffect(() => {
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    window.scrollTo({ top: 0, left: 0, behavior: reduced ? 'auto' : 'instant' })
  }, [location.pathname])

  return (
    <div key={location.pathname} className="animate-page flex h-full min-h-full flex-1 flex-col">
      {children}
    </div>
  )
}
