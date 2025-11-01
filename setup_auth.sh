#!/bin/bash

# CAAI Authentication Setup Script
echo "🚀 Setting up CAAI Authentication System..."
echo "=" * 60

# Backend setup
echo "📦 Installing Python dependencies..."
cd backend
pip install -r requirements.txt

echo "🗄️ Initializing authentication database..."
python init_auth_db.py

# Frontend setup
echo "📦 Installing Node.js dependencies..."
cd ../frontend-next
npm install

# Create environment files
echo "⚙️ Creating environment files..."

# Backend .env
cat > ../backend/.env << EOF
# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production-$(openssl rand -hex 32)

# Database
DATABASE_URL=sqlite:///./caai_auth.db

# FastAPI
UVICORN_HOST=0.0.0.0
UVICORN_PORT=8000

# Gemini API
GEMINI_API_KEY=AIzaSyATL5uTTApzOo7m6bItJPCP1IV8f3VGXKk
EOF

# Frontend .env.local
cat > .env.local << EOF
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF

echo ""
echo "=" * 60
echo "✅ CAAI Authentication System Setup Complete!"
echo ""
echo "📋 Summary:"
echo "   • Python dependencies installed"
echo "   • Authentication database initialized"
echo "   • Node.js dependencies installed"
echo "   • Environment files created"
echo ""
echo "🚀 To start the system:"
echo "   Backend:  cd backend && python main.py"
echo "   Frontend: cd frontend-next && npm run dev"
echo ""
echo "🔐 Default accounts created:"
echo "   SuperAdmin: superadmin / SuperAdmin@123"
echo "   Admin:      admin / Admin@123"
echo "   User:       user1 / User@123"
echo ""
echo "⚠️  Security Reminders:"
echo "   • Change default passwords immediately"
echo "   • Update JWT_SECRET_KEY in production"
echo "   • Enable HTTPS in production"
echo "   • Configure proper CORS origins"