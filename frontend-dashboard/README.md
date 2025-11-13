# CAAI Dashboard - AI Agent System

## Functional Next.js Dashboard with Tailwind CSS

A modern, responsive dashboard for managing and executing AI-powered CA agents.

## Features

 **Real-time Agent Management**
- View all 16 agents (8 AI-powered + 8 standard)
- See agent status (Active/Inactive)
- Filter and search functionality
- Live backend connection status

 **Agent Execution**
- Interactive modal for each agent
- Dynamic parameter forms based on agent actions
- Real-time execution with loading states
- JSON result display with syntax highlighting

 **Statistics Dashboard**
- Total agents count
- Active agents tracking
- AI-powered agents indicator
- Execution metrics

 **Professional UI**
- Built with Next.js 16 + TypeScript
- Styled with Tailwind CSS
- Responsive design (mobile, tablet, desktop)
- Modern glassmorphism effects

## Quick Start

### 1. Start the Backend
```bash
cd ../backend
python main.py
```

Backend will run on: http://localhost:8000

### 2. Start the Dashboard
```bash
npm run dev
```

Dashboard will run on: http://localhost:3000

### 3. Open in Browser
Navigate to: http://localhost:3000

## Usage

### Viewing Agents
- All agents are displayed as cards in the grid
- AI-powered agents have a purple " AI" badge
- Active/Inactive status is shown with color indicators

### Executing Agents
1. Click " Execute Agent" on any active agent card
2. Select an action from the dropdown
3. Fill in required parameters
4. Click " Execute Agent"
5. View results in real-time

### Filtering
- **Search**: Type agent name or display name
- **Filter by Status**: All / Active / Inactive / AI-Powered

## API Integration

The dashboard connects to the FastAPI backend at `http://localhost:8000`:

- `GET /agents` - Fetch all agents
- `GET /agents/metrics` - Get execution metrics
- `GET /overview` - Backend health check
- `POST /agents/execute` - Execute agent actions

## Development

### Project Structure
```
frontend-dashboard/
 app/
    page.tsx          # Main dashboard page
    layout.tsx        # Root layout
    globals.css       # Global styles
 components/
    AgentCard.tsx     # Agent card component
    ExecutionModal.tsx # Execution modal
    StatsCards.tsx    # Statistics cards
 package.json
```

### Technologies Used
- **Next.js 16** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS
- **React Hooks** - State management

## Features by Component

### AgentCard
- Displays agent information
- Shows AI-powered badge
- Active/Inactive status
- Action count
- Execute button

### ExecutionModal
- Dynamic parameter forms
- Input validation
- File path inputs
- JSON editors
- Real-time results
- Error handling

### StatsCards
- Total agents count
- Active agents
- AI-powered count
- Total executions

## Troubleshooting

### Backend Connection Issues
- Ensure backend is running on port 8000
- Check CORS settings in main.py
- Verify API endpoints are accessible

### Agent Execution Fails
- Check if agent is active
- Verify all required parameters are provided
- Ensure backend has valid API keys configured

## Next Steps

The dashboard is functional and ready to use. Future improvements could include:
- File upload functionality
- Real-time execution logs
- Agent activation/deactivation
- Execution history
- Export results

## Author

Built for CAAI - CA AI Agent System
