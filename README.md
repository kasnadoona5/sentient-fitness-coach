# 🏋️ Sentient Fitness Coach Agent

> **Built with [Sentient Agent Framework](https://github.com/sentient-agi/Sentient-Agent-Framework)** - Production-ready AI agent with intelligent coaching capabilities

An AI-powered fitness and nutrition coach that provides accurate calorie tracking, personalized workout plans, and intelligent coaching through natural conversation. Built using the official Sentient Agent Framework with AI-powered intent classification.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Sentient Framework](https://img.shields.io/badge/framework-Sentient-blue.svg)](https://github.com/sentient-agi/Sentient-Agent-Framework)
[![Status: Production](https://img.shields.io/badge/status-production-success.svg)]()

<img width="1289" alt="Fitness Coach Interface" src="https://github.com/user-attachments/assets/22eb532c-1367-4606-b4fc-8d5233f4b9c6" />

---

## 🚀 New in v2.0

✨ **AI-Powered Intent Classification** - Automatically detects nutrition queries without hardcoded food lists  
✨ **Typo Tolerance** - Handles common misspellings ("colories", "calory")  
✨ **Zero Hallucination** - Only uses real Nutritionix API data for calories  
✨ **Smart Compound Queries** - Handles multiple foods in one request  
✨ **Free Tier Model** - Uses Mistral Small 3.2 24B (131K context) completely free  
✨ **Conversation Memory** - Backend memory maintains context across messages  

---

## 🤝 Sentient Framework Integration

This agent is built with the **official Sentient Agent Framework** and provides:

- ✅ **AbstractAgent** implementation following Sentient standards
- ✅ **Server-Sent Events (SSE)** streaming responses
- ✅ **Session management** with user tracking
- ✅ **Async/await** architecture for optimal performance
- ✅ **Production-ready** deployment with systemd + Nginx

---

## ✨ Features

### 🍎 Nutrition Intelligence
- **Accurate calorie counting** via Nutritionix API
- **AI-powered food detection** - No hardcoded food lists
- Natural language queries (*"How many calories in 3 eggs?"*)
- **Typo tolerance** (*"How many colories in avocado?"*)
- Detailed macronutrient breakdown (protein, carbs, fat, fiber, sugar)
- **Compound query support** (*"3 eggs and 2 slices of toast"*)
- Support for 200,000+ food items

### 💪 Personalized Workouts
- **Interactive plan generation** - Asks clarifying questions
- Custom workout plans based on fitness level, goals, equipment
- Progressive difficulty levels (beginner to advanced)
- Targeted muscle group training
- Home workouts (no equipment) to gym-based programs

### 🧠 Smart Coaching Features
- **AI-powered intent classification** - Knows when to use API vs provide advice
- **Real-time streaming** - Instant responses with Server-Sent Events
- **Context-aware** - Adapts recommendations to user's fitness level
- **Conversation memory** - Remembers previous messages in the session
- **Interactive coaching** - Asks questions before creating plans

### 🚀 Production Features
- Built on official **Sentient Agent Framework**
- Server-Sent Events (SSE) for real-time streaming
- 24/7 availability with systemd auto-restart
- Nginx reverse proxy for scalability
- Comprehensive error handling and logging
- Beautiful responsive web interface

---

## 📋 Prerequisites

Before installation, ensure you have:

- **Operating System:** Ubuntu 22.04 (or similar Linux distribution)
- **Python:** 3.11 or higher
- **Web Server:** Nginx (will be installed)
- **API Keys** (free tiers available):
  - [OpenRouter API Key](https://openrouter.ai/) - For AI language model (FREE)
  - [Nutritionix API Keys](https://nutritionix.com/business/api) - For nutrition data (FREE tier: 200 requests/day)

---

## 🚀 Installation Guide

### Step 1: System Setup

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install software-properties-common (needed for adding PPA)
sudo apt install software-properties-common -y

#Add deadsnakes PPA for Python 3.11+
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

#Install Python 3.11, venv, pip, and required tools
sudo apt install python3.11 python3.11-venv python3.11-dev git nginx -y

#Verify Python 3.11 installation (required for Sentient Framework)
python3.11 --version
```



### Step 2: Clone Repository

```bash
# Navigate to web directory
cd /var/www

# Clone the project
git clone https://github.com/kasnadoona5/sentient-fitness-coach.git

# Enter project directory
cd sentient-fitness-coach
```

### Step 3: Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
# Your prompt should now show (venv)
```

### Step 4: Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install sentient-agent-framework httpx python-dotenv

# Verify installations
pip list | grep -E "sentient|httpx|dotenv"
```

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
3. Sign up for free developer account
4. After signup, you'll receive:
   - **Application ID** (e.g., `f20efaf6`)
   - **Application Key** (e.g., `501fdbe4...`)

### Step 6: Configure Environment Variables

```bash
# Create .env file
nano .env
```

**Paste and update with YOUR actual keys:**

```env
# OpenRouter LLM (get from https://openrouter.ai/)
OPENROUTER_API_KEY=sk-or-v1-YOUR-ACTUAL-KEY-HERE

# Nutritionix API (get from https://nutritionix.com/business/api)
NUTRITIONIX_APP_ID=your-actual-app-id-here
NUTRITIONIX_API_KEY=your-actual-api-key-here
```

**Save:** Press `CTRL+X`, then `Y`, then `Enter`

### Step 7: Test the Application

```bash
# Ensure virtual environment is active
source venv/bin/activate

# Run test server
python app.py
```

**Expected output:**
```
INFO: Started server process
INFO: Waiting for application startup.
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:8000
```

**In another terminal, test:**

```bash
# Test API endpoint
curl -X POST http://localhost:8000/assist \
  -H "Content-Type: application/json" \
  -d '{
    "session": {
      "user_id": "test",
      "session_id": "test123",
      "processor_id": "test123",
      "activity_id": "test123",
      "request_id": "test123",
      "interactions": []
    },
    "query": {
      "id": "test123",
      "prompt": "hello"
    }
  }'
```

**Stop test server:** Press `CTRL+C`

### Step 8: Create Systemd Service (Production)

```bash
sudo nano /etc/systemd/system/sentient-fitness.service
```

**Paste this configuration:**

```ini
[Unit]
Description=Sentient Fitness Coach Agent (Framework)
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/sentient-fitness-coach
Environment="PATH=/var/www/sentient-fitness-coach/venv/bin"
ExecStart=/var/www/sentient-fitness-coach/venv/bin/python app.py
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

### Step 9: Configure Nginx Reverse Proxy

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

    # Proxy API requests to Sentient Agent Framework
    location /assist {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_cache_bypass $http_upgrade;
        
        # SSE support
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
```

**Enable site and restart Nginx:**

```bash
# Enable the site
sudo ln -sf /etc/nginx/sites-available/sentient-fitness /etc/nginx/sites-enabled/

# Remove default site
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### Step 10: Final Testing

**Test web interface:**

Open your browser: `http://YOUR_SERVER_IP/`

Try these queries:
- "How many calories in 3 eggs?"
- "What should I eat before gym?"
- "Create a beginner workout plan"

---

## 📡 API Reference

### Endpoint: `POST /assist`

Main agent endpoint following Sentient Framework standards

**Request:**
```json
{
  "session": {
    "user_id": "unique_user_id",
    "session_id": "session_123",
    "processor_id": "proc_123",
    "activity_id": "act_123",
    "request_id": "req_123",
    "interactions": []
  },
  "query": {
    "id": "query_123",
    "prompt": "How many calories in 3 eggs?"
  }
}
```

**Response:** Server-Sent Events stream
```
event: response
data: {"content_type":"chunked.text","event_name":"response","is_complete":false,"content":"Based on..."}

event: response
data: {"content_type":"chunked.text","event_name":"response","is_complete":true,"content":" "}
```

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Framework** | Sentient Agent Framework | Agent architecture & SSE streaming |
| **Backend** | Python 3.10+ asyncio | Async event handling |
| **LLM** | Mistral Small 3.2 24B (free) | AI language model via OpenRouter |
| **Nutrition API** | Nutritionix | Food database & calorie data |
| **HTTP Client** | httpx | Async HTTP requests |
| **Memory** | In-memory dict | Conversation history (resets on restart) |
| **Reverse Proxy** | Nginx | Web server & SSE support |
| **Process Manager** | Systemd | Service management & auto-restart |
| **Frontend** | HTML/CSS/JavaScript | Web interface |

---

## 📂 Project Structure

```
sentient-fitness-coach/
├── app.py                  # Main agent implementation (Sentient Framework)
├── index.html              # Web chat interface
├── .env                    # API keys (DO NOT commit!)
├── .gitignore              # Git ignore rules
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

**Simple, clean, production-ready!**

---

## 🐛 Troubleshooting

### Issue: "Module not found: sentient_agent_framework"

**Solution:**
```bash
source venv/bin/activate
pip install sentient-agent-framework
```

### Issue: "API key not configured"

**Solution:** Check your `.env` file has correct API keys
```bash
cat .env
```

### Issue: Port 8000 already in use

**Solution:**
```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill the process
sudo kill -9 PID

# Restart service
sudo systemctl restart sentient-fitness.service
```

### Issue: Input disabled after first message

**Solution:** Clear browser cache (CTRL+SHIFT+R) - This was fixed in v2.0

### Issue: Agent gives wrong calorie estimates

**Solution:** Agent now uses ONLY Nutritionix API data - no more hallucinations!

---

## 📊 Monitoring & Logs

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

---

## 🌟 Features Showcase

### 1. Accurate Nutrition Data
```
You: "How many calories in 3 large eggs?"
Agent: "Based on the Nutritionix API data, 3 large eggs (150g) contain 214.5 kcal.
        Protein: 18.8g | Carbs: 1.1g | Fat: 14.3g"
```

### 2. Typo Tolerance
```
You: "How many colories are in 2 bananas?"
Agent: "Based on the Nutritionix API, 2 medium bananas contain 210.0 kcal..."
```

### 3. AI Food Detection
```
You: "avocado nutrition"
Agent: "Based on the Nutritionix API, 1 avocado (201g) contains 321.6 kcal..."
```

### 4. Interactive Coaching
```
You: "Create a beginner workout plan"
Agent: "I'd be happy to help! To create the best plan for you, could you tell me:
        1. Your main goal (weight loss, muscle gain, general fitness)
        2. How many days per week you'd like to work out
        3. What equipment do you have access to?..."
```

### 5. Conversation Memory
```
You: "I want to workout at home with no equipment"
Agent: "Great! Could you tell me your fitness level?"
You: "beginner"
Agent: "Thank you! Since you're a beginner working out at home without equipment,
        here's your 4-week beginner home workout plan..."
```

---

## 🎯 Testing Results

All 7 test cases passed with 100% accuracy:

✅ Specific nutrition queries (API data)  
✅ Typo tolerance (colories → calories)  
✅ General advice (no hallucination)  
✅ Workout plan generation  
✅ AI food detection (avocado, sushi, etc.)  
✅ Compound queries (multiple foods)  
✅ Conversation memory  

---

## 🙏 Acknowledgments

- **[Sentient Agent Framework](https://github.com/sentient-agi/Sentient-Agent-Framework)** - Official framework for building production agents
- **OpenRouter** - Free LLM API access with Mistral Small 3.2 24B
- **Nutritionix** - Comprehensive nutrition database (200,000+ foods)
- **Mistral AI** - High-quality open-source language model

---

## 📞 Support & Links

- **GitHub Repository:** https://github.com/kasnadoona5/sentient-fitness-coach
- **Report Issues:** https://github.com/kasnadoona5/sentient-fitness-coach/issues
- **Sentient Framework:** https://github.com/sentient-agi/Sentient-Agent-Framework

---

<img width="961" alt="Chat Interface Demo" src="https://github.com/user-attachments/assets/91d7f96a-4e9b-4b5d-85f2-881072cfb48b" />

---

**Built with ❤️ using Sentient Agent Framework**
