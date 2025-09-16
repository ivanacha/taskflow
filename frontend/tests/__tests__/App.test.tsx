import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import App from '../../src/App'

describe('App', () => {
  it('renders TaskFlow header', () => {
    render(<App />)
    expect(screen.getByText('TaskFlow')).toBeInTheDocument()
  })

  it('renders navigation links', () => {
    render(<App />)
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Projects')).toBeInTheDocument()
    expect(screen.getByText('Tasks')).toBeInTheDocument()
  })

  it('renders dashboard content by default', () => {
    render(<App />)
    expect(screen.getByText('Dashboard Page')).toBeInTheDocument()
  })
})