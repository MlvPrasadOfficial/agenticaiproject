'use client';

import React, { useState, useRef, useEffect } from 'react';
import { motion, Reorder, AnimatePresence } from 'framer-motion';
import { 
  GripVertical, 
  Play, 
  Pause, 
  Square, 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  MoreVertical,
  Edit3,
  Trash2,
  Copy,
  ArrowUp,
  ArrowDown,
  Zap,
  Calendar,
  User,
  Tag
} from 'lucide-react';

interface TaskQueueItem {
  id: string;
  title: string;
  description?: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'pending' | 'running' | 'completed' | 'failed' | 'paused';
  agentId?: string;
  agentName?: string;
  estimatedDuration?: number;
  actualDuration?: number;
  progress?: number;
  dependencies?: string[];
  tags?: string[];
  createdAt: Date;
  scheduledAt?: Date;
  completedAt?: Date;
  metadata?: Record<string, any>;
}

interface AgentTaskQueueProps {
  tasks: TaskQueueItem[];
  onTasksReorder?: (newOrder: TaskQueueItem[]) => void;
  onTaskStart?: (taskId: string) => void;
  onTaskPause?: (taskId: string) => void;
  onTaskStop?: (taskId: string) => void;
  onTaskEdit?: (taskId: string) => void;
  onTaskDelete?: (taskId: string) => void;
  onTaskDuplicate?: (taskId: string) => void;
  onTaskPriorityChange?: (taskId: string, priority: TaskQueueItem['priority']) => void;
  className?: string;
  allowReordering?: boolean;
  showProgress?: boolean;
  groupBy?: 'none' | 'status' | 'priority' | 'agent';
}

