#!/bin/bash
# Script to start both Flask backend and Next.js frontend

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting development servers...${NC}\n"

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/src"
FRONTEND_DIR="$(cd "$PROJECT_ROOT/../NextJs-Super-FrontEnd" && pwd)"

# Check if frontend directory exists
if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${YELLOW}⚠️  Frontend directory not found at: $FRONTEND_DIR${NC}"
    echo -e "${YELLOW}   Starting backend only...${NC}\n"
    cd "$BACKEND_DIR"
    source .venv/bin/activate
    python app.py
    exit 0
fi

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Stopping servers...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

trap cleanup SIGINT SIGTERM

# Start Flask backend
echo -e "${GREEN}📦 Starting Flask backend...${NC}"
cd "$BACKEND_DIR"
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating...${NC}"
    python3 -m venv .venv
fi

source .venv/bin/activate

# Check if dependencies are installed
if ! python -c "import flask" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Installing backend dependencies...${NC}"
    pip install -r requirements.txt
fi

python app.py &
BACKEND_PID=$!
echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}\n"

# Wait a bit for backend to start
sleep 2

# Start Next.js frontend
echo -e "${GREEN}🌐 Starting Next.js frontend...${NC}"
cd "$FRONTEND_DIR"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠️  Installing frontend dependencies...${NC}"
    npm install
fi

npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}\n"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✨ Development servers are running!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Backend:${NC}  http://localhost:4000"
echo -e "${GREEN}Frontend:${NC} http://localhost:3000"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}\n"

# Wait for both processes
wait

