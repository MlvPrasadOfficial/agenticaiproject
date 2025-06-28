'use client'

import { useHealthCheck } from '@/hooks/api'
import { AlertCircle, CheckCircle, Loader2 } from 'lucide-react'

export function HealthIndicator() {
  const { data, isLoading, isError } = useHealthCheck()

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 text-gray-400">
        <Loader2 className="h-4 w-4 animate-spin" />
        <span className="text-sm">Checking system health...</span>
      </div>
    )
  }

  if (isError) {
    return (
      <div className="flex items-center gap-2 text-red-400">
        <AlertCircle className="h-4 w-4" />
        <span className="text-sm">System health check failed</span>
      </div>
    )
  }

  if (data) {
    const statusColor = {
      healthy: 'text-green-400',
      unhealthy: 'text-red-400',
      degraded: 'text-yellow-400',
    }[data.status]

    const StatusIcon = data.status === 'healthy' ? CheckCircle : AlertCircle

    return (
      <div className={`flex items-center gap-2 ${statusColor}`}>
        <StatusIcon className="h-4 w-4" />
        <span className="text-sm capitalize">
          System {data.status} • v{data.version}
        </span>
      </div>
    )
  }

  return null
}