export function AgentTaskQueue({
  tasks,
  onTasksReorder,
  onTaskStart,
  onTaskPause,
  onTaskStop,
  onTaskEdit,
  onTaskDelete,
  onTaskDuplicate,
  onTaskPriorityChange,
  className = '',
  allowReordering = true,
  showProgress = true,
  groupBy = 'none'
}: AgentTaskQueueProps) {
  const [selectedTask, setSelectedTask] = useState<string | null>(null);
  const [filter, setFilter] = useState<TaskQueueItem['status'] | 'all'>('all');
  const [draggedTask, setDraggedTask] = useState<string | null>(null);
  const constraintsRef = useRef<HTMLDivElement>(null);

  const getPriorityColor = (priority: TaskQueueItem['priority']) => {
    switch (priority) {
      case 'urgent':
        return 'bg-red-100 text-red-800 border-red-200 dark:bg-red-900/20 dark:text-red-300 dark:border-red-800';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200 dark:bg-orange-900/20 dark:text-orange-300 dark:border-orange-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200 dark:bg-yellow-900/20 dark:text-yellow-300 dark:border-yellow-800';
      case 'low':
        return 'bg-gray-100 text-gray-800 border-gray-200 dark:bg-gray-900/20 dark:text-gray-300 dark:border-gray-800';
    }
  };

  const getStatusColor = (status: TaskQueueItem['status']) => {
    switch (status) {
      case 'pending':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300';
      case 'running':
        return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300';
      case 'completed':
        return 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/20 dark:text-emerald-300';
      case 'failed':
        return 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300';
      case 'paused':
        return 'bg-amber-100 text-amber-800 dark:bg-amber-900/20 dark:text-amber-300';
    }
  };

  const getStatusIcon = (status: TaskQueueItem['status']) => {
    switch (status) {
      case 'pending':
        return <Clock className="w-4 h-4" />;
      case 'running':
        return <Play className="w-4 h-4" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4" />;
      case 'failed':
        return <AlertCircle className="w-4 h-4" />;
      case 'paused':
        return <Pause className="w-4 h-4" />;
    }
  };

  const filteredTasks = tasks.filter(task => 
    filter === 'all' || task.status === filter
  );

  const groupedTasks = React.useMemo(() => {
    if (groupBy === 'none') {
      return { 'All Tasks': filteredTasks };
    }

    return filteredTasks.reduce((groups, task) => {
      let key: string;
      switch (groupBy) {
        case 'status':
          key = task.status.charAt(0).toUpperCase() + task.status.slice(1);
          break;
        case 'priority':
          key = task.priority.charAt(0).toUpperCase() + task.priority.slice(1);
          break;
        case 'agent':
          key = task.agentName || 'Unassigned';
          break;
        default:
          key = 'All Tasks';
      }
      
      if (!groups[key]) {
        groups[key] = [];
      }
      groups[key].push(task);
      return groups;
    }, {} as Record<string, TaskQueueItem[]>);
  }, [filteredTasks, groupBy]);

  const handleTaskAction = (taskId: string, action: string) => {
    switch (action) {
      case 'start':
        onTaskStart?.(taskId);
        break;
      case 'pause':
        onTaskPause?.(taskId);
        break;
      case 'stop':
        onTaskStop?.(taskId);
        break;
      case 'edit':
        onTaskEdit?.(taskId);
        break;
      case 'delete':
        onTaskDelete?.(taskId);
        break;
      case 'duplicate':
        onTaskDuplicate?.(taskId);
        break;
    }
  };

  const renderTaskActions = (task: TaskQueueItem) => {
    return (
      <div className="flex items-center gap-1">
        {/* Primary Actions */}
        {task.status === 'pending' && (
          <button
            onClick={() => handleTaskAction(task.id, 'start')}
            className="p-1.5 hover:bg-green-100 dark:hover:bg-green-900/20 rounded transition-colors"
            title="Start task"
          >
            <Play className="w-4 h-4 text-green-600" />
          </button>
        )}
        
        {task.status === 'running' && (
          <>
            <button
              onClick={() => handleTaskAction(task.id, 'pause')}
              className="p-1.5 hover:bg-yellow-100 dark:hover:bg-yellow-900/20 rounded transition-colors"
              title="Pause task"
            >
              <Pause className="w-4 h-4 text-yellow-600" />
            </button>
            <button
              onClick={() => handleTaskAction(task.id, 'stop')}
              className="p-1.5 hover:bg-red-100 dark:hover:bg-red-900/20 rounded transition-colors"
              title="Stop task"
            >
              <Square className="w-4 h-4 text-red-600" />
            </button>
          </>
        )}

        {task.status === 'paused' && (
          <button
            onClick={() => handleTaskAction(task.id, 'start')}
            className="p-1.5 hover:bg-green-100 dark:hover:bg-green-900/20 rounded transition-colors"
            title="Resume task"
          >
            <Play className="w-4 h-4 text-green-600" />
          </button>
        )}

        {/* More Actions Menu */}
        <div className="relative group">
          <button className="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors">
            <MoreVertical className="w-4 h-4 text-gray-500" />
          </button>
          
          <div className="absolute right-0 top-full mt-1 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-10">
            <div className="py-1">
              <button
                onClick={() => handleTaskAction(task.id, 'edit')}
                className="w-full px-3 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
              >
                <Edit3 className="w-4 h-4" />
                Edit Task
              </button>
              <button
                onClick={() => handleTaskAction(task.id, 'duplicate')}
                className="w-full px-3 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
              >
                <Copy className="w-4 h-4" />
                Duplicate
              </button>
              <div className="border-t border-gray-200 dark:border-gray-700 my-1" />
              <button
                onClick={() => handleTaskAction(task.id, 'delete')}
                className="w-full px-3 py-2 text-left text-sm hover:bg-red-50 dark:hover:bg-red-900/20 text-red-600 dark:text-red-400 flex items-center gap-2"
              >
                <Trash2 className="w-4 h-4" />
                Delete Task
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderTaskItem = (task: TaskQueueItem, index: number) => {
    const isSelected = selectedTask === task.id;
    const isDragging = draggedTask === task.id;

    return (
      <motion.div
        layout
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.2 }}
        className={`
          bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700
          hover:border-blue-300 dark:hover:border-blue-600 transition-all duration-200
          ${isSelected ? 'ring-2 ring-blue-500 border-blue-300 dark:border-blue-600' : ''}
          ${isDragging ? 'shadow-lg scale-105' : 'shadow-sm'}
        `}
        onClick={() => setSelectedTask(isSelected ? null : task.id)}
      >
        <div className="p-4">
          <div className="flex items-start gap-3">
            {/* Drag Handle */}
            {allowReordering && (
              <div 
                className="cursor-grab active:cursor-grabbing mt-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                onMouseDown={() => setDraggedTask(task.id)}
                onMouseUp={() => setDraggedTask(null)}
              >
                <GripVertical className="w-4 h-4" />
              </div>
            )}

            {/* Task Content */}
            <div className="flex-1 min-w-0">
              {/* Header */}
              <div className="flex items-start justify-between gap-3 mb-2">
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 dark:text-gray-100 text-sm">
                    {task.title}
                  </h3>
                  {task.description && (
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      {task.description}
                    </p>
                  )}
                </div>
                
                {renderTaskActions(task)}
              </div>

              {/* Metadata */}
              <div className="flex flex-wrap items-center gap-2 mb-3">
                {/* Status */}
                <div className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(task.status)}`}>
                  {getStatusIcon(task.status)}
                  {task.status}
                </div>

                {/* Priority */}
                <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getPriorityColor(task.priority)}`}>
                  {task.priority}
                </div>

                {/* Agent */}
                {task.agentName && (
                  <div className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
                    <User className="w-3 h-3" />
                    {task.agentName}
                  </div>
                )}

                {/* Duration */}
                {task.estimatedDuration && (
                  <div className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
                    <Clock className="w-3 h-3" />
                    ~{Math.round(task.estimatedDuration / 1000)}s
                  </div>
                )}
              </div>

              {/* Progress Bar */}
              {showProgress && task.status === 'running' && task.progress !== undefined && (
                <div className="mb-3">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-xs text-gray-600 dark:text-gray-400">Progress</span>
                    <span className="text-xs text-gray-600 dark:text-gray-400">{Math.round(task.progress)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <motion.div
                      className="bg-blue-500 h-2 rounded-full"
                      initial={{ width: 0 }}
                      animate={{ width: `${task.progress}%` }}
                      transition={{ duration: 0.5 }}
                    />
                  </div>
                </div>
              )}

              {/* Tags */}
              {task.tags && task.tags.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-3">
                  {task.tags.map(tag => (
                    <div
                      key={tag}
                      className="inline-flex items-center gap-1 px-2 py-1 rounded text-xs bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300"
                    >
                      <Tag className="w-3 h-3" />
                      {tag}
                    </div>
                  ))}
                </div>
              )}

              {/* Timestamps */}
              <div className="text-xs text-gray-500 dark:text-gray-400 space-y-1">
                <div className="flex items-center gap-4">
                  <span>Created: {task.createdAt.toLocaleString()}</span>
                  {task.scheduledAt && (
                    <span>Scheduled: {task.scheduledAt.toLocaleString()}</span>
                  )}
                </div>
                {task.completedAt && (
                  <div>Completed: {task.completedAt.toLocaleString()}</div>
                )}
              </div>

              {/* Dependencies */}
              {task.dependencies && task.dependencies.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                  <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Dependencies:</div>
                  <div className="flex flex-wrap gap-1">
                    {task.dependencies.map(depId => (
                      <span
                        key={depId}
                        className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded"
                      >
                        {depId}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </motion.div>
    );
  };

  const renderGroup = (groupName: string, groupTasks: TaskQueueItem[]) => {
    if (allowReordering && groupBy === 'none') {
      return (
        <Reorder.Group
          axis="y"
          values={groupTasks}
          onReorder={(newOrder) => onTasksReorder?.(newOrder)}
          className="space-y-3"
        >
          {groupTasks.map((task, index) => (
            <Reorder.Item
              key={task.id}
              value={task}
              className="cursor-grab active:cursor-grabbing"
            >
              {renderTaskItem(task, index)}
            </Reorder.Item>
          ))}
        </Reorder.Group>
      );
    }

    return (
      <div className="space-y-3">
        {groupTasks.map((task, index) => renderTaskItem(task, index))}
      </div>
    );
  };

  return (
    <div className={`space-y-6 ${className}`} ref={constraintsRef}>
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Task Queue
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            {tasks.length} tasks • {tasks.filter(t => t.status === 'running').length} running
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Filter */}
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as any)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
          >
            <option value="all">All Tasks</option>
            <option value="pending">Pending</option>
            <option value="running">Running</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
            <option value="paused">Paused</option>
          </select>

          {/* Group By */}
          <select
            value={groupBy}
            onChange={(e) => setGroupBy(e.target.value as any)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
          >
            <option value="none">No Grouping</option>
            <option value="status">Group by Status</option>
            <option value="priority">Group by Priority</option>
            <option value="agent">Group by Agent</option>
          </select>
        </div>
      </div>

      {/* Task Queue */}
      <AnimatePresence>
        {Object.entries(groupedTasks).map(([groupName, groupTasks]) => (
          <motion.div
            key={groupName}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-4"
          >
            {groupBy !== 'none' && (
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 border-b border-gray-200 dark:border-gray-700 pb-2">
                {groupName} ({groupTasks.length})
              </h3>
            )}
            
            {renderGroup(groupName, groupTasks)}
          </motion.div>
        ))}
      </AnimatePresence>

      {/* Empty State */}
      {filteredTasks.length === 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-12"
        >
          <div className="text-gray-400 dark:text-gray-600 mb-4">
            <Zap className="w-12 h-12 mx-auto" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
            No tasks found
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            {filter === 'all' ? 'The task queue is empty.' : `No ${filter} tasks found.`}
          </p>
        </motion.div>
      )}
    </div>
  );
}
