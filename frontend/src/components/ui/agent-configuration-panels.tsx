'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Settings, 
  ChevronDown, 
  ChevronRight, 
  Save, 
  RotateCcw, 
  Copy, 
  Eye, 
  EyeOff, 
  Info,
  AlertTriangle,
  Zap,
  Brain,
  Database,
  Clock
} from 'lucide-react';

interface AgentConfig {
  id: string;
  name: string;
  description: string;
  version: string;
  status: 'active' | 'inactive' | 'error';
  settings: {
    general: {
      enabled: boolean;
      priority: number;
      maxConcurrentTasks: number;
      timeout: number;
      retryAttempts: number;
    };
    llm: {
      model: string;
      temperature: number;
      maxTokens: number;
      topP: number;
      frequencyPenalty: number;
      presencePenalty: number;
    };
    memory: {
      enabled: boolean;
      maxSize: number;
      persistentStorage: boolean;
      compressionThreshold: number;
    };
    performance: {
      caching: boolean;
      parallelProcessing: boolean;
      optimizeForSpeed: boolean;
      logLevel: 'debug' | 'info' | 'warn' | 'error';
    };
    security: {
      encryptData: boolean;
      sanitizeInputs: boolean;
      restrictedModes: string[];
      maxRequestSize: number;
    };
  };
  capabilities: string[];
  dependencies: string[];
  lastModified: Date;
}

interface AgentConfigurationPanelsProps {
  agents: AgentConfig[];
  onUpdateConfig?: (agentId: string, config: AgentConfig['settings']) => void;
  onSaveConfig?: (agentId: string) => void;
  onResetConfig?: (agentId: string) => void;
  className?: string;
}

