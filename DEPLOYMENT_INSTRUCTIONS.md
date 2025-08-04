# Cafe24 Automation Server - Deployment Instructions

## 🚀 Complete Deployment Guide

### 1. Repository Information
- **GitHub Repository**: https://github.com/manwonyori/cafe24-automation
- **Live Demo**: https://cafe24-automation.onrender.com

### 2. Render.com Deployment Steps

#### Step 1: Connect GitHub Repository
1. Go to https://dashboard.render.com/
2. Click "New +" → "Web Service"
3. Connect your GitHub account
4. Select repository: `manwonyori/cafe24-automation`
5. Branch: `master`

#### Step 2: Service Configuration
- **Name**: `cafe24-automation`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python app.py`

#### Step 3: Environment Variables
Copy and paste these EXACT environment variables:

```
CAFE24_MALL_ID=manwonyori
CAFE24_CLIENT_ID=9bPpABwHB5mtkCEAfIeuNK
CAFE24_CLIENT_SECRET=qtnWtUk2OZzua1SRa7gN3A
CAFE24_REDIRECT_URI=https://cafe24-automation.onrender.com/callback
CAFE24_ACCESS_TOKEN=V6G4Dzp6xvki7EKmpjKT9jg62Zgosyk7RguBwiwt/j4=
CAFE24_REFRESH_TOKEN=KIOmihlDK9roYKGWOo8vAA
CAFE24_API_VERSION=2025-06-01
ENABLE_AUTO_REFRESH=true
ENABLE_DASHBOARD=true
ENABLE_API_ENDPOINTS=true
PRODUCTION_MODE=true
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1
PORT=5000
```

#### Step 4: Deploy
1. Click "Create Web Service"
2. Wait for deployment to complete (~5-10 minutes)
3. Your service will be available at: `https://cafe24-automation.onrender.com`

### 3. API Endpoints

Once deployed, these endpoints will be available:

- **Status Check**: `GET /api/status`
- **Products List**: `GET /api/products`
- **Today's Orders**: `GET /api/orders/today`
- **Categories**: `GET /api/categories`

### 4. Features

✅ **Automatic Token Refresh**: The system automatically refreshes OAuth tokens every hour
✅ **Error Recovery**: Handles token expiration and API errors gracefully
✅ **Production Ready**: Optimized for production deployment
✅ **Real-time Data**: Live connection to Cafe24 API
✅ **Comprehensive Logging**: Full request/response logging for debugging

### 5. Testing the Deployment

After deployment, test these URLs:

1. **Service Status**: https://cafe24-automation.onrender.com/api/status
2. **Products API**: https://cafe24-automation.onrender.com/api/products?limit=5
3. **Orders API**: https://cafe24-automation.onrender.com/api/orders/today

### 6. Troubleshooting

If you encounter issues:

1. **500 Errors**: Check Render logs for token refresh issues
2. **401 Unauthorized**: Token may be expired, will auto-refresh in background
3. **Deployment Fails**: Ensure environment variables are exactly as provided above

### 7. Success Indicators

✅ `/api/status` returns `"status": "ok"`
✅ `/api/products` returns product data
✅ `/api/orders/today` returns order data
✅ Logs show "자동 토큰 갱신 스케줄러 시작" message

## 🎉 You're Done!

Your Cafe24 automation system is now live and fully functional. The system will automatically handle token refreshing and maintain API connectivity.

**Live Service**: https://cafe24-automation.onrender.com