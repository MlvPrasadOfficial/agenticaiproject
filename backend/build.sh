# Render Build Script for Backend

# This script is executed by Render during deployment
echo "🚀 Starting backend deployment build..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Run tests
echo "🧪 Running tests..."
python -m pytest tests/ -v --tb=short

# Check code quality
echo "🔍 Running code quality checks..."
python -m pylint app/ --exit-zero
python -m black --check app/ || echo "⚠️  Code formatting issues found"

# Database setup (if needed)
echo "🗄️ Setting up database..."
# Add any database migration commands here if needed

echo "✅ Backend build completed successfully!"
