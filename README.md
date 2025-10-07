# 🏋️ Sentient Fitness Coach Agent

> **Built for the [Sentient Platform](https://sentient.xyz)** - Following [Sentient Agent Framework standards](https://github.com/sentient-agi/Sentient-Agent-Framework) 

An intelligent AI-powered fitness and nutrition coach compatible with the Sentient decentralized AI platform. Provides accurate calorie tracking, personalized workout plans, and real-time coaching through natural conversation.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Status: Production](https://img.shields.io/badge/status-production-success.svg)]()

<img width="1289" alt="Fitness Coach Interface" src="https://github.com/user-attachments/assets/22eb532c-1367-4606-b4fc-8d5233f4b9c6" />

---

## 🤝 Sentient Integration

This agent follows **Sentient platform API specifications** and provides:

- ✅ **REST API** endpoints compatible with Sentient standards
- ✅ **Server-Sent Events (SSE)** streaming responses
- ✅ **Health check** and capability endpoints
- ✅ **Agent metadata** and versioning
- ✅ **Production-ready** deployment with Nginx + Gunicorn
- ✅ **Web interface** for easy interaction

---

## ✨ Features

### 🍎 Nutrition Intelligence
- **Accurate calorie counting** via Nutritionix API
- Natural language food queries (*"How many calories in 3 eggs?"*)
- Detailed macronutrient breakdown (protein, carbs, fat, fiber, sugar)
- Smart food extraction from conversational questions
- Support for 200,000+ food items

### 💪 Personalized Workouts
- Custom workout plan generation based on fitness level
- 1000+ exercises database with detailed instructions
- Adaptive difficulty levels (beginner to advanced)
- Targeted muscle group training
- Duration-based workout customization

### 🧠 Smart Coaching Features
- **Real-time streaming** - Instant responses with typing effect
- **Context-aware** - Adapts recommendations to user's fitness level
- **Multi-turn conversations** - Natural back-and-forth dialogue

### 🚀 Production Features
- Server-Sent Events (SSE) for real-time streaming
- 24/7 availability with systemd auto-restart
- Nginx reverse proxy for scalability
- Comprehensive error handling and logging
- Beautiful web interface with responsive design

---

## 📋 Prerequisites

Before installation, ensure you have:

- **Operating System:** Ubuntu 22.04 (or similar Linux distribution)
- **Python:** 3.11 or higher
- **Web Server:** Nginx (will be installed)
- **API Keys** (free tiers available):
  - [OpenRouter API Key](https://openrouter.ai/) - For AI language model
  - [Nutritionix API Keys](https://nutritionix.com/business/api) - For nutrition data

---

## 🚀 Installation Guide

### Step 1: System Setup

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python 3.11 and required tools
sudo apt install python3.11 python3.11-venv python3-pip git nginx -y

# Verify Python installation
python3.11 --version
# Expected output: Python 3.11.x
```

### Step 2: Clone Repository

```bash
# Navigate to web directory
cd /var/www

# Clone the project
git clone https://github.com/kasnadoona5/sentient-fitness-coach.git

# Enter project directory
cd sentient-fitness-coach

# Verify files
ls -la
```

**You should see:** `app.py`, `agent.py`, `index.html`, `tools/`, etc.

### Step 3: Create Python Virtual Environment

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate
# Your prompt should now show (venv) at the beginning
```

### Step 4: Install Python Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install required packages
pip install flask gunicorn httpx python-dotenv

# Verify installations
pip list
```

**Required packages:** flask, gunicorn, httpx, python-dotenv

### Step 5: Get API Keys

#### 5a. OpenRouter API Key (FREE)

1. Go to [OpenRouter.ai](https://openrouter.ai/)
2. Click **"Sign In"** (use Google or GitHub)
3. Navigate to **"Keys"** section
4. Click **"Create Key"**
5. Copy the key (starts with `sk-or-v1-...`)

#### 5b. Nutritionix API Keys (FREE)

1. Go to [Nutritionix Developer Portal](https://developer.nutritionix.com/)
2. Click **"Get Your API Key"**
3. Sign up for free developer account (200 requests/day)
4. After signup, you'll receive:
   - **Application ID** (e.g., `f20efaf6`)
   - **Application Key** (e.g., `501fdbe4...`)

### Step 6: Configure Environment Variables

```bash
# Create .env file from example
cp .env.example .env

# Edit with your API keys
nano .env
```

**Update with YOUR actual keys:**

```env
# OpenRouter LLM (get from https://openrouter.ai/)
OPENROUTER_API_KEY=sk-or-v1-YOUR-ACTUAL-KEY-HERE

# Nutritionix API (get from https://nutritionix.com/business/api)
NUTRITIONIX_APP_ID=your-actual-app-id-here
NUTRITIONIX_API_KEY=your-actual-api-key-here

# Agent Configuration
AGENT_NAME=Fitness Coach
PORT=8000
APP_URL=http://your-server-ip-here

# Flask Environment
FLASK_ENV=production
```

**Save:** Press `CTRL+X`, then `Y`, then `Enter`

### Step 7: Create Required Directories

```bash
# Create logs and data directories
mkdir -p logs data

# Verify directory structure
ls -la
```

### Step 8: Test the Application

```bash
# Ensure virtual environment is active
source venv/bin/activate

# Run test server
python app.py
```

**Expected output:**
```
Running on http://0.0.0.0:8000
```

**In another terminal, test:**

```bash
# Test health endpoint
curl http://localhost:8000/health
# Expected: {"status": "healthy", ...}
```

**Stop test server:** Press `CTRL+C`

### Step 9: Create Systemd Service (Production)

```bash
sudo nano /etc/systemd/system/sentient-fitness.service
```

**Paste this configuration:**

```ini
[Unit]
Description=Sentient Fitness Coach Agent
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/sentient-fitness-coach
Environment="PATH=/var/www/sentient-fitness-coach/venv/bin"
ExecStart=/var/www/sentient-fitness-coach/venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 2 --timeout 120 wsgi:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Save and enable service:**

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable sentient-fitness.service

# Start service
sudo systemctl start sentient-fitness.service

# Check status
sudo systemctl status sentient-fitness.service
```

### Step 10: Configure Nginx Reverse Proxy

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/sentient-fitness
```

**Paste this configuration:**

```nginx
server {
    listen 80 default_server;
    server_name _;

    # Serve web interface
    location / {
        root /var/www/sentient-fitness-coach;
        index index.html;
        try_files $uri $uri/ =404;
    }

    # Proxy API requests
    location /chat {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_buffering off;
        proxy_read_timeout 300;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }
}
```

**Enable site and restart Nginx:**

```bash
# Enable the site
sudo ln -sf /etc/nginx/sites-available/sentient-fitness /etc/nginx/sites-enabled/

# Remove default site (if exists)
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx

# Check Nginx status
sudo systemctl status nginx
```

### Step 11: Final Testing

**Test API directly:**

```bash
# Test health check
curl http://localhost/health

# Test chat endpoint
curl -X POST http://localhost/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","message":"How many calories in 3 eggs?"}'
```

**Test web interface:**

Open your browser and go to: `http://YOUR_SERVER_IP/`

---

## 📡 API Reference

### Endpoint: `GET /`

Returns web chat interface (HTML)

**Response:** Beautiful web UI for interacting with the agent

### Endpoint: `GET /health`

Health check endpoint (Sentient standard)

**Response:**
```json
{
  "status": "healthy",
  "agent": "Fitness Coach AI",
  "version": "1.0.0",
  "framework": "Sentient Agent Framework"
}
```

### Endpoint: `POST /chat`

Main conversational endpoint with Server-Sent Events streaming

**Request:**
```json
{
  "user_id": "unique_user_identifier",
  "message": "Your question or request"
}
```

**Response:** SSE stream
```
data: {"content": "Based", "type": "chunk"}
data: {"content": " on", "type": "chunk"}
data: {"content": " nutrition", "type": "chunk"}
...
data: {"type": "done"}
```

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | Flask | Web framework |
| **WSGI Server** | Gunicorn | Production server |
| **LLM** | OpenRouter (Mistral Small 3.2) | AI language model |
| **Nutrition API** | Nutritionix | Food database & calorie data |
| **HTTP Client** | httpx | Async HTTP requests |
| **Memory** | JSON files | Conversation history |
| **Reverse Proxy** | Nginx | Web server & load balancing |
| **Process Manager** | Systemd | Service management & auto-restart |
| **Frontend** | HTML/CSS/JavaScript | Web interface |

---

## 📂 Project Structure

```
sentient-fitness-coach/
├── index.html              # Web chat interface
├── app.py                  # Flask application & API routes
├── wsgi.py                 # WSGI entry point for Gunicorn
├── sentient_agent.py       # Sentient-compatible agent wrapper
├── agent.py                # Core agent logic & message processing
├── llm_client.py           # OpenRouter LLM integration
├── memory.py               # User memory & conversation history
├── tools/
│   ├── nutrition.py        # Nutritionix API integration
│   └── exercise.py         # Workout plan generator
├── logs/                   # Application logs (auto-created)
├── data/                   # User data storage (auto-created)
├── .env                    # API keys (DO NOT commit!)
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

---

## 🐛 Troubleshooting

### Issue: "Module not found" errors

**Solution:**
```bash
source venv/bin/activate
pip install flask gunicorn httpx python-dotenv
```

### Issue: "API key not configured"

**Solution:** Check your `.env` file has correct API keys
```bash
cat .env | grep API
```

### Issue: Port 8000 already in use

**Solution:**
```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill the process (replace PID)
sudo kill -9 PID

# Restart service
sudo systemctl restart sentient-fitness.service
```

### Issue: Nginx 502 Bad Gateway

**Solution:**
```bash
# Check if backend is running
curl http://127.0.0.1:8000/health

# If not running, restart service
sudo systemctl restart sentient-fitness.service

# Check service logs
sudo journalctl -u sentient-fitness.service -n 50
```

---

## 📊 Monitoring & Logs

### View Application Logs

```bash
# Real-time logs
tail -f logs/agent.log

# Last 50 lines
tail -50 logs/agent.log
```

### View Service Logs

```bash
# Real-time service logs
sudo journalctl -u sentient-fitness.service -f

# Last 100 lines
sudo journalctl -u sentient-fitness.service -n 100

# Filter for errors
sudo journalctl -u sentient-fitness.service | grep -i error
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENROUTER_API_KEY` | OpenRouter API key for LLM | Yes | - |
| `NUTRITIONIX_APP_ID` | Nutritionix application ID | Yes | - |
| `NUTRITIONIX_API_KEY` | Nutritionix API key | Yes | - |
| `AGENT_NAME` | Name of the agent | No | "Fitness Coach" |
| `PORT` | Server port | No | 8000 |
| `APP_URL` | Public URL for the agent | No | - |
| `FLASK_ENV` | Flask environment | No | production |

---


## 🙏 Acknowledgments

- **Sentient Labs** - Decentralized AI platform
- **OpenRouter** - Free LLM API access
- **Nutritionix** - Comprehensive nutrition database
- **Mistral AI** - Open-source language model

---

## 📞 Support & Links

- **GitHub Repository:** https://github.com/kasnadoona5/sentient-fitness-coach
- **Report Issues:** https://github.com/kasnadoona5/sentient-fitness-coach/issues

---

## 🌟 Features Showcase

### Nutrition Tracking
Ask questions like:
- "How many calories in 3 eggs?"
- "What's the protein content in chicken breast?"
- "Nutrition facts for 1 cup of oatmeal"

**Response:** Accurate calorie and macronutrient data from Nutritionix API

### Workout Plans
Ask for workouts like:
- "Create a beginner workout plan"
- "Give me a 30-minute chest workout"
- "I want to build muscle, what exercises should I do?"

**Response:** Personalized workout plans with exercises, sets, reps, and instructions

### Conversation Memory
The agent remembers your preferences:
- "What did I ask about earlier?"
- "Remember my fitness goals"

**Response:** Context-aware responses based on conversation history

---

<img width="961" alt="Chat Interface Demo" src="https://github.com/user-attachments/assets/91d7f96a-4e9b-4b5d-85f2-881072cfb48b" />

---

**Built with ❤️ for the Sentient decentralized AI network**
