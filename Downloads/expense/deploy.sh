#!/bin/bash
# Deploy Expense Tracker to Vercel and GitHub
# Run this script to deploy your app

echo "🚀 Expense Tracker Cloud - Deployment Script"
echo "=============================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Check if files exist
if [ ! -f "index.html" ]; then
    echo "❌ index.html not found. Make sure you're in the correct directory."
    exit 1
fi

echo "✅ Files found!"
echo ""

# Initialize git if not already done
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
    git config user.email "your-email@example.com"
    git config user.name "Expense Tracker User"
fi

# Add all files
echo "📝 Adding files..."
git add .

# Commit
echo "💾 Committing..."
git commit -m "Deploy Expense Tracker AI Cloud - $(date '+%Y-%m-%d %H:%M:%S')"

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo ""
    echo "📥 Vercel CLI not found. Installing..."
    npm install -g vercel
fi

echo ""
echo "🌐 Deploying to Vercel..."
echo "=============================================="
echo ""

# Deploy to Vercel
vercel --prod

echo ""
echo "✅ Deployment Complete!"
echo ""
echo "📌 Next Steps:"
echo "1. Copy your deployment URL from above"
echo "2. Visit the URL to see your app live"
echo "3. Share the URL with others"
echo "4. Data is stored locally in each browser"
echo ""
echo "🔄 To update:"
echo "   git add ."
echo "   git commit -m 'Your message'"
echo "   git push"
echo "   (Vercel auto-deploys!)"
echo ""