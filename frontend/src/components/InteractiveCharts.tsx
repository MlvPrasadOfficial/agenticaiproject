/**
 * Interactive Data Visualization Components
 * Task 56: Add data visualization components (D3.js integration, interactive charts and graphs)
 */

'use client';

import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { LineChart, BarChart, Scatter, Download, ZoomIn, ZoomOut, RotateCcw, Filter } from 'lucide-react';

interface DataPoint {
  x: number | string;
  y: number;
  category?: string;
  date?: Date;
  label?: string;
}

interface ChartData {
  data: DataPoint[];
  title: string;
  xLabel: string;
  yLabel: string;
  type: 'line' | 'bar' | 'scatter' | 'area';
}

interface InteractiveChartsProps {
  chartData: ChartData[];
  fileId?: string;
  loading?: boolean;
}

export default function InteractiveCharts({ chartData, fileId, loading }: InteractiveChartsProps) {
  const lineChartRef = useRef<SVGSVGElement>(null);
  const barChartRef = useRef<SVGSVGElement>(null);
  const scatterChartRef = useRef<SVGSVGElement>(null);
  const areaChartRef = useRef<SVGSVGElement>(null);
  
  const [selectedChart, setSelectedChart] = useState<'line' | 'bar' | 'scatter' | 'area'>('line');
  const [zoomLevel, setZoomLevel] = useState(1);
  const [hoveredPoint, setHoveredPoint] = useState<DataPoint | null>(null);

  // Sample data if none provided
  const sampleData: ChartData[] = chartData.length > 0 ? chartData : [
    {
      data: Array.from({ length: 20 }, (_, i) => ({
        x: i,
        y: Math.sin(i * 0.5) * 50 + 100 + Math.random() * 20,
        label: `Point ${i}`
      })),
      title: 'Revenue Trend',
      xLabel: 'Month',
      yLabel: 'Revenue ($)',
      type: 'line'
    },
    {
      data: [
        { x: 'Product A', y: 120, category: 'Electronics' },
        { x: 'Product B', y: 85, category: 'Clothing' },
        { x: 'Product C', y: 95, category: 'Books' },
        { x: 'Product D', y: 110, category: 'Electronics' },
        { x: 'Product E', y: 75, category: 'Clothing' }
      ],
      title: 'Sales by Product',
      xLabel: 'Product',
      yLabel: 'Sales',
      type: 'bar'
    },
    {
      data: Array.from({ length: 50 }, (_, i) => ({
        x: Math.random() * 100,
        y: Math.random() * 100,
        category: ['A', 'B', 'C'][Math.floor(Math.random() * 3)],
        label: `Data Point ${i}`
      })),
      title: 'Customer Segmentation',
      xLabel: 'Value 1',
      yLabel: 'Value 2',
      type: 'scatter'
    },
    {
      data: Array.from({ length: 15 }, (_, i) => ({
        x: i,
        y: Math.random() * 50 + 25,
        label: `Period ${i}`
      })),
      title: 'Growth Area',
      xLabel: 'Time Period',
      yLabel: 'Growth Rate (%)',
      type: 'area'
    }
  ];

  // Line Chart with zoom and hover
  useEffect(() => {
    if (!lineChartRef.current || loading) return;

    const svg = d3.select(lineChartRef.current);
    svg.selectAll('*').remove();

    const margin = { top: 20, right: 30, bottom: 40, left: 50 };
    const width = 600 - margin.left - margin.right;
    const height = 300 - margin.bottom - margin.top;

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const lineData = sampleData.find(d => d.type === 'line')?.data || [];
    
    const x = d3.scaleLinear()
      .domain(d3.extent(lineData, d => d.x as number) as [number, number])
      .range([0, width]);

    const y = d3.scaleLinear()
      .domain(d3.extent(lineData, d => d.y) as [number, number])
      .range([height, 0]);

    // Add zoom behavior
    const zoom = d3.zoom<SVGGElement, unknown>()
      .scaleExtent([0.5, 5])
      .on('zoom', (event) => {
        const newX = event.transform.rescaleX(x);
        const newY = event.transform.rescaleY(y);
        
        // Update line
        line.attr('d', d3.line<DataPoint>()
          .x(d => newX(d.x as number))
          .y(d => newY(d.y))
        );

        // Update axes
        xAxis.call(d3.axisBottom(newX));
        yAxis.call(d3.axisLeft(newY));

        // Update dots
        dots.attr('cx', d => newX(d.x as number))
           .attr('cy', d => newY(d.y));
      });

    g.call(zoom);

    // Add axes
    const xAxis = g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x));

    const yAxis = g.append('g')
      .call(d3.axisLeft(y));

    // Add grid lines
    g.append('g')
      .attr('class', 'grid')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x)
        .tickSize(-height)
        .tickFormat(() => '')
      )
      .selectAll('line')
      .attr('stroke', '#e5e7eb')
      .attr('stroke-width', 1);

    g.append('g')
      .attr('class', 'grid')
      .call(d3.axisLeft(y)
        .tickSize(-width)
        .tickFormat(() => '')
      )
      .selectAll('line')
      .attr('stroke', '#e5e7eb')
      .attr('stroke-width', 1);

    // Add line
    const line = g.append('path')
      .datum(lineData)
      .attr('fill', 'none')
      .attr('stroke', '#3b82f6')
      .attr('stroke-width', 2)
      .attr('d', d3.line<DataPoint>()
        .x(d => x(d.x as number))
        .y(d => y(d.y))
        .curve(d3.curveMonotoneX)
      );

    // Add dots with hover effects
    const dots = g.selectAll('.dot')
      .data(lineData)
      .enter().append('circle')
      .attr('class', 'dot')
      .attr('cx', d => x(d.x as number))
      .attr('cy', d => y(d.y))
      .attr('r', 4)
      .attr('fill', '#3b82f6')
      .style('cursor', 'pointer')
      .on('mouseover', function(event, d) {
        d3.select(this).attr('r', 6).attr('fill', '#1d4ed8');
        setHoveredPoint(d);
      })
      .on('mouseout', function() {
        d3.select(this).attr('r', 4).attr('fill', '#3b82f6');
        setHoveredPoint(null);
      });

    // Add labels
    g.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', 0 - margin.left)
      .attr('x', 0 - (height / 2))
      .attr('dy', '1em')
      .style('text-anchor', 'middle')
      .text(sampleData.find(d => d.type === 'line')?.yLabel || 'Y-Axis');

    g.append('text')
      .attr('transform', `translate(${width / 2}, ${height + margin.bottom})`)
      .style('text-anchor', 'middle')
      .text(sampleData.find(d => d.type === 'line')?.xLabel || 'X-Axis');

  }, [sampleData, loading, zoomLevel]);

  // Bar Chart with interactive features
  useEffect(() => {
    if (!barChartRef.current || loading) return;

    const svg = d3.select(barChartRef.current);
    svg.selectAll('*').remove();

    const margin = { top: 20, right: 30, bottom: 40, left: 50 };
    const width = 600 - margin.left - margin.right;
    const height = 300 - margin.bottom - margin.top;

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const barData = sampleData.find(d => d.type === 'bar')?.data || [];
    
    const x = d3.scaleBand()
      .domain(barData.map(d => d.x as string))
      .range([0, width])
      .padding(0.1);

    const y = d3.scaleLinear()
      .domain([0, d3.max(barData, d => d.y) || 0])
      .range([height, 0]);

    const color = d3.scaleOrdinal(d3.schemeCategory10);

    // Add axes
    g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x));

    g.append('g')
      .call(d3.axisLeft(y));

    // Add bars with animations
    g.selectAll('.bar')
      .data(barData)
      .enter().append('rect')
      .attr('class', 'bar')
      .attr('x', d => x(d.x as string) || 0)
      .attr('width', x.bandwidth())
      .attr('y', height)
      .attr('height', 0)
      .attr('fill', (d, i) => color(i.toString()))
      .style('cursor', 'pointer')
      .on('mouseover', function(event, d) {
        d3.select(this).attr('opacity', 0.8);
        setHoveredPoint(d);
      })
      .on('mouseout', function() {
        d3.select(this).attr('opacity', 1);
        setHoveredPoint(null);
      })
      .transition()
      .duration(800)
      .attr('y', d => y(d.y))
      .attr('height', d => height - y(d.y));

  }, [sampleData, loading]);

  // Scatter Plot with categories
  useEffect(() => {
    if (!scatterChartRef.current || loading) return;

    const svg = d3.select(scatterChartRef.current);
    svg.selectAll('*').remove();

    const margin = { top: 20, right: 30, bottom: 40, left: 50 };
    const width = 600 - margin.left - margin.right;
    const height = 300 - margin.bottom - margin.top;

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const scatterData = sampleData.find(d => d.type === 'scatter')?.data || [];
    
    const x = d3.scaleLinear()
      .domain(d3.extent(scatterData, d => d.x as number) as [number, number])
      .range([0, width]);

    const y = d3.scaleLinear()
      .domain(d3.extent(scatterData, d => d.y) as [number, number])
      .range([height, 0]);

    const color = d3.scaleOrdinal(d3.schemeCategory10);

    // Add axes
    g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x));

    g.append('g')
      .call(d3.axisLeft(y));

    // Add dots
    g.selectAll('.scatter-dot')
      .data(scatterData)
      .enter().append('circle')
      .attr('class', 'scatter-dot')
      .attr('cx', d => x(d.x as number))
      .attr('cy', d => y(d.y))
      .attr('r', 5)
      .attr('fill', d => color(d.category || 'default'))
      .attr('opacity', 0.7)
      .style('cursor', 'pointer')
      .on('mouseover', function(event, d) {
        d3.select(this).attr('r', 8).attr('opacity', 1);
        setHoveredPoint(d);
      })
      .on('mouseout', function() {
        d3.select(this).attr('r', 5).attr('opacity', 0.7);
        setHoveredPoint(null);
      });

  }, [sampleData, loading]);

  // Area Chart
  useEffect(() => {
    if (!areaChartRef.current || loading) return;

    const svg = d3.select(areaChartRef.current);
    svg.selectAll('*').remove();

    const margin = { top: 20, right: 30, bottom: 40, left: 50 };
    const width = 600 - margin.left - margin.right;
    const height = 300 - margin.bottom - margin.top;

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const areaData = sampleData.find(d => d.type === 'area')?.data || [];
    
    const x = d3.scaleLinear()
      .domain(d3.extent(areaData, d => d.x as number) as [number, number])
      .range([0, width]);

    const y = d3.scaleLinear()
      .domain([0, d3.max(areaData, d => d.y) || 0])
      .range([height, 0]);

    // Add axes
    g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x));

    g.append('g')
      .call(d3.axisLeft(y));

    // Define area
    const area = d3.area<DataPoint>()
      .x(d => x(d.x as number))
      .y0(height)
      .y1(d => y(d.y))
      .curve(d3.curveMonotoneX);

    // Add gradient
    const gradient = svg.append('defs')
      .append('linearGradient')
      .attr('id', 'area-gradient')
      .attr('gradientUnits', 'userSpaceOnUse')
      .attr('x1', 0).attr('y1', y(0))
      .attr('x2', 0).attr('y2', y(d3.max(areaData, d => d.y) || 0));

    gradient.append('stop')
      .attr('offset', '0%')
      .attr('stop-color', '#3b82f6')
      .attr('stop-opacity', 0.8);

    gradient.append('stop')
      .attr('offset', '100%')
      .attr('stop-color', '#3b82f6')
      .attr('stop-opacity', 0.1);

    // Add area
    g.append('path')
      .datum(areaData)
      .attr('fill', 'url(#area-gradient)')
      .attr('d', area);

  }, [sampleData, loading]);

  const handleExport = () => {
    // Export chart as SVG
    const svgElement = document.querySelector(`svg[data-chart="${selectedChart}"]`);
    if (svgElement) {
      const svgData = new XMLSerializer().serializeToString(svgElement);
      const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
      const svgUrl = URL.createObjectURL(svgBlob);
      const downloadLink = document.createElement('a');
      downloadLink.href = svgUrl;
      downloadLink.download = `${selectedChart}-chart.svg`;
      document.body.appendChild(downloadLink);
      downloadLink.click();
      document.body.removeChild(downloadLink);
    }
  };

  const resetZoom = () => {
    setZoomLevel(1);
    // Trigger re-render of charts
    const event = new Event('zoom-reset');
    window.dispatchEvent(event);
  };

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="bg-gray-200 rounded-lg h-12"></div>
        <div className="bg-gray-200 rounded-lg h-96"></div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="bg-gray-200 rounded-lg h-80"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Chart Controls */}
      <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-200">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-gray-700">Chart Type:</span>
            <div className="flex rounded-lg border border-gray-300 overflow-hidden">
              {['line', 'bar', 'scatter', 'area'].map((type) => (
                <button
                  key={type}
                  onClick={() => setSelectedChart(type as any)}
                  className={`px-4 py-2 text-sm font-medium transition-colors ${
                    selectedChart === type
                      ? 'bg-blue-500 text-white'
                      : 'bg-white text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  {type === 'line' && <LineChart className="h-4 w-4 inline mr-1" />}
                  {type === 'bar' && <BarChart className="h-4 w-4 inline mr-1" />}
                  {type === 'scatter' && <Scatter className="h-4 w-4 inline mr-1" />}
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setZoomLevel(prev => Math.min(prev * 1.2, 3))}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              title="Zoom In"
            >
              <ZoomIn className="h-4 w-4" />
            </button>
            <button
              onClick={() => setZoomLevel(prev => Math.max(prev / 1.2, 0.5))}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              title="Zoom Out"
            >
              <ZoomOut className="h-4 w-4" />
            </button>
            <button
              onClick={resetZoom}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              title="Reset Zoom"
            >
              <RotateCcw className="h-4 w-4" />
            </button>
            <button
              onClick={handleExport}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              title="Export Chart"
            >
              <Download className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Chart Display */}
      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">
            {sampleData.find(d => d.type === selectedChart)?.title || 'Interactive Chart'}
          </h3>
          {hoveredPoint && (
            <div className="bg-gray-900 text-white px-3 py-2 rounded-lg text-sm">
              {hoveredPoint.label && <div className="font-medium">{hoveredPoint.label}</div>}
              <div>X: {hoveredPoint.x}, Y: {hoveredPoint.y.toFixed(2)}</div>
              {hoveredPoint.category && <div>Category: {hoveredPoint.category}</div>}
            </div>
          )}
        </div>

        <div className="flex justify-center">
          {selectedChart === 'line' && (
            <svg ref={lineChartRef} width="600" height="340" data-chart="line" className="overflow-visible" />
          )}
          {selectedChart === 'bar' && (
            <svg ref={barChartRef} width="600" height="340" data-chart="bar" className="overflow-visible" />
          )}
          {selectedChart === 'scatter' && (
            <svg ref={scatterChartRef} width="600" height="340" data-chart="scatter" className="overflow-visible" />
          )}
          {selectedChart === 'area' && (
            <svg ref={areaChartRef} width="600" height="340" data-chart="area" className="overflow-visible" />
          )}
        </div>
      </div>

      {/* Additional Chart Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {sampleData.slice(0, 3).map((chart, index) => (
          <div key={index} className="bg-white rounded-lg p-4 shadow-sm border border-gray-200">
            <h4 className="text-md font-medium text-gray-900 mb-3">{chart.title}</h4>
            <div className="h-48 bg-gray-50 rounded-lg flex items-center justify-center">
              <div className="text-gray-500 text-sm">
                Mini {chart.type} chart preview
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
