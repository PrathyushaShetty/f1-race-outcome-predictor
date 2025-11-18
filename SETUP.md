# 🏎️ F1 Race Outcome Predictor - Setup Guide

This guide will help you set up and run the F1 Race Outcome Predictor application on your local machine.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 16+** - [Download Node.js](https://nodejs.org/) (for web interface)
- **PostgreSQL 14+** - [Download PostgreSQL](https://www.postgresql.org/download/)
- **Redis** - [Download Redis](https://redis.io/download) (optional, for caching)
- **Git** - [Download Git](https://git-scm.com/downloads)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/PrathyushaShetty/f1-race-outcome-predictor.git
cd f1-race-outcome-predictor
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
# You'll need to set database credentials and API keys
```

### 4. Set Up Database

```bash
# Create PostgreSQL database
createdb f1_predictor

# Initialize database schema and sample data
python scripts/init_db.py
```

### 5. Start the Application

```bash
# Option 1: Use the startup script (recommended)
python start.py

# Option 2: Start services manually
# Terminal 1 - API Server
python app/main.py

# Terminal 2 - Live Prediction Service
python services/live_predictor.py

# Terminal 3 - Web Interface (optional)
cd web
npm install
npm start
```

## 🔧 Detailed Setup

### Environment Configuration

Edit the `.env` file with your specific configuration:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/f1_predictor

# API Keys (optional but recommended)
F1_API_KEY=your_f1_api_key_here
WEATHER_API_KEY=your_openweather_api_key_here

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379/0

# Application Settings
DEBUG=False
LOG_LEVEL=INFO
SECRET_KEY=your_secret_key_here
```

### Database Setup

1. **Install PostgreSQL** and create a database:
   ```sql
   CREATE DATABASE f1_predictor;
   CREATE USER f1_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE f1_predictor TO f1_user;
   ```

2. **Run the initialization script**:
   ```bash
   python scripts/init_db.py
   ```

   This will:
   - Create all necessary tables
   - Populate sample data
   - Set up indexes for performance

### API Keys (Optional)

To get real-time data, you may want to obtain API keys:

- **F1 API**: For live timing data (if available)
- **OpenWeatherMap**: For weather forecasts - [Get API Key](https://openweathermap.org/api)

### Web Interface Setup

```bash
cd web
npm install
npm start
```

The web interface will be available at `http://localhost:3000`

## 📊 Usage

### API Endpoints

Once running, the API will be available at `http://localhost:8000`

#### Pre-Race Predictions
```bash
GET /api/v1/predictions/pre-race/bahrain-2024
```

#### Live Race Predictions
```bash
GET /api/v1/predictions/live/bahrain-2024
```

#### Fan Predictions
```bash
POST /api/v1/fans/predictions
{
  "user_id": "user123",
  "race_id": "bahrain-2024",
  "winner_prediction": "Max Verstappen",
  "podium_predictions": ["Max Verstappen", "Lewis Hamilton", "Charles Leclerc"]
}
```

### WebSocket Connection

Connect to live predictions via WebSocket:

```javascript
const socket = new WebSocket('ws://localhost:8001/live/bahrain-2024');

socket.onmessage = function(event) {
    const prediction = JSON.parse(event.data);
    console.log('Live prediction:', prediction);
};
```

### Web Interface

Visit `http://localhost:3000` to access:

- **Dashboard**: Overview of predictions and statistics
- **Live Race**: Real-time race predictions and updates
- **Predictions**: Submit and view race predictions
- **Leaderboard**: Fan prediction rankings

## 🔍 Testing

### API Testing

```bash
# Test API health
curl http://localhost:8000/health

# Test prediction endpoint
curl http://localhost:8000/api/v1/predictions/pre-race/bahrain-2024
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
```

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure PostgreSQL is running
   - Check database credentials in `.env`
   - Verify database exists

2. **Import Errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

3. **Port Already in Use**
   - Change ports in configuration
   - Kill existing processes: `lsof -ti:8000 | xargs kill -9`

4. **Web Interface Not Loading**
   - Ensure Node.js is installed
   - Run `npm install` in web directory
   - Check for port conflicts

### Logs

Check application logs for debugging:

```bash
# Application logs
tail -f logs/f1_predictor.log

# Error logs
tail -f logs/f1_predictor_errors.log
```

## 📈 Performance Optimization

### Database Optimization

```sql
-- Create additional indexes for better performance
CREATE INDEX idx_race_results_race_id ON race_results(race_id);
CREATE INDEX idx_predictions_race_id ON predictions(race_id);
CREATE INDEX idx_fan_predictions_user_id ON fan_predictions(user_id);
```

### Redis Caching

Enable Redis for better performance:

```bash
# Install Redis
# Ubuntu/Debian: sudo apt-get install redis-server
# macOS: brew install redis
# Windows: Download from Redis website

# Start Redis
redis-server
```

## 🔄 Updates and Maintenance

### Model Updates

Models are automatically retrained based on the schedule in `config/models.yaml`. To manually trigger updates:

```bash
curl -X POST http://localhost:8000/api/v1/predictions/update-models
```

### Data Updates

The system automatically fetches new race data. To manually update:

```bash
python scripts/update_data.py
```

### Backup

Regular backups are recommended:

```bash
# Database backup
pg_dump f1_predictor > backup_$(date +%Y%m%d).sql

# Model backup
tar -czf models_backup_$(date +%Y%m%d).tar.gz models/
```

## 🚀 Production Deployment

For production deployment, consider:

1. **Use environment variables** for all configuration
2. **Set up proper logging** and monitoring
3. **Use a production WSGI server** like Gunicorn
4. **Set up reverse proxy** with Nginx
5. **Enable SSL/TLS** for secure connections
6. **Set up database connection pooling**
7. **Configure Redis** for session management
8. **Set up automated backups**

### Docker Deployment

```bash
# Build Docker image
docker build -t f1-predictor .

# Run with Docker Compose
docker-compose up -d
```

## 📞 Support

If you encounter any issues:

1. Check the [troubleshooting section](#-troubleshooting)
2. Review application logs
3. Open an issue on GitHub
4. Contact the development team

## 🎯 Next Steps

After setup, you can:

1. **Explore the API** using the interactive docs at `http://localhost:8000/docs`
2. **Submit test predictions** via the web interface
3. **Monitor live races** during race weekends
4. **Customize models** by editing `config/models.yaml`
5. **Add new features** by extending the codebase

Happy racing! 🏁
