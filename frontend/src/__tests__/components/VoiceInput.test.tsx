/**
 * @jest-environment jsdom
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import VoiceInput from '@/components/VoiceInput'

// Mock implementations
const mockOnTranscript = jest.fn()
const mockOnVoiceStart = jest.fn()
const mockOnVoiceEnd = jest.fn()

describe('VoiceInput Component', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    // Reset SpeechRecognition mock
    global.SpeechRecognition = jest.fn(() => ({
      start: jest.fn(),
      stop: jest.fn(),
      abort: jest.fn(),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      onstart: null,
      onend: null,
      onresult: null,
      onerror: null,
      continuous: true,
      interimResults: true,
      lang: 'en-US',
    }))
    global.webkitSpeechRecognition = global.SpeechRecognition
  })

  it('renders voice input button', () => {
    render(<VoiceInput onTranscript={mockOnTranscript} />)
    
    const button = screen.getByRole('button')
    expect(button).toBeInTheDocument()
    expect(screen.getByText('Click to speak')).toBeInTheDocument()
  })

  it('shows unsupported message when Speech Recognition is not available', () => {
    // Remove SpeechRecognition to simulate unsupported browser
    delete global.SpeechRecognition
    delete global.webkitSpeechRecognition

    render(<VoiceInput onTranscript={mockOnTranscript} />)
    
    expect(screen.getByText('Voice input not supported')).toBeInTheDocument()
  })

  it('disables button when disabled prop is true', () => {
    render(<VoiceInput onTranscript={mockOnTranscript} disabled={true} />)
    
    const button = screen.getByRole('button')
    expect(button).toBeDisabled()
  })

  it('calls onTranscript when speech result is received', async () => {
    const mockRecognition = {
      start: jest.fn(),
      stop: jest.fn(),
      abort: jest.fn(),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      onstart: null,
      onend: null,
      onresult: null,
      onerror: null,
      continuous: true,
      interimResults: true,
      lang: 'en-US',
    }

    global.SpeechRecognition = jest.fn(() => mockRecognition)

    render(<VoiceInput onTranscript={mockOnTranscript} />)
    
    const button = screen.getByRole('button')
    await userEvent.click(button)

    // Simulate speech recognition result
    if (mockRecognition.onresult) {
      const mockEvent = {
        resultIndex: 0,
        results: [
          {
            0: { transcript: 'Hello world' },
            isFinal: true,
            length: 1
          }
        ]
      }
      mockRecognition.onresult(mockEvent)
    }

    await waitFor(() => {
      expect(mockOnTranscript).toHaveBeenCalledWith('Hello world')
    })
  })

  it('toggles listening state when button is clicked', async () => {
    const mockRecognition = {
      start: jest.fn(),
      stop: jest.fn(),
      abort: jest.fn(),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      onstart: null,
      onend: null,
      onresult: null,
      onerror: null,
      continuous: true,
      interimResults: true,
      lang: 'en-US',
    }

    global.SpeechRecognition = jest.fn(() => mockRecognition)

    render(<VoiceInput onTranscript={mockOnTranscript} />)
    
    const button = screen.getByRole('button')
    
    // Start listening
    await userEvent.click(button)
    expect(mockRecognition.start).toHaveBeenCalled()

    // Simulate onstart callback
    if (mockRecognition.onstart) {
      mockRecognition.onstart()
    }

    await waitFor(() => {
      expect(screen.getByText('Listening...')).toBeInTheDocument()
    })
  })
})
