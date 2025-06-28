'use client';

import React, { useState } from 'react';
import { 
  Download, 
  Share2, 
  Copy, 
  Mail, 
  FileText, 
  Image, 
  FileSpreadsheet,
  Link,
  QrCode,
  Printer,
  CheckCircle,
  X,
  Eye,
  Settings
} from 'lucide-react';

interface ExportData {
  type: 'conversation' | 'analysis' | 'insight' | 'chart' | 'report';
  title: string;
  data: any;
  metadata?: {
    timestamp: Date;
    agentType?: string;
    sessionId?: string;
    fileId?: string;
  };
}

interface ExportSharingProps {
  data: ExportData;
  onExport: (format: string, options: any) => Promise<void>;
  onShare: (method: string, options: any) => Promise<void>;
  className?: string;
  isOpen: boolean;
  onClose: () => void;
}

export default function ExportSharing({
  data,
  onExport,
  onShare,
  className = '',
  isOpen,
  onClose
}: ExportSharingProps) {
  const [activeTab, setActiveTab] = useState<'export' | 'share'>('export');
  const [selectedFormat, setSelectedFormat] = useState('pdf');
  const [selectedMethod, setSelectedMethod] = useState('link');
  const [exportOptions, setExportOptions] = useState({
    includeMetadata: true,
    includeTimestamp: true,
    includeCharts: true,
    includeRawData: false,
    format: 'standard',
    quality: 'high'
  });
  const [shareOptions, setShareOptions] = useState({
    expiration: '7days',
    password: '',
    allowDownload: true,
    allowComments: false,
    publicAccess: false
  });
  const [isProcessing, setIsProcessing] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const exportFormats = [
    { id: 'pdf', name: 'PDF Document', icon: FileText, description: 'Professional report format' },
    { id: 'excel', name: 'Excel Spreadsheet', icon: FileSpreadsheet, description: 'Data analysis format' },
    { id: 'png', name: 'PNG Image', icon: Image, description: 'High quality image' },
    { id: 'csv', name: 'CSV Data', icon: FileSpreadsheet, description: 'Raw data format' },
    { id: 'json', name: 'JSON Data', icon: FileText, description: 'Structured data format' }
  ];

  const shareeMethods = [
    { id: 'link', name: 'Share Link', icon: Link, description: 'Generate shareable URL' },
    { id: 'email', name: 'Email', icon: Mail, description: 'Send via email' },
    { id: 'qr', name: 'QR Code', icon: QrCode, description: 'Generate QR code' },
    { id: 'embed', name: 'Embed Code', icon: Copy, description: 'HTML embed code' }
  ];

  const handleExport = async () => {
    setIsProcessing(true);
    setError('');
    
    try {
      await onExport(selectedFormat, {
        ...exportOptions,
        filename: `${data.title}-${Date.now()}`
      });
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError('Export failed. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleShare = async () => {
    setIsProcessing(true);
    setError('');
    
    try {
      await onShare(selectedMethod, {
        ...shareOptions,
        data: data,
        format: selectedFormat
      });
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError('Sharing failed. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleCopyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 2000);
    } catch (err) {
      setError('Failed to copy to clipboard');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className={`bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden ${className}`}>
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Export & Share</h2>
            <p className="text-sm text-gray-600 mt-1">{data.title}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-gray-200">
          <button
            onClick={() => setActiveTab('export')}
            className={`flex-1 px-6 py-3 text-sm font-medium transition-colors ${
              activeTab === 'export'
                ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <Download className="w-4 h-4 inline mr-2" />
            Export
          </button>
          <button
            onClick={() => setActiveTab('share')}
            className={`flex-1 px-6 py-3 text-sm font-medium transition-colors ${
              activeTab === 'share'
                ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <Share2 className="w-4 h-4 inline mr-2" />
            Share
          </button>
        </div>

        {/* Content */}
        <div className="p-6 max-h-96 overflow-y-auto">
          {activeTab === 'export' ? (
            <div className="space-y-6">
              {/* Format Selection */}
              <div>
                <h3 className="text-sm font-medium text-gray-900 mb-3">Select Format</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {exportFormats.map((format) => (
                    <button
                      key={format.id}
                      onClick={() => setSelectedFormat(format.id)}
                      className={`flex items-center gap-3 p-3 border rounded-lg transition-colors text-left ${
                        selectedFormat === format.id
                          ? 'border-blue-500 bg-blue-50 text-blue-700'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <format.icon className="w-5 h-5" />
                      <div>
                        <div className="font-medium">{format.name}</div>
                        <div className="text-xs text-gray-500">{format.description}</div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Export Options */}
              <div>
                <h3 className="text-sm font-medium text-gray-900 mb-3">Export Options</h3>
                <div className="space-y-3">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={exportOptions.includeMetadata}
                      onChange={(e) => setExportOptions(prev => ({
                        ...prev,
                        includeMetadata: e.target.checked
                      }))}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700">Include metadata</span>
                  </label>
                  
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={exportOptions.includeTimestamp}
                      onChange={(e) => setExportOptions(prev => ({
                        ...prev,
                        includeTimestamp: e.target.checked
                      }))}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700">Include timestamp</span>
                  </label>
                  
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={exportOptions.includeCharts}
                      onChange={(e) => setExportOptions(prev => ({
                        ...prev,
                        includeCharts: e.target.checked
                      }))}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700">Include charts and visualizations</span>
                  </label>
                  
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={exportOptions.includeRawData}
                      onChange={(e) => setExportOptions(prev => ({
                        ...prev,
                        includeRawData: e.target.checked
                      }))}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700">Include raw data</span>
                  </label>
                </div>
              </div>

              {/* Quality Settings */}
              {(selectedFormat === 'png' || selectedFormat === 'pdf') && (
                <div>
                  <h3 className="text-sm font-medium text-gray-900 mb-3">Quality</h3>
                  <select
                    value={exportOptions.quality}
                    onChange={(e) => setExportOptions(prev => ({
                      ...prev,
                      quality: e.target.value
                    }))}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="low">Low (Smaller file)</option>
                    <option value="medium">Medium</option>
                    <option value="high">High (Larger file)</option>
                  </select>
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-6">
              {/* Sharing Method */}
              <div>
                <h3 className="text-sm font-medium text-gray-900 mb-3">Sharing Method</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {shareeMethods.map((method) => (
                    <button
                      key={method.id}
                      onClick={() => setSelectedMethod(method.id)}
                      className={`flex items-center gap-3 p-3 border rounded-lg transition-colors text-left ${
                        selectedMethod === method.id
                          ? 'border-blue-500 bg-blue-50 text-blue-700'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <method.icon className="w-5 h-5" />
                      <div>
                        <div className="font-medium">{method.name}</div>
                        <div className="text-xs text-gray-500">{method.description}</div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Share Options */}
              <div>
                <h3 className="text-sm font-medium text-gray-900 mb-3">Sharing Options</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm text-gray-700 mb-1">Expiration</label>
                    <select
                      value={shareOptions.expiration}
                      onChange={(e) => setShareOptions(prev => ({
                        ...prev,
                        expiration: e.target.value
                      }))}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="1hour">1 Hour</option>
                      <option value="1day">1 Day</option>
                      <option value="7days">7 Days</option>
                      <option value="30days">30 Days</option>
                      <option value="never">Never</option>
                    </select>
                  </div>

                  {selectedMethod === 'link' && (
                    <div>
                      <label className="block text-sm text-gray-700 mb-1">Password (Optional)</label>
                      <input
                        type="password"
                        value={shareOptions.password}
                        onChange={(e) => setShareOptions(prev => ({
                          ...prev,
                          password: e.target.value
                        }))}
                        placeholder="Enter password for protected access"
                        className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  )}

                  <div className="space-y-2">
                    <label className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={shareOptions.allowDownload}
                        onChange={(e) => setShareOptions(prev => ({
                          ...prev,
                          allowDownload: e.target.checked
                        }))}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-sm text-gray-700">Allow download</span>
                    </label>
                    
                    <label className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={shareOptions.allowComments}
                        onChange={(e) => setShareOptions(prev => ({
                          ...prev,
                          allowComments: e.target.checked
                        }))}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-sm text-gray-700">Allow comments</span>
                    </label>
                    
                    <label className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={shareOptions.publicAccess}
                        onChange={(e) => setShareOptions(prev => ({
                          ...prev,
                          publicAccess: e.target.checked
                        }))}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-sm text-gray-700">Public access (no login required)</span>
                    </label>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-gray-200 bg-gray-50">
          {success && (
            <div className="flex items-center gap-2 text-green-600">
              <CheckCircle className="w-4 h-4" />
              <span className="text-sm">
                {activeTab === 'export' ? 'Exported successfully!' : 'Shared successfully!'}
              </span>
            </div>
          )}
          
          {error && (
            <div className="text-red-600 text-sm">{error}</div>
          )}
          
          <div className="flex items-center gap-3 ml-auto">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={activeTab === 'export' ? handleExport : handleShare}
              disabled={isProcessing}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              {isProcessing ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  {activeTab === 'export' ? (
                    <>
                      <Download className="w-4 h-4" />
                      Export
                    </>
                  ) : (
                    <>
                      <Share2 className="w-4 h-4" />
                      Share
                    </>
                  )}
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export type { ExportData };
