#!/bin/bash
# Vercel Build Script for Frontend

echo "🚀 Starting frontend deployment build..."

# Install dependencies
echo "📦 Installing dependencies..."
npm ci --production=false

# Run tests
echo "🧪 Running tests..."
npm run test:ci

# Run linting
echo "🔍 Running code quality checks..."
npm run lint

# Build the application
echo "🏗️ Building Next.js application..."
npm run build

# Optimize build
echo "⚡ Optimizing build..."
# Additional optimization steps can be added here

echo "✅ Frontend build completed successfully!"
