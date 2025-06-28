'use client';

import {
  Database, FileText, Settings, MessageCircle, BarChart,
  Lightbulb, TrendingUp, Wand2, Users, BookOpen, User, ChevronDown
} from "lucide-react";

interface Agent {
  icon: React.ReactNode;
  name: string;
  status: 'idle' | 'processing' | 'complete' | 'error';
  description: string;
}

const agentList: Agent[] = [
  { 
    icon: <Database size={20} />, 
    name: "Data Agent",
    status: 'idle',
    description: "Handles data ingestion and preprocessing"
  },
  { 
    icon: <FileText size={20} />, 
    name: "Cleaner Agent",
    status: 'idle',
    description: "Cleans and validates data quality"
  },
  { 
    icon: <Settings size={20} />, 
    name: "Planning Agent",
    status: 'idle',
    description: "Plans analysis workflow and strategy"
  },
  { 
    icon: <MessageCircle size={20} />, 
    name: "Query Agent",
    status: 'idle',
    description: "Processes natural language queries"
  },
  { 
    icon: <BarChart size={20} />, 
    name: "SQL Agent",
    status: 'idle',
    description: "Executes SQL queries and data retrieval"
  },
  { 
    icon: <Lightbulb size={20} />, 
    name: "Insight Agent",
    status: 'idle',
    description: "Generates insights and recommendations"
  },
  { 
    icon: <TrendingUp size={20} />, 
    name: "Chart Agent",
    status: 'idle',
    description: "Creates visualizations and charts"
  },
  { 
    icon: <Wand2 size={20} />, 
    name: "Critique Agent",
    status: 'idle',
    description: "Reviews and validates analysis results"
  },
  { 
    icon: <Users size={20} />, 
    name: "Debate Agent",
    status: 'idle',
    description: "Facilitates multi-perspective analysis"
  },
  { 
    icon: <BookOpen size={20} />, 
    name: "Narrative Agent",
    status: 'idle',
    description: "Generates narrative summaries"
  },
  { 
    icon: <User size={20} />, 
    name: "Report Agent",
    status: 'idle',
    description: "Compiles final reports and documentation"
  },
];

const getStatusColor = (status: Agent['status']) => {
  switch (status) {
    case 'processing':
      return 'text-accent-primary border-accent-primary/30 bg-accent-primary/10';
    case 'complete':
      return 'text-accent-tertiary border-accent-tertiary/30 bg-accent-tertiary/10';
    case 'error':
      return 'text-accent-error border-accent-error/30 bg-accent-error/10';
    default:
      return 'text-text-secondary border-glass-border bg-glass-bg';
  }
};

const getStatusDot = (status: Agent['status']) => {
  switch (status) {
    case 'processing':
      return 'bg-accent-primary animate-pulse';
    case 'complete':
      return 'bg-accent-tertiary';
    case 'error':
      return 'bg-accent-error';
    default:
      return 'bg-text-muted';
  }
};

export default function AgentList() {
  return (
    <div className="flex flex-col gap-3">
      {agentList.map(({ icon, name, status, description }) => (
        <div
          key={name}
          className={`flex items-center justify-between p-4 rounded-xl border transition-all duration-300 cursor-pointer hover:transform hover:scale-[1.02] group ${getStatusColor(status)}`}
        >
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-glass-bg border border-glass-border">
              {icon}
            </div>
            <div className="flex flex-col">
              <div className="flex items-center gap-2">
                <span className="font-medium text-sm">{name}</span>
                <div className={`w-2 h-2 rounded-full ${getStatusDot(status)}`} />
              </div>
              <span className="text-xs text-text-muted group-hover:text-text-secondary transition-colors">
                {description}
              </span>
            </div>
          </div>
          <ChevronDown className="w-4 h-4 text-text-muted group-hover:text-text-secondary transition-all duration-300 group-hover:rotate-180" />
        </div>
      ))}
    </div>
  );
}