export function AgentConfigurationPanels({
  agents,
  onUpdateConfig,
  onSaveConfig,
  onResetConfig,
  className = ''
}: AgentConfigurationPanelsProps) {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({});
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState<Record<string, boolean>>({});
  const [showSensitiveData, setShowSensitiveData] = useState<Record<string, boolean>>({});

  const toggleSection = (sectionId: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [sectionId]: !prev[sectionId]
    }));
  };

  const handleConfigChange = (agentId: string, section: string, field: string, value: any) => {
    const agent = agents.find(a => a.id === agentId);
    if (!agent) return;

    const updatedSettings = {
      ...agent.settings,
      [section]: {
        ...agent.settings[section as keyof typeof agent.settings],
        [field]: value
      }
    };

    onUpdateConfig?.(agentId, updatedSettings);
    setHasUnsavedChanges(prev => ({ ...prev, [agentId]: true }));
  };

  const handleSave = (agentId: string) => {
    onSaveConfig?.(agentId);
    setHasUnsavedChanges(prev => ({ ...prev, [agentId]: false }));
  };

  const handleReset = (agentId: string) => {
    onResetConfig?.(agentId);
    setHasUnsavedChanges(prev => ({ ...prev, [agentId]: false }));
  };

  const renderConfigSection = (
    agent: AgentConfig,
    sectionKey: string,
    sectionName: string,
    icon: React.ReactNode,
    description?: string
  ) => {
    const sectionId = `${agent.id}-${sectionKey}`;
    const isExpanded = expandedSections[sectionId];
    const sectionData = agent.settings[sectionKey as keyof typeof agent.settings];

    return (
      <div key={sectionKey} className="border border-gray-200 dark:border-gray-700 rounded-lg">
        <button
          onClick={() => toggleSection(sectionId)}
          className="w-full p-4 flex items-center justify-between text-left hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
        >
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400">
              {icon}
            </div>
            <div>
              <h4 className="font-medium text-gray-900 dark:text-gray-100">{sectionName}</h4>
              {description && (
                <p className="text-sm text-gray-500 dark:text-gray-400">{description}</p>
              )}
            </div>
          </div>
          <motion.div
            animate={{ rotate: isExpanded ? 90 : 0 }}
            transition={{ duration: 0.2 }}
          >
            <ChevronRight className="w-4 h-4 text-gray-400" />
          </motion.div>
        </button>

        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="overflow-hidden border-t border-gray-200 dark:border-gray-700"
            >
              <div className="p-4 space-y-4 bg-gray-50 dark:bg-gray-800/50">
                {Object.entries(sectionData as Record<string, any>).map(([field, value]) => (
                  <div key={field} className="space-y-2">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 capitalize">
                      {field.replace(/([A-Z])/g, ' $1').toLowerCase()}
                    </label>
                    {renderConfigField(agent, sectionKey, field, value)}
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    );
  };

  const renderConfigField = (agent: AgentConfig, section: string, field: string, value: any) => {
    const fieldId = `${agent.id}-${section}-${field}`;
    const isSensitive = field.toLowerCase().includes('key') || field.toLowerCase().includes('token');

    if (typeof value === 'boolean') {
      return (
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={value}
            onChange={(e) => handleConfigChange(agent.id, section, field, e.target.checked)}
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <span className="text-sm text-gray-600 dark:text-gray-400">
            {value ? 'Enabled' : 'Disabled'}
          </span>
        </label>
      );
    }

    if (typeof value === 'number') {
      return (
        <div className="relative">
          <input
            type="number"
            value={value}
            onChange={(e) => handleConfigChange(agent.id, section, field, Number(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      );
    }

    if (typeof value === 'string') {
      if (field === 'logLevel') {
        return (
          <select
            value={value}
            onChange={(e) => handleConfigChange(agent.id, section, field, e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500"
          >
            <option value="debug">Debug</option>
            <option value="info">Info</option>
            <option value="warn">Warning</option>
            <option value="error">Error</option>
          </select>
        );
      }

      return (
        <div className="relative">
          <input
            type={isSensitive && !showSensitiveData[fieldId] ? 'password' : 'text'}
            value={value}
            onChange={(e) => handleConfigChange(agent.id, section, field, e.target.value)}
            className="w-full px-3 py-2 pr-10 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          {isSensitive && (
            <button
              onClick={() => setShowSensitiveData(prev => ({ ...prev, [fieldId]: !prev[fieldId] }))}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              {showSensitiveData[fieldId] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          )}
        </div>
      );
    }

    if (Array.isArray(value)) {
      return (
        <div className="space-y-2">
          {value.map((item, index) => (
            <div key={index} className="flex items-center gap-2">
              <input
                type="text"
                value={item}
                onChange={(e) => {
                  const newArray = [...value];
                  newArray[index] = e.target.value;
                  handleConfigChange(agent.id, section, field, newArray);
                }}
                className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={() => {
                  const newArray = value.filter((_, i) => i !== index);
                  handleConfigChange(agent.id, section, field, newArray);
                }}
                className="p-2 text-red-500 hover:bg-red-100 dark:hover:bg-red-900/20 rounded"
              >
                ×
              </button>
            </div>
          ))}
          <button
            onClick={() => {
              const newArray = [...value, ''];
              handleConfigChange(agent.id, section, field, newArray);
            }}
            className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
          >
            + Add item
          </button>
        </div>
      );
    }

    return (
      <div className="text-sm text-gray-500 dark:text-gray-400">
        Unsupported field type: {typeof value}
      </div>
    );
  };

  const renderAgentCard = (agent: AgentConfig) => {
    const isSelected = selectedAgent === agent.id;
    const hasChanges = hasUnsavedChanges[agent.id];

    return (
      <motion.div
        key={agent.id}
        layout
        className={`
          p-4 border rounded-lg cursor-pointer transition-all
          ${isSelected
            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
            : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
          }
        `}
        onClick={() => setSelectedAgent(isSelected ? null : agent.id)}
      >
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <h3 className="font-medium text-gray-900 dark:text-gray-100">{agent.name}</h3>
              <span className={`
                px-2 py-1 rounded-full text-xs font-medium
                ${agent.status === 'active'
                  ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                  : agent.status === 'error'
                  ? 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
                  : 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400'
                }
              `}>
                {agent.status}
              </span>
              {hasChanges && (
                <span className="w-2 h-2 bg-orange-500 rounded-full" title="Unsaved changes" />
              )}
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">{agent.description}</p>
            <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
              <span>v{agent.version}</span>
              <span>{agent.capabilities.length} capabilities</span>
              <span>{agent.dependencies.length} dependencies</span>
            </div>
          </div>
          <Settings className="w-5 h-5 text-gray-400" />
        </div>
      </motion.div>
    );
  };

  const selectedAgentData = agents.find(a => a.id === selectedAgent);

  return (
    <div className={`space-y-6 ${className}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Settings className="w-5 h-5 text-blue-600" />
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            Agent Configuration
          </h2>
        </div>
        {selectedAgent && hasUnsavedChanges[selectedAgent] && (
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-orange-500" />
            <span className="text-sm text-orange-600 dark:text-orange-400">
              Unsaved changes
            </span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Agent List */}
        <div className="space-y-3">
          <h3 className="font-medium text-gray-700 dark:text-gray-300">Select Agent</h3>
          {agents.map(agent => renderAgentCard(agent))}
        </div>

        {/* Configuration Panel */}
        <div className="lg:col-span-2">
          <AnimatePresence>
            {selectedAgentData ? (
              <motion.div
                key={selectedAgent}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="space-y-6"
              >
                {/* Header */}
                <div className="flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                      {selectedAgentData.name} Configuration
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Last modified: {selectedAgentData.lastModified.toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => selectedAgent && handleReset(selectedAgent)}
                      className="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                    >
                      <RotateCcw className="w-4 h-4 mr-1" />
                      Reset
                    </motion.button>
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => selectedAgent && handleSave(selectedAgent)}
                      disabled={!selectedAgent || !hasUnsavedChanges[selectedAgent]}
                      className={`
                        px-3 py-2 text-sm rounded-lg transition-colors
                        ${selectedAgent && hasUnsavedChanges[selectedAgent]
                          ? 'bg-blue-600 text-white hover:bg-blue-700'
                          : 'bg-gray-200 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed'
                        }
                      `}
                    >
                      <Save className="w-4 h-4 mr-1" />
                      Save
                    </motion.button>
                  </div>
                </div>

                {/* Configuration Sections */}
                <div className="space-y-4">
                  {renderConfigSection(
                    selectedAgentData,
                    'general',
                    'General Settings',
                    <Settings className="w-4 h-4" />,
                    'Basic configuration and behavior settings'
                  )}
                  {renderConfigSection(
                    selectedAgentData,
                    'llm',
                    'Language Model',
                    <Brain className="w-4 h-4" />,
                    'LLM parameters and generation settings'
                  )}
                  {renderConfigSection(
                    selectedAgentData,
                    'memory',
                    'Memory Management',
                    <Database className="w-4 h-4" />,
                    'Memory and storage configuration'
                  )}
                  {renderConfigSection(
                    selectedAgentData,
                    'performance',
                    'Performance',
                    <Zap className="w-4 h-4" />,
                    'Performance optimization settings'
                  )}
                  {renderConfigSection(
                    selectedAgentData,
                    'security',
                    'Security',
                    <AlertTriangle className="w-4 h-4" />,
                    'Security and access control settings'
                  )}
                </div>
              </motion.div>
            ) : (
              <div className="flex items-center justify-center h-64 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg">
                <div className="text-center">
                  <Settings className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-500 dark:text-gray-400">
                    Select an agent to configure its settings
                  </p>
                </div>
              </div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
