'use client';

import React, { useRef, useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import * as d3 from 'd3';
import { Download, ZoomIn, ZoomOut, RotateCcw, Settings, Maximize2 } from 'lucide-react';

interface DataPoint {
  x: number | Date;
  y: number;
  label?: string;
  color?: string;
  metadata?: Record<string, any>;
}

interface ChartSeries {
  name: string;
  data: DataPoint[];
  color?: string;
  type?: 'line' | 'area' | 'bar' | 'scatter';
  visible?: boolean;
}

interface InteractiveChartsProps {
  series: ChartSeries[];
  width?: number;
  height?: number;
  title?: string;
  xAxisLabel?: string;
  yAxisLabel?: string;
  chartType?: 'line' | 'area' | 'bar' | 'scatter' | 'combo';
  enableZoom?: boolean;
  enableBrush?: boolean;
  enableTooltip?: boolean;
  enableLegend?: boolean;
  className?: string;
  onDataPointClick?: (dataPoint: DataPoint, series: ChartSeries) => void;
  onExport?: (format: 'png' | 'svg' | 'csv') => void;
}

export function InteractiveCharts({
  series,
  width = 800,
  height = 400,
  title,
  xAxisLabel,
  yAxisLabel,
  chartType = 'line',
  enableZoom = true,
  enableBrush = false,
  enableTooltip = true,
  enableLegend = true,
  className = '',
  onDataPointClick,
  onExport
}: InteractiveChartsProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);
  const [zoomTransform, setZoomTransform] = useState<d3.ZoomTransform | null>(null);
  const [selectedSeries, setSelectedSeries] = useState<string[]>(
    series.filter(s => s.visible !== false).map(s => s.name)
  );
  const [isFullscreen, setIsFullscreen] = useState(false);

  const margin = { top: 20, right: 30, bottom: 40, left: 50 };
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;

  useEffect(() => {
    if (!svgRef.current || series.length === 0) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    // Create main group
    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Filter visible series
    const visibleSeries = series.filter(s => selectedSeries.includes(s.name));
    if (visibleSeries.length === 0) return;

    // Get all data points for domain calculation
    const allData = visibleSeries.flatMap(s => s.data);
    
    // Create scales
    const xExtent = d3.extent(allData, d => d.x) as [any, any];
    const yExtent = d3.extent(allData, d => d.y) as [number, number];
    
    const xScale = (allData[0]?.x instanceof Date ? d3.scaleTime() : d3.scaleLinear())
      .domain(xExtent)
      .range([0, innerWidth]);

    const yScale = d3.scaleLinear()
      .domain([yExtent[0] - (yExtent[1] - yExtent[0]) * 0.1, yExtent[1] + (yExtent[1] - yExtent[0]) * 0.1])
      .range([innerHeight, 0]);

    // Color scale
    const colorScale = d3.scaleOrdinal(d3.schemeCategory10);

    // Create axes
    const xAxis = d3.axisBottom(xScale);
    const yAxis = d3.axisLeft(yScale);

    const xAxisGroup = g.append('g')
      .attr('class', 'x-axis')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(xAxis);

    const yAxisGroup = g.append('g')
      .attr('class', 'y-axis')
      .call(yAxis);

    // Add axis labels
    if (xAxisLabel) {
      g.append('text')
        .attr('class', 'x-axis-label')
        .attr('transform', `translate(${innerWidth / 2},${innerHeight + 35})`)
        .style('text-anchor', 'middle')
        .style('font-size', '12px')
        .style('fill', 'currentColor')
        .text(xAxisLabel);
    }

    if (yAxisLabel) {
      g.append('text')
        .attr('class', 'y-axis-label')
        .attr('transform', 'rotate(-90)')
        .attr('y', -35)
        .attr('x', -innerHeight / 2)
        .style('text-anchor', 'middle')
        .style('font-size', '12px')
        .style('fill', 'currentColor')
        .text(yAxisLabel);
    }

    // Create clip path for zooming
    const clipPath = g.append('defs')
      .append('clipPath')
      .attr('id', 'chart-clip')
      .append('rect')
      .attr('width', innerWidth)
      .attr('height', innerHeight);

    // Chart content group
    const chartGroup = g.append('g')
      .attr('clip-path', 'url(#chart-clip)');

    // Render each series
    visibleSeries.forEach((seriesData, seriesIndex) => {
      const color = seriesData.color || colorScale(seriesIndex.toString());
      const seriesGroup = chartGroup.append('g')
        .attr('class', `series-${seriesIndex}`);

      if (chartType === 'line' || seriesData.type === 'line') {
        // Line chart
        const line = d3.line<DataPoint>()
          .x(d => xScale(d.x))
          .y(d => yScale(d.y))
          .curve(d3.curveMonotoneX);

        const path = seriesGroup.append('path')
          .datum(seriesData.data)
          .attr('fill', 'none')
          .attr('stroke', color)
          .attr('stroke-width', 2)
          .attr('d', line);

        // Animate line drawing
        const totalLength = path.node()?.getTotalLength() || 0;
        path
          .attr('stroke-dasharray', `${totalLength} ${totalLength}`)
          .attr('stroke-dashoffset', totalLength)
          .transition()
          .duration(1500)
          .ease(d3.easeLinear)
          .attr('stroke-dashoffset', 0);

      } else if (chartType === 'area' || seriesData.type === 'area') {
        // Area chart
        const area = d3.area<DataPoint>()
          .x(d => xScale(d.x))
          .y0(yScale(0))
          .y1(d => yScale(d.y))
          .curve(d3.curveMonotoneX);

        seriesGroup.append('path')
          .datum(seriesData.data)
          .attr('fill', color)
          .attr('fill-opacity', 0.3)
          .attr('stroke', color)
          .attr('stroke-width', 2)
          .attr('d', area);

      } else if (chartType === 'bar' || seriesData.type === 'bar') {
        // Bar chart
        const barWidth = innerWidth / seriesData.data.length * 0.8;
        
        seriesGroup.selectAll('.bar')
          .data(seriesData.data)
          .enter()
          .append('rect')
          .attr('class', 'bar')
          .attr('x', d => xScale(d.x) - barWidth / 2)
          .attr('y', d => yScale(Math.max(0, d.y)))
          .attr('width', barWidth)
          .attr('height', d => Math.abs(yScale(d.y) - yScale(0)))
          .attr('fill', color)
          .attr('opacity', 0.8)
          .on('mouseover', function(event, d) {
            d3.select(this).attr('opacity', 1);
            showTooltip(event, d, seriesData);
          })
          .on('mouseout', function() {
            d3.select(this).attr('opacity', 0.8);
            hideTooltip();
          })
          .on('click', (event, d) => onDataPointClick?.(d, seriesData));

      } else if (chartType === 'scatter' || seriesData.type === 'scatter') {
        // Scatter plot
        seriesGroup.selectAll('.dot')
          .data(seriesData.data)
          .enter()
          .append('circle')
          .attr('class', 'dot')
          .attr('cx', d => xScale(d.x))
          .attr('cy', d => yScale(d.y))
          .attr('r', 4)
          .attr('fill', color)
          .attr('stroke', 'white')
          .attr('stroke-width', 2)
          .on('mouseover', function(event, d) {
            d3.select(this).attr('r', 6);
            showTooltip(event, d, seriesData);
          })
          .on('mouseout', function() {
            d3.select(this).attr('r', 4);
            hideTooltip();
          })
          .on('click', (event, d) => onDataPointClick?.(d, seriesData));
      }

      // Add data points for line/area charts
      if ((chartType === 'line' || chartType === 'area') && enableTooltip) {
        seriesGroup.selectAll('.dot')
          .data(seriesData.data)
          .enter()
          .append('circle')
          .attr('class', 'dot')
          .attr('cx', d => xScale(d.x))
          .attr('cy', d => yScale(d.y))
          .attr('r', 3)
          .attr('fill', color)
          .attr('stroke', 'white')
          .attr('stroke-width', 2)
          .style('opacity', 0)
          .on('mouseover', function(event, d) {
            d3.select(this).style('opacity', 1).attr('r', 5);
            showTooltip(event, d, seriesData);
          })
          .on('mouseout', function() {
            d3.select(this).style('opacity', 0).attr('r', 3);
            hideTooltip();
          })
          .on('click', (event, d) => onDataPointClick?.(d, seriesData));
      }
    });

    // Zoom behavior
    if (enableZoom) {
      const zoom = d3.zoom<SVGSVGElement, unknown>()
        .scaleExtent([0.1, 10])
        .extent([[0, 0], [width, height]])
        .on('zoom', (event) => {
          const { transform } = event;
          setZoomTransform(transform);

          // Update scales
          const newXScale = transform.rescaleX(xScale);
          const newYScale = transform.rescaleY(yScale);

          // Update axes
          xAxisGroup.call(xAxis.scale(newXScale));
          yAxisGroup.call(yAxis.scale(newYScale));

          // Update chart elements
          chartGroup.selectAll('.series-0 path')
            .attr('transform', transform.toString());
          
          chartGroup.selectAll('.dot')
            .attr('transform', transform.toString());
            
          chartGroup.selectAll('.bar')
            .attr('transform', transform.toString());
        });

      svg.call(zoom);
    }

    // Brush for selection
    if (enableBrush) {
      const brush = d3.brushX()
        .extent([[0, 0], [innerWidth, innerHeight]])
        .on('end', (event) => {
          if (!event.selection) return;
          const [x0, x1] = event.selection;
          const domain = [xScale.invert(x0), xScale.invert(x1)];
          // Handle brush selection
          console.log('Brush selection:', domain);
        });

      g.append('g')
        .attr('class', 'brush')
        .call(brush);
    }

    // Tooltip functions
    function showTooltip(event: any, data: DataPoint, series: ChartSeries) {
      if (!enableTooltip || !tooltipRef.current) return;

      const tooltip = d3.select(tooltipRef.current);
      const formatValue = d3.format('.2f');
      const formatDate = d3.timeFormat('%Y-%m-%d %H:%M');

      tooltip
        .style('opacity', 1)
        .style('left', `${event.pageX + 10}px`)
        .style('top', `${event.pageY - 10}px`)
        .html(`
          <div class="p-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg">
            <div class="font-medium text-gray-900 dark:text-gray-100">${series.name}</div>
            <div class="text-sm text-gray-600 dark:text-gray-400">
              ${data.x instanceof Date ? formatDate(data.x) : data.x}: ${formatValue(data.y)}
            </div>
            ${data.label ? `<div class="text-xs text-gray-500">${data.label}</div>` : ''}
            ${data.metadata ? `<div class="text-xs text-gray-500 mt-1">${Object.entries(data.metadata).map(([k, v]) => `${k}: ${v}`).join(', ')}</div>` : ''}
          </div>
        `);
    }

    function hideTooltip() {
      if (!tooltipRef.current) return;
      d3.select(tooltipRef.current).style('opacity', 0);
    }

  }, [series, selectedSeries, width, height, chartType, enableZoom, enableBrush, enableTooltip]);

  const resetZoom = () => {
    if (!svgRef.current) return;
    const svg = d3.select(svgRef.current);
    svg.transition().duration(750).call(
      d3.zoom<SVGSVGElement, unknown>().transform,
      d3.zoomIdentity
    );
    setZoomTransform(null);
  };

  const exportChart = (format: 'png' | 'svg' | 'csv') => {
    if (format === 'csv') {
      // Export data as CSV
      const csvData = series.flatMap(s => 
        s.data.map(d => ({
          series: s.name,
          x: d.x,
          y: d.y,
          label: d.label || '',
          ...d.metadata
        }))
      );
      
      const csv = d3.csvFormat(csvData);
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `chart-data-${Date.now()}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } else {
      onExport?.(format);
    }
  };

  const toggleSeries = (seriesName: string) => {
    setSelectedSeries(prev => 
      prev.includes(seriesName)
        ? prev.filter(s => s !== seriesName)
        : [...prev, seriesName]
    );
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          {title && (
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              {title}
            </h3>
          )}
        </div>
        
        <div className="flex items-center gap-2">
          {/* Export */}
          <div className="relative group">
            <button className="p-2 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-700">
              <Download className="w-4 h-4" />
            </button>
            <div className="absolute right-0 top-full mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
              <button
                onClick={() => exportChart('png')}
                className="block w-full px-3 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                Export PNG
              </button>
              <button
                onClick={() => exportChart('svg')}
                className="block w-full px-3 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                Export SVG
              </button>
              <button
                onClick={() => exportChart('csv')}
                className="block w-full px-3 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                Export CSV
              </button>
            </div>
          </div>

          {/* Zoom Controls */}
          {enableZoom && (
            <>
              <button
                onClick={resetZoom}
                className="p-2 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-700"
                title="Reset Zoom"
              >
                <RotateCcw className="w-4 h-4" />
              </button>
              
              <button
                onClick={() => setIsFullscreen(!isFullscreen)}
                className="p-2 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-700"
                title="Fullscreen"
              >
                <Maximize2 className="w-4 h-4" />
              </button>
            </>
          )}
        </div>
      </div>

      {/* Legend */}
      {enableLegend && (
        <div className="flex flex-wrap gap-4">
          {series.map((s, index) => (
            <label key={s.name} className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={selectedSeries.includes(s.name)}
                onChange={() => toggleSeries(s.name)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <div
                className="w-3 h-3 rounded"
                style={{ backgroundColor: s.color || d3.schemeCategory10[index] }}
              />
              <span className="text-sm text-gray-700 dark:text-gray-300">{s.name}</span>
            </label>
          ))}
        </div>
      )}

      {/* Chart */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className={`relative ${isFullscreen ? 'fixed inset-4 z-50 bg-white dark:bg-gray-900 rounded-lg p-4' : ''}`}
      >
        <svg
          ref={svgRef}
          width={isFullscreen ? '100%' : width}
          height={isFullscreen ? '90vh' : height}
          className="border border-gray-200 dark:border-gray-700 rounded"
        />
        
        {/* Tooltip */}
        <div
          ref={tooltipRef}
          className="absolute pointer-events-none opacity-0 transition-opacity z-10"
        />
        
        {/* Zoom info */}
        {zoomTransform && (
          <div className="absolute top-2 right-2 px-2 py-1 bg-black/50 text-white text-xs rounded">
            Zoom: {zoomTransform.k.toFixed(2)}x
          </div>
        )}
      </motion.div>

      {/* Instructions */}
      <div className="text-xs text-gray-500 dark:text-gray-400">
        {enableZoom && 'Mouse wheel to zoom, drag to pan. '}
        {enableBrush && 'Drag to select range. '}
        {enableTooltip && 'Hover over data points for details.'}
      </div>
    </div>
  );
}

// Example usage component
export function InteractiveChartsExample() {
  const generateTimeSeriesData = (name: string, points: number, variance: number): ChartSeries => {
    const data: DataPoint[] = [];
    let value = 100;
    const startDate = new Date(Date.now() - points * 24 * 60 * 60 * 1000);
    
    for (let i = 0; i < points; i++) {
      value += (Math.random() - 0.5) * variance;
      data.push({
        x: new Date(startDate.getTime() + i * 24 * 60 * 60 * 1000),
        y: value,
        label: `Day ${i + 1}`,
        metadata: { trend: value > data[data.length - 1]?.y ? 'up' : 'down' }
      });
    }
    
    return { name, data, type: 'line' };
  };

  const sampleSeries: ChartSeries[] = [
    generateTimeSeriesData('Revenue', 30, 20),
    generateTimeSeriesData('Users', 30, 15),
    generateTimeSeriesData('Conversion Rate', 30, 5)
  ];

  return (
    <div className="p-6 space-y-8">
      <InteractiveCharts
        series={sampleSeries}
        title="Interactive Time Series Chart"
        xAxisLabel="Date"
        yAxisLabel="Value"
        chartType="line"
        enableZoom={true}
        enableBrush={false}
        enableTooltip={true}
        enableLegend={true}
        width={800}
        height={400}
        onDataPointClick={(dataPoint, series) => {
          console.log('Clicked:', dataPoint, series);
        }}
        onExport={(format) => {
          console.log('Export as:', format);
        }}
      />
    </div>
  );
}
