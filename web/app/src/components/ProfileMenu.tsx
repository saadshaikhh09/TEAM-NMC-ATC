import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import type { Account } from '../services/api'

const initials = (name: string) => name.trim().split(/\s+/).slice(0, 2).map((part) => part[0]).join('').toUpperCase()

export function ProfileMenu({ account, onLogout }: { account: Account; onLogout: () => Promise<void> }) {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)
  useEffect(() => {
    if (!open) return
    const close = (event: MouseEvent) => { if (!ref.current?.contains(event.target as Node)) setOpen(false) }
    const escape = (event: KeyboardEvent) => { if (event.key === 'Escape') setOpen(false) }
    document.addEventListener('mousedown', close)
    document.addEventListener('keydown', escape)
    return () => { document.removeEventListener('mousedown', close); document.removeEventListener('keydown', escape) }
  }, [open])

  return (
    <div className="relative" ref={ref}>
      <button aria-expanded={open} aria-haspopup="menu" className="profile-trigger" onClick={() => setOpen(!open)} type="button">
        <span>{initials(account.name)}</span><b>{account.name}</b><i aria-hidden="true">⌄</i>
      </button>
      {open && (
        <div className="profile-panel" role="menu">
          <div><strong>{account.name}</strong><small>{account.email}</small></div>
          <Link onClick={() => setOpen(false)} role="menuitem" to="/app/profile">Profile & safeguards</Link>
          <button onClick={() => void onLogout()} role="menuitem" type="button">Log out</button>
        </div>
      )}
    </div>
  )
}
