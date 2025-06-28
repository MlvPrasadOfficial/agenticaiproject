/**
 * Data Statistics Dashboard Component
 * Task 55: Create data statistics dashboard (charts, metrics, data quality indicators)
 */

'use client';

import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { BarChart3, PieChart, TrendingUp, Database, AlertTriangle, CheckCircle, Activity } from 'lucide-react';

interface DataStatistics {
  total_records: number;
  total_columns: number;
  missing_values_percentage: number;
  data_types: Record<string, number>;
  quality_score: number;
  outliers_detected: number;
  duplicate_records: number;
  column_statistics: Record<string, {
    mean?: number;
    median?: number;
    std?: number;
    min?: number;
    max?: number;
    unique_values?: number;
    null_count: number;
  }>;
}

interface DataStatisticsDashboardProps {
  fileId: string;
  statistics?: DataStatistics;
  loading?: boolean;
}

export default function DataStatisticsDashboard({ fileId, statistics, loading }: DataStatisticsDashboardProps) {
  const barChartRef = useRef<SVGSVGElement>(null);
  const pieChartRef = useRef<SVGSVGElement>(null);
  const qualityChartRef = useRef<SVGSVGElement>(null);

  // Sample data if no statistics provided
  const mockStatistics: DataStatistics = statistics || {
    total_records: 1250,
    total_columns: 8,
    missing_values_percentage: 5.2,
    data_types: {
      'numeric': 4,
      'text': 3,
      'date': 1
    },
    quality_score: 87.5,
    outliers_detected: 12,
    duplicate_records: 3,
    column_statistics: {
      'revenue': { mean: 15420, median: 12300, std: 8940, min: 1200, max: 45600, null_count: 5 },
      'customer_id': { unique_values: 1247, null_count: 0 },
      'date': { unique_values: 365, null_count: 2 },
      'category': { unique_values: 12, null_count: 8 }
    }
  };

  // Create bar chart for data types
  useEffect(() => {
    if (!barChartRef.current || loading) return;

    const svg = d3.select(barChartRef.current);
    svg.selectAll('*').remove();

    const margin = { top: 20, right: 20, bottom: 40, left: 50 };
    const width = 300 - margin.left - margin.right;
    const height = 200 - margin.bottom - margin.top;

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const data = Object.entries(mockStatistics.data_types);
    
    const x = d3.scaleBand()
      .domain(data.map(d => d[0]))
      .range([0, width])
      .padding(0.1);

    const y = d3.scaleLinear()
      .domain([0, d3.max(data, d => d[1]) || 0])
      .range([height, 0]);

    // Add bars
    g.selectAll('.bar')
      .data(data)
      .enter().append('rect')
      .attr('class', 'bar')
      .attr('x', d => x(d[0]) || 0)
      .attr('width', x.bandwidth())
      .attr('y', d => y(d[1]))
      .attr('height', d => height - y(d[1]))
      .attr('fill', '#3b82f6')
      .attr('rx', 4);

    // Add axes
    g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x));

    g.append('g')
      .call(d3.axisLeft(y));

    // Add labels
    g.selectAll('.label')
      .data(data)
      .enter().append('text')
      .attr('class', 'label')
      .attr('x', d => (x(d[0]) || 0) + x.bandwidth() / 2)
      .attr('y', d => y(d[1]) - 5)
      .attr('text-anchor', 'middle')
      .attr('fill', '#374151')
      .attr('font-size', '12px')
      .text(d => d[1]);

  }, [mockStatistics, loading]);

  // Create pie chart for data quality
  useEffect(() => {
    if (!pieChartRef.current || loading) return;

    const svg = d3.select(pieChartRef.current);
    svg.selectAll('*').remove();

    const width = 200;
    const height = 200;
    const radius = Math.min(width, height) / 2 - 10;

    const g = svg.append('g')
      .attr('transform', `translate(${width / 2},${height / 2})`);

    const qualityScore = mockStatistics.quality_score;
    const data = [
      { label: 'Quality', value: qualityScore },
      { label: 'Issues', value: 100 - qualityScore }
    ];

    const color = d3.scaleOrdinal()
      .domain(['Quality', 'Issues'])
      .range(['#10b981', '#ef4444']);

    const pie = d3.pie<{label: string, value: number}>()
      .value(d => d.value);

    const arc = d3.arc<d3.PieArcDatum<{label: string, value: number}>>()
      .innerRadius(radius * 0.6)
      .outerRadius(radius);

    const arcs = g.selectAll('.arc')
      .data(pie(data))
      .enter().append('g')
      .attr('class', 'arc');

    arcs.append('path')
      .attr('d', arc)
      .attr('fill', d => color(d.data.label) as string);

    // Add center text
    g.append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', '0.35em')
      .attr('font-size', '24px')
      .attr('font-weight', 'bold')
      .attr('fill', '#374151')
      .text(`${qualityScore}%`);

  }, [mockStatistics, loading]);

  // Create quality indicators chart
  useEffect(() => {
    if (!qualityChartRef.current || loading) return;

    const svg = d3.select(qualityChartRef.current);
    svg.selectAll('*').remove();

    const margin = { top: 20, right: 20, bottom: 40, left: 80 };
    const width = 350 - margin.left - margin.right;
    const height = 150 - margin.bottom - margin.top;

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const data = [
      { metric: 'Missing Values', value: mockStatistics.missing_values_percentage, max: 100 },
      { metric: 'Outliers', value: (mockStatistics.outliers_detected / mockStatistics.total_records) * 100, max: 100 },
      { metric: 'Duplicates', value: (mockStatistics.duplicate_records / mockStatistics.total_records) * 100, max: 100 }
    ];

    const y = d3.scaleBand()
      .domain(data.map(d => d.metric))
      .range([0, height])
      .padding(0.1);

    const x = d3.scaleLinear()
      .domain([0, 100])
      .range([0, width]);

    // Add background bars
    g.selectAll('.bg-bar')
      .data(data)
      .enter().append('rect')
      .attr('class', 'bg-bar')
      .attr('x', 0)
      .attr('y', d => y(d.metric) || 0)
      .attr('width', width)
      .attr('height', y.bandwidth())
      .attr('fill', '#f3f4f6')
      .attr('rx', 3);

    // Add value bars
    g.selectAll('.value-bar')
      .data(data)
      .enter().append('rect')
      .attr('class', 'value-bar')
      .attr('x', 0)
      .attr('y', d => y(d.metric) || 0)
      .attr('width', d => x(d.value))
      .attr('height', y.bandwidth())
      .attr('fill', d => d.value > 10 ? '#ef4444' : '#10b981')
      .attr('rx', 3);

    // Add labels
    g.selectAll('.metric-label')
      .data(data)
      .enter().append('text')
      .attr('class', 'metric-label')
      .attr('x', -10)
      .attr('y', d => (y(d.metric) || 0) + y.bandwidth() / 2)
      .attr('dy', '0.35em')
      .attr('text-anchor', 'end')
      .attr('fill', '#374151')
      .attr('font-size', '12px')
      .text(d => d.metric);

    // Add value labels
    g.selectAll('.value-label')
      .data(data)
      .enter().append('text')
      .attr('class', 'value-label')
      .attr('x', d => x(d.value) + 5)
      .attr('y', d => (y(d.metric) || 0) + y.bandwidth() / 2)
      .attr('dy', '0.35em')
      .attr('fill', '#374151')
      .attr('font-size', '11px')
      .text(d => `${d.value.toFixed(1)}%`);

  }, [mockStatistics, loading]);

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-gray-200 rounded-lg h-24"></div>
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="bg-gray-200 rounded-lg h-64"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Records</p>
              <p className="text-2xl font-bold text-gray-900">{mockStatistics.total_records.toLocaleString()}</p>
            </div>
            <Database className="h-8 w-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Columns</p>
              <p className="text-2xl font-bold text-gray-900">{mockStatistics.total_columns}</p>
            </div>
            <BarChart3 className="h-8 w-8 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Data Quality</p>
              <p className="text-2xl font-bold text-gray-900">{mockStatistics.quality_score}%</p>
            </div>
            {mockStatistics.quality_score >= 80 ? (
              <CheckCircle className="h-8 w-8 text-green-500" />
            ) : (
              <AlertTriangle className="h-8 w-8 text-yellow-500" />
            )}
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Missing Values</p>
              <p className="text-2xl font-bold text-gray-900">{mockStatistics.missing_values_percentage}%</p>
            </div>
            <Activity className="h-8 w-8 text-orange-500" />
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Data Types Chart */}
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <BarChart3 className="h-5 w-5 mr-2 text-blue-500" />
            Data Types Distribution
          </h3>
          <svg ref={barChartRef} width="300" height="240" className="overflow-visible" />
        </div>

        {/* Quality Score Chart */}
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <PieChart className="h-5 w-5 mr-2 text-green-500" />
            Data Quality Score
          </h3>
          <div className="flex justify-center">
            <svg ref={pieChartRef} width="200" height="200" />
          </div>
        </div>

        {/* Quality Indicators */}
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <TrendingUp className="h-5 w-5 mr-2 text-orange-500" />
            Quality Indicators
          </h3>
          <svg ref={qualityChartRef} width="350" height="190" className="overflow-visible" />
        </div>
      </div>

      {/* Detailed Statistics Table */}
      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Column Statistics</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Column</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Mean</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Median</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Unique Values</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Null Count</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {Object.entries(mockStatistics.column_statistics).map(([column, stats]) => (
                <tr key={column}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{column}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {stats.mean ? stats.mean.toLocaleString() : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {stats.median ? stats.median.toLocaleString() : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {stats.unique_values || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      stats.null_count === 0 ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {stats.null_count}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
