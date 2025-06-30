import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown, 
  PieChart, 
  Activity,
  Download,
  Filter,
  Calendar,
  Users,
  DollarSign,
  ArrowUpRight,
  ArrowDownRight,
  Eye,
  FileSpreadsheet
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

interface DataVisualizationProps {
  readonly data?: any
  readonly analysisResults?: any[]
  readonly sessionId?: string
}

interface MetricCard {
  title: string
  value: string | number
  change: number
  trend: 'up' | 'down' | 'stable'
  icon: React.ComponentType<any>
  color: string
}

export function DataVisualization({ data, analysisResults, sessionId }: DataVisualizationProps) {
  const [selectedPeriod, setSelectedPeriod] = useState('7d')
  const [metrics, setMetrics] = useState<MetricCard[]>([])
  const [chartData, setChartData] = useState<any>(null)

  // Process analysis results into visualization data
  useEffect(() => {
    if (analysisResults && analysisResults.length > 0) {
      const latestAnalysis = analysisResults[analysisResults.length - 1]
      
      // Extract metrics from analysis
      const processedMetrics: MetricCard[] = [
        {
          title: 'Total Records',
          value: latestAnalysis.total_rows || '0',
          change: 12.5,
          trend: 'up',
          icon: FileSpreadsheet,
          color: 'blue'
        },
        {
          title: 'Data Quality Score',
          value: `${Math.round((latestAnalysis.quality_score || 0) * 100)}%`,
          change: 8.2,
          trend: 'up',
          icon: Activity,
          color: 'green'
        },
        {
          title: 'Missing Values',
          value: latestAnalysis.missing_values || '0',
          change: -15.3,
          trend: 'down',
          icon: TrendingDown,
          color: 'red'
        },
        {
          title: 'Unique Columns',
          value: latestAnalysis.column_count || '0',
          change: 5.1,
          trend: 'up',
          icon: BarChart3,
          color: 'purple'
        }
      ]
      
      setMetrics(processedMetrics)
      
      // Generate chart data
      if (latestAnalysis.column_analysis) {
        const chartDataProcessed = {
          columns: Object.keys(latestAnalysis.column_analysis),
          values: Object.values(latestAnalysis.column_analysis).map((col: any) => col.non_null_count || 0)
        }
        setChartData(chartDataProcessed)
      }
    }
  }, [analysisResults])

  const periods = [
    { label: '7 Days', value: '7d' },
    { label: '30 Days', value: '30d' },
    { label: '90 Days', value: '90d' },
    { label: 'All Time', value: 'all' }
  ]

  return (
    <div className="space-y-6">
      {/* Header Controls */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Data Insights</h2>
          <p className="text-muted-foreground">Real-time analytics and visualization</p>
        </div>
        
        <div className="flex items-center gap-3">
          {/* Time Period Selector */}
          <div className="flex items-center gap-1 bg-muted rounded-lg p-1">
            {periods.map((period) => (
              <Button
                key={period.value}
                variant={selectedPeriod === period.value ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setSelectedPeriod(period.value)}
                className="h-8"
              >
                {period.label}
              </Button>
            ))}
          </div>
          
          <Button variant="outline" size="sm">
            <Filter className="w-4 h-4 mr-2" />
            Filter
          </Button>
          
          <Button variant="outline" size="sm">
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Metrics Grid */}
      {metrics.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {metrics.map((metric, index) => (
            <motion.div
              key={metric.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
            >
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className={`p-2 rounded-lg bg-${metric.color}-100 dark:bg-${metric.color}-900/20`}>
                      <metric.icon className={`w-5 h-5 text-${metric.color}-600 dark:text-${metric.color}-400`} />
                    </div>
                    <Badge 
                      variant={metric.trend === 'up' ? 'default' : metric.trend === 'down' ? 'destructive' : 'secondary'}
                      className="flex items-center gap-1"
                    >
                      {metric.trend === 'up' ? (
                        <ArrowUpRight className="w-3 h-3" />
                      ) : metric.trend === 'down' ? (
                        <ArrowDownRight className="w-3 h-3" />
                      ) : null}
                      {Math.abs(metric.change)}%
                    </Badge>
                  </div>
                  
                  <div className="mt-4">
                    <div className="text-2xl font-bold">{metric.value}</div>
                    <div className="text-sm text-muted-foreground">{metric.title}</div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      )}

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Column Distribution Chart */}
        {chartData && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                Column Data Distribution
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {chartData.columns.map((column: string, index: number) => (
                  <div key={column} className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="font-medium">{column}</span>
                      <span className="text-muted-foreground">{chartData.values[index]}</span>
                    </div>
                    <div className="w-full bg-muted rounded-full h-2">
                      <motion.div
                        className="bg-blue-500 h-2 rounded-full"
                        initial={{ width: 0 }}
                        animate={{ 
                          width: `${(chartData.values[index] / Math.max(...chartData.values)) * 100}%` 
                        }}
                        transition={{ duration: 0.8, delay: index * 0.1 }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Analysis History */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5" />
              Analysis History
            </CardTitle>
          </CardHeader>
          <CardContent>
            {analysisResults && analysisResults.length > 0 ? (
              <div className="space-y-4">
                {analysisResults.slice(-5).reverse().map((analysis, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                    className="flex items-center justify-between p-3 bg-muted rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-2 h-2 bg-green-500 rounded-full" />
                      <div>
                        <div className="font-medium text-sm">Data Analysis Complete</div>
                        <div className="text-xs text-muted-foreground">
                          {analysis.filename || 'Unknown file'}
                        </div>
                      </div>
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {new Date(analysis.timestamp || Date.now()).toLocaleDateString()}
                    </div>
                  </motion.div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <PieChart className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <p className="font-medium mb-2">No analysis data available</p>
                <p className="text-sm">Upload and analyze data to see insights</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Detailed Analysis Results */}
      {analysisResults && analysisResults.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Eye className="w-5 h-5" />
              Latest Analysis Details
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {analysisResults.slice(-1).map((analysis, index) => (
                <div key={index} className="space-y-4">
                  {/* Summary Stats */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-muted rounded-lg">
                    <div className="text-center">
                      <div className="text-lg font-bold text-blue-600">
                        {analysis.total_rows || 'N/A'}
                      </div>
                      <div className="text-sm text-muted-foreground">Total Rows</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold text-green-600">
                        {analysis.column_count || 'N/A'}
                      </div>
                      <div className="text-sm text-muted-foreground">Columns</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold text-purple-600">
                        {analysis.memory_usage || 'N/A'}
                      </div>
                      <div className="text-sm text-muted-foreground">Memory Usage</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold text-orange-600">
                        {analysis.quality_score ? `${Math.round(analysis.quality_score * 100)}%` : 'N/A'}
                      </div>
                      <div className="text-sm text-muted-foreground">Quality Score</div>
                    </div>
                  </div>

                  {/* Raw Analysis Data */}
                  <details className="group">
                    <summary className="cursor-pointer flex items-center gap-2 font-medium hover:text-blue-600">
                      <ArrowUpRight className="w-4 h-4 transition-transform group-open:rotate-90" />
                      View Raw Analysis Data
                    </summary>
                    <div className="mt-3 p-4 bg-gray-50 dark:bg-gray-900 rounded-lg overflow-auto">
                      <pre className="text-xs whitespace-pre-wrap">
                        {JSON.stringify(analysis, null, 2)}
                      </pre>
                    </div>
                  </details>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Empty State */}
      {(!analysisResults || analysisResults.length === 0) && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16 text-center">
            <BarChart3 className="w-24 h-24 text-muted-foreground mb-6 opacity-50" />
            <h3 className="text-xl font-semibold mb-2">No Data to Visualize</h3>
            <p className="text-muted-foreground mb-6 max-w-md">
              Upload and analyze your data files to see beautiful charts, insights, and analytics here.
            </p>
            <div className="flex gap-3">
              <Button variant="default">
                <Upload className="w-4 h-4 mr-2" />
                Upload Data
              </Button>
              <Button variant="outline">
                <Activity className="w-4 h-4 mr-2" />
                Run Analysis
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
