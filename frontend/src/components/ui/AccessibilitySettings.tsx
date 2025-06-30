'use client';

import React, { useState, useEffect } from 'react';
import { Settings, Eye, Palette, Volume2, Keyboard } from 'lucide-react';
import { useHighContrast, useReducedMotion, useAnnouncement, LiveRegion } from '@/lib/accessibility';

interface AccessibilitySettingsProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function AccessibilitySettings({ isOpen, onClose }: AccessibilitySettingsProps) {
  const { isHighContrast, toggleHighContrast } = useHighContrast();
  const prefersReducedMotion = useReducedMotion();
  const { announcement, announce } = useAnnouncement();
  
  const [fontSize, setFontSize] = useState('normal');
  const [soundEnabled, setSoundEnabled] = useState(false);
  const [keyboardHelpVisible, setKeyboardHelpVisible] = useState(false);

  useEffect(() => {
    // Load settings from localStorage
    const savedSettings = localStorage.getItem('accessibility-settings');
    if (savedSettings) {
      const settings = JSON.parse(savedSettings);
      setFontSize(settings.fontSize || 'normal');
      setSoundEnabled(settings.soundEnabled || false);
    }
  }, []);

  const saveSettings = () => {
    const settings = {
      fontSize,
      soundEnabled,
      highContrast: isHighContrast,
    };
    localStorage.setItem('accessibility-settings', JSON.stringify(settings));
    announce('Settings saved successfully');
  };

  const handleFontSizeChange = (size: string) => {
    setFontSize(size);
    document.documentElement.style.fontSize = 
      size === 'large' ? '1.125em' : 
      size === 'larger' ? '1.25em' : '1em';
    
    announce(`Font size changed to ${size}`);
  };

  if (!isOpen) return null;

  return (
    <>
      <div 
        className="fixed inset-0 bg-black/50 z-40"
        onClick={onClose}
        aria-hidden="true"
      />
      
      <div
        role="dialog"
        aria-labelledby="accessibility-settings-title"
        aria-modal="true"
        className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 w-full max-w-lg"
      >
        <div className="card-glass p-6 m-4">
          <div className="flex items-center justify-between mb-6">
            <h2 
              id="accessibility-settings-title"
              className="text-xl font-bold text-text-primary flex items-center gap-2"
            >
              <Settings className="w-5 h-5" aria-hidden="true" />
              Accessibility Settings
            </h2>
            <button
              onClick={onClose}
              className="btn-secondary px-3 py-1 text-sm"
              aria-label="Close accessibility settings"
            >
              ×
            </button>
          </div>

          <div className="space-y-6">
            {/* Visual Settings */}
            <section>
              <h3 className="text-lg font-semibold text-text-primary mb-3 flex items-center gap-2">
                <Eye className="w-4 h-4" aria-hidden="true" />
                Visual
              </h3>
              
              <div className="space-y-4">
                <div>
                  <label 
                    htmlFor="font-size"
                    className="block text-sm font-medium text-text-secondary mb-2"
                  >
                    Font Size
                  </label>
                  <select
                    id="font-size"
                    value={fontSize}
                    onChange={(e) => handleFontSizeChange(e.target.value)}
                    className="w-full px-3 py-2 bg-surface border border-border rounded focus:ring-2 focus:ring-primary"
                    aria-describedby="font-size-help"
                  >
                    <option value="normal">Normal</option>
                    <option value="large">Large</option>
                    <option value="larger">Extra Large</option>
                  </select>
                  <p id="font-size-help" className="text-xs text-text-tertiary mt-1">
                    Adjust text size for better readability
                  </p>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <label 
                      htmlFor="high-contrast"
                      className="text-sm font-medium text-text-secondary"
                    >
                      High Contrast Mode
                    </label>
                    <p className="text-xs text-text-tertiary">
                      Increase color contrast for better visibility
                    </p>
                  </div>
                  <button
                    id="high-contrast"
                    role="switch"
                    aria-checked={isHighContrast}
                    onClick={toggleHighContrast}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 ${
                      isHighContrast ? 'bg-primary' : 'bg-gray-300'
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        isHighContrast ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>
              </div>
            </section>

            {/* Motion Settings */}
            <section>
              <h3 className="text-lg font-semibold text-text-primary mb-3 flex items-center gap-2">
                <Palette className="w-4 h-4" aria-hidden="true" />
                Motion
              </h3>
              
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-text-secondary">
                    Reduced Motion
                  </p>
                  <p className="text-xs text-text-tertiary">
                    {prefersReducedMotion ? 'Enabled by system preferences' : 'Disabled'}
                  </p>
                </div>
                <div className={`px-3 py-1 rounded text-xs font-medium ${
                  prefersReducedMotion 
                    ? 'bg-accent-success/20 text-accent-success'
                    : 'bg-surface text-text-tertiary'
                }`}>
                  {prefersReducedMotion ? 'Active' : 'Inactive'}
                </div>
              </div>
            </section>

            {/* Audio Settings */}
            <section>
              <h3 className="text-lg font-semibold text-text-primary mb-3 flex items-center gap-2">
                <Volume2 className="w-4 h-4" aria-hidden="true" />
                Audio
              </h3>
              
              <div className="flex items-center justify-between">
                <div>
                  <label 
                    htmlFor="sound-feedback"
                    className="text-sm font-medium text-text-secondary"
                  >
                    Sound Feedback
                  </label>
                  <p className="text-xs text-text-tertiary">
                    Play sounds for UI interactions and notifications
                  </p>
                </div>
                <button
                  id="sound-feedback"
                  role="switch"
                  aria-checked={soundEnabled}
                  onClick={() => setSoundEnabled(!soundEnabled)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 ${
                    soundEnabled ? 'bg-primary' : 'bg-gray-300'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      soundEnabled ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>
            </section>

            {/* Keyboard Navigation */}
            <section>
              <h3 className="text-lg font-semibold text-text-primary mb-3 flex items-center gap-2">
                <Keyboard className="w-4 h-4" aria-hidden="true" />
                Keyboard Navigation
              </h3>
              
              <button
                onClick={() => setKeyboardHelpVisible(!keyboardHelpVisible)}
                className="btn-secondary text-sm"
                aria-expanded={keyboardHelpVisible}
                aria-controls="keyboard-help"
              >
                {keyboardHelpVisible ? 'Hide' : 'Show'} Keyboard Shortcuts
              </button>
              
              {keyboardHelpVisible && (
                <div id="keyboard-help" className="mt-3 p-4 bg-surface/50 rounded border">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                    <div><kbd className="bg-gray-200 px-1 rounded">Tab</kbd> - Navigate forward</div>
                    <div><kbd className="bg-gray-200 px-1 rounded">Shift+Tab</kbd> - Navigate backward</div>
                    <div><kbd className="bg-gray-200 px-1 rounded">Enter</kbd> - Activate button/link</div>
                    <div><kbd className="bg-gray-200 px-1 rounded">Space</kbd> - Activate button/checkbox</div>
                    <div><kbd className="bg-gray-200 px-1 rounded">Esc</kbd> - Close modal/menu</div>
                    <div><kbd className="bg-gray-200 px-1 rounded">Arrow Keys</kbd> - Navigate menus</div>
                  </div>
                </div>
              )}
            </section>
          </div>

          <div className="flex gap-3 mt-6">
            <button
              onClick={saveSettings}
              className="btn-primary flex-1"
            >
              Save Settings
            </button>
            <button
              onClick={onClose}
              className="btn-secondary px-6"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>

      <LiveRegion announcement={announcement} />
    </>
  );
}
