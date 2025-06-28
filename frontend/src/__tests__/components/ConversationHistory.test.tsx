/**
 * @jest-environment jsdom
 */

import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ConversationHistory, { ConversationMessage } from '@/components/ConversationHistory'

const mockMessages: ConversationMessage[] = [
  {
    id: '1',
    type: 'user',
    content: 'Hello, can you help me analyze this data?',
    timestamp: new Date('2023-06-28T10:00:00Z'),
  },
  {
    id: '2',
    type: 'assistant',
    content: 'Of course! I\'d be happy to help you analyze your data. Could you please upload the file or provide more details?',
    timestamp: new Date('2023-06-28T10:01:00Z'),
    metadata: {
      agentType: 'planning',
      executionId: 'exec-123',
      processingTime: 1500,
      confidence: 0.95
    }
  },
  {
    id: '3',
    type: 'system',
    content: 'File uploaded successfully: sales_data.csv',
    timestamp: new Date('2023-06-28T10:02:00Z'),
  }
]

const mockHandlers = {
  onMessageEdit: jest.fn(),
  onMessageDelete: jest.fn(),
  onMessageFeedback: jest.fn(),
  onMessageCopy: jest.fn(),
}

describe('ConversationHistory Component', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    
    // Mock clipboard API
    Object.defineProperty(navigator, 'clipboard', {
      writable: true,
      value: {
        writeText: jest.fn(() => Promise.resolve()),
      },
    })
  })

  it('renders conversation messages', () => {
    render(<ConversationHistory messages={mockMessages} />)
    
    expect(screen.getByText('Hello, can you help me analyze this data?')).toBeInTheDocument()
    expect(screen.getByText(/Of course! I'd be happy to help/)).toBeInTheDocument()
    expect(screen.getByText('File uploaded successfully: sales_data.csv')).toBeInTheDocument()
  })

  it('displays empty state when no messages', () => {
    render(<ConversationHistory messages={[]} />)
    
    expect(screen.getByText('No conversation yet')).toBeInTheDocument()
    expect(screen.getByText(/Start a conversation by typing/)).toBeInTheDocument()
  })

  it('shows different icons for different message types', () => {
    render(<ConversationHistory messages={mockMessages} />)
    
    // Check that different message types have different styling
    const messageContainers = screen.getAllByRole('generic').filter(el => 
      el.className?.includes('border-blue-200') || 
      el.className?.includes('border-green-200') || 
      el.className?.includes('border-gray-200')
    )
    
    expect(messageContainers.length).toBeGreaterThan(0)
  })

  it('displays message metadata for assistant messages', () => {
    render(<ConversationHistory messages={mockMessages} />)
    
    expect(screen.getByText('Planning Agent')).toBeInTheDocument()
    expect(screen.getByText('(1500ms)')).toBeInTheDocument()
  })

  it('allows copying message content', async () => {
    render(<ConversationHistory messages={mockMessages} {...mockHandlers} />)
    
    const copyButtons = screen.getAllByTitle('Copy message')
    await userEvent.click(copyButtons[0])
    
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
      'Hello, can you help me analyze this data?'
    )
    expect(mockHandlers.onMessageCopy).toHaveBeenCalledWith(
      'Hello, can you help me analyze this data?'
    )
  })

  it('shows edit functionality for user messages', async () => {
    render(<ConversationHistory messages={mockMessages} {...mockHandlers} />)
    
    const editButtons = screen.getAllByTitle('Edit message')
    expect(editButtons.length).toBeGreaterThan(0)
    
    await userEvent.click(editButtons[0])
    
    // Should show textarea for editing
    expect(screen.getByRole('textbox')).toBeInTheDocument()
    expect(screen.getByText('Save')).toBeInTheDocument()
    expect(screen.getByText('Cancel')).toBeInTheDocument()
  })

  it('handles message deletion', async () => {
    render(<ConversationHistory messages={mockMessages} {...mockHandlers} />)
    
    const deleteButtons = screen.getAllByTitle('Delete message')
    await userEvent.click(deleteButtons[0])
    
    expect(mockHandlers.onMessageDelete).toHaveBeenCalledWith('1')
  })

  it('shows feedback buttons for assistant messages', () => {
    render(<ConversationHistory messages={mockMessages} {...mockHandlers} />)
    
    expect(screen.getByTitle('Thumbs up')).toBeInTheDocument()
    expect(screen.getByTitle('Thumbs down')).toBeInTheDocument()
  })

  it('handles feedback submission', async () => {
    render(<ConversationHistory messages={mockMessages} {...mockHandlers} />)
    
    const thumbsUpButton = screen.getByTitle('Thumbs up')
    await userEvent.click(thumbsUpButton)
    
    expect(mockHandlers.onMessageFeedback).toHaveBeenCalledWith('2', { rating: 'positive' })
  })

  it('displays confidence indicators', () => {
    render(<ConversationHistory messages={mockMessages} />)
    
    expect(screen.getByText('95%')).toBeInTheDocument()
  })

  it('formats timestamps correctly', () => {
    render(<ConversationHistory messages={mockMessages} />)
    
    // Should show relative time
    expect(screen.getByText(/ago/)).toBeInTheDocument()
  })
})
