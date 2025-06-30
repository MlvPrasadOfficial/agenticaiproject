'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Search, X, Loader2, Filter, SortAsc } from 'lucide-react';

interface AnimatedSearchBarProps {
  placeholder?: string;
  onSearch?: (query: string) => void;
  onClear?: () => void;
  onFilterClick?: () => void;
  onSortClick?: () => void;
  isLoading?: boolean;
  hasFilters?: boolean;
  hasSorting?: boolean;
  suggestions?: string[];
  className?: string;
  expandedWidth?: string;
  collapsedWidth?: string;
}

export default function AnimatedSearchBar({
  placeholder = 'Search...',
  onSearch,
  onClear,
  onFilterClick,
  onSortClick,
  isLoading = false,
  hasFilters = false,
  hasSorting = false,
  suggestions = [],
  className = '',
  expandedWidth = 'w-96',
  collapsedWidth = 'w-64'
}: AnimatedSearchBarProps) {
  const [isFocused, setIsFocused] = useState(false);
  const [query, setQuery] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [filteredSuggestions, setFilteredSuggestions] = useState<string[]>([]);
  const [selectedSuggestionIndex, setSelectedSuggestionIndex] = useState(-1);
  
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const debounceRef = useRef<NodeJS.Timeout>();

  // Filter suggestions based on query
  useEffect(() => {
    if (query && suggestions.length > 0) {
      const filtered = suggestions.filter(suggestion =>
        suggestion.toLowerCase().includes(query.toLowerCase())
      );
      setFilteredSuggestions(filtered);
      setShowSuggestions(filtered.length > 0);
    } else {
      setFilteredSuggestions([]);
      setShowSuggestions(false);
    }
    setSelectedSuggestionIndex(-1);
  }, [query, suggestions]);

  // Debounced search
  useEffect(() => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    debounceRef.current = setTimeout(() => {
      if (query && onSearch) {
        onSearch(query);
      }
    }, 300);

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, [query, onSearch]);

  // Handle click outside to close suggestions
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsFocused(false);
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
  };

  const handleInputFocus = () => {
    setIsFocused(true);
    if (filteredSuggestions.length > 0) {
      setShowSuggestions(true);
    }
  };

  const handleInputBlur = () => {
    // Delay to allow suggestion clicks
    setTimeout(() => {
      setIsFocused(false);
      setShowSuggestions(false);
    }, 200);
  };

  const handleClear = () => {
    setQuery('');
    setFilteredSuggestions([]);
    setShowSuggestions(false);
    setSelectedSuggestionIndex(-1);
    if (onClear) {
      onClear();
    }
    inputRef.current?.focus();
  };

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
    setShowSuggestions(false);
    setSelectedSuggestionIndex(-1);
    if (onSearch) {
      onSearch(suggestion);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!showSuggestions) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedSuggestionIndex(prev => 
          prev < filteredSuggestions.length - 1 ? prev + 1 : 0
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedSuggestionIndex(prev => 
          prev > 0 ? prev - 1 : filteredSuggestions.length - 1
        );
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedSuggestionIndex >= 0) {
          handleSuggestionClick(filteredSuggestions[selectedSuggestionIndex]);
        } else if (query && onSearch) {
          onSearch(query);
          setShowSuggestions(false);
        }
        break;
      case 'Escape':
        setShowSuggestions(false);
        setSelectedSuggestionIndex(-1);
        inputRef.current?.blur();
        break;
    }
  };

  return (
    <div ref={containerRef} className={`relative ${className}`}>
      {/* Main Search Container */}
      <div 
        className={`
          relative flex items-center transition-all duration-300 ease-in-out
          ${isFocused ? expandedWidth : collapsedWidth}
          bg-white/10 dark:bg-gray-800/20 backdrop-blur-xl
          border border-white/20 dark:border-gray-700/30
          rounded-2xl shadow-lg hover:shadow-xl
          ${isFocused ? 'shadow-2xl ring-2 ring-blue-500/30' : ''}
        `}
      >
        {/* Search Icon */}
        <div className="absolute left-4 flex items-center">
          {isLoading ? (
            <Loader2 className="w-5 h-5 text-gray-400 animate-spin" />
          ) : (
            <Search 
              className={`w-5 h-5 transition-colors duration-200 ${
                isFocused ? 'text-blue-500' : 'text-gray-400'
              }`} 
            />
          )}
        </div>

        {/* Input Field */}
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={handleInputChange}
          onFocus={handleInputFocus}
          onBlur={handleInputBlur}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className={`
            w-full h-12 pl-12 pr-20 bg-transparent
            text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400
            focus:outline-none focus:ring-0 border-0
            transition-all duration-200
            ${isFocused ? 'text-base' : 'text-sm'}
          `}
          aria-label="Search input"
          aria-expanded={showSuggestions}
          aria-haspopup="listbox"
          role="combobox"
          aria-autocomplete="list"
          aria-describedby={showSuggestions ? 'search-suggestions' : undefined}
        />

        {/* Action Buttons */}
        <div className="absolute right-2 flex items-center space-x-1">
          {/* Clear Button */}
          {query && (
            <button
              onClick={handleClear}
              className="p-2 rounded-lg hover:bg-white/10 dark:hover:bg-gray-700/30 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
              aria-label="Clear search"
              title="Clear search"
            >
              <X className="w-4 h-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200" />
            </button>
          )}

          {/* Filter Button */}
          {hasFilters && (
            <button
              onClick={onFilterClick}
              className="p-2 rounded-lg hover:bg-white/10 dark:hover:bg-gray-700/30 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
              aria-label="Open filters"
              title="Open filters"
            >
              <Filter className="w-4 h-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200" />
            </button>
          )}

          {/* Sort Button */}
          {hasSorting && (
            <button
              onClick={onSortClick}
              className="p-2 rounded-lg hover:bg-white/10 dark:hover:bg-gray-700/30 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
              aria-label="Sort options"
              title="Sort options"
            >
              <SortAsc className="w-4 h-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200" />
            </button>
          )}
        </div>

        {/* Focus Ring Animation */}
        <div 
          className={`
            absolute inset-0 rounded-2xl transition-all duration-300
            ${isFocused 
              ? 'bg-gradient-to-r from-blue-500/5 to-purple-500/5 ring-1 ring-blue-500/20' 
              : ''
            }
          `}
          style={{ pointerEvents: 'none' }}
        />
      </div>

      {/* Suggestions Dropdown */}
      {showSuggestions && filteredSuggestions.length > 0 && (
        <div 
          className={`
            absolute top-full mt-2 left-0 right-0 z-50
            bg-white/95 dark:bg-gray-800/95 backdrop-blur-xl
            border border-white/20 dark:border-gray-700/30
            rounded-xl shadow-2xl max-h-64 overflow-y-auto
            animate-in fade-in slide-in-from-top-2 duration-200
          `}
          id="search-suggestions"
          role="listbox"
        >
          {filteredSuggestions.map((suggestion, index) => (
            <button
              key={index}
              onClick={() => handleSuggestionClick(suggestion)}
              className={`
                w-full px-4 py-3 text-left hover:bg-white/10 dark:hover:bg-gray-700/30
                transition-colors duration-150 first:rounded-t-xl last:rounded-b-xl
                ${selectedSuggestionIndex === index 
                  ? 'bg-blue-500/10 text-blue-700 dark:text-blue-300' 
                  : 'text-gray-700 dark:text-gray-200'
                }
                focus:outline-none focus:bg-blue-500/10 focus:text-blue-700 dark:focus:text-blue-300
              `}
              role="option"
              aria-selected={selectedSuggestionIndex === index}
            >
              <div className="flex items-center space-x-3">
                <Search className="w-4 h-4 text-gray-400" />
                <span className="truncate">{suggestion}</span>
              </div>
            </button>
          ))}
        </div>
      )}

      {/* Loading State Overlay */}
      {isLoading && (
        <div className="absolute inset-0 bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm rounded-2xl flex items-center justify-center">
          <Loader2 className="w-6 h-6 text-blue-500 animate-spin" />
        </div>
      )}
    </div>
  );
}
