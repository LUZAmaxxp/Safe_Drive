# Deploying Safe Drive to Vercel

## Overview

This guide explains how to deploy the Safe Drive application to Vercel. Note that **only the frontend can be deployed to Vercel** because:

1. Vercel is optimized for static sites and serverless functions
2. The Flask backend requires continuous webcam access
3. The backend uses heavy ML libraries (OpenCV, dlib, TensorFlow) that are not suitable for serverless

## Architecture

```
Frontend (Vercel) → Backend API (Separate Hosting)
```

You'll need to deploy:
- **Frontend**: Vercel (this guide)
- **Backend**: Railway, Render, or similar Python-friendly platform

---

## Prerequisites

1. A Vercel account ([vercel.com](https://vercel.com))
2. Vercel CLI installed: `npm i -g vercel`
3. Your backend deployed elsewhere (see Backend Deployment section)

---

## Step 1: Deploy Backend First

The backend must be deployed **before** the frontend. Recommended platforms:

### Option A: Railway (Recommended)
1. Go to [railway.app](https://railway.app)
2. Create new project → Deploy from GitHub repo
3. Select your repository
4. Railway will auto-detect Python
5. Set environment variables in Railway dashboard
6. Railway will provide a URL like: `https://your-app.railway.app`

### Option B: Render
1. Go to [render.com](https://render.com)
2. Create new Web Service
3. Connect your GitHub repo
4. Build command: `pip install -r requirements.txt`
5. Start command: `python app.py`
6. Render will provide a URL

### Option C: PythonAnywhere
1. Go to [pythonanywhere.com](https://pythonanywhere.com)
2. Upload files via web interface
3. Configure web app
4. Note: Free tier has limitations for ML apps

---

## Step 2: Deploy Frontend to Vercel

### Method A: Deploy via Vercel Dashboard (Easiest)

1. **Push your code to GitHub** (if not already done)
   ```bash
   git add .
   git commit -m "Ready for Vercel deployment"
   git push origin main
   ```

2. **Go to [vercel.com](https://vercel.com)**
   - Sign in with GitHub

3. **Import your project**
   - Click "Add New Project"
   - Select your Safe_Drive repository
   - Vercel will auto-detect settings

4. **Configure environment variables**
   - Add environment variable:
     - Key: `REACT_APP_API_URL`
     - Value: `https://your-backend-url.railway.app/api`
     (Replace with your actual backend URL)

5. **Deploy**
   - Click "Deploy"
   - Wait for build to complete
   - Your app will be live at `https://your-app.vercel.app`

### Method B: Deploy via CLI

1. **Install Vercel CLI** (if not installed)
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Navigate to project directory**
   ```bash
   cd c:\Users\pc\Desktop\Safe_Drive
   ```

4. **Set environment variable**
   ```bash
   vercel env add REACT_APP_API_URL
   # Enter your backend URL when prompted
   ```

5. **Deploy**
   ```bash
   vercel --prod
   ```

---

## Step 3: Update Vercel Settings

After deployment, configure the following in Vercel dashboard:

### Root Directory
1. Go to Project Settings → General
2. Root Directory: Set to `frontend` (or leave empty if deploying from root)

### Build Settings
- Framework Preset: Other
- Build Command: `cd frontend && npm install && npm run build`
- Output Directory: `frontend/build`
- Install Command: `cd frontend && npm install`

### Environment Variables
Add these in Settings → Environment Variables:
- `REACT_APP_API_URL`: Your backend API URL
  - Example: `https://your-backend.railway.app/api`

---

## Step 4: Verify Deployment

1. Visit your Vercel URL
2. Check browser console for errors
3. Try starting monitoring (camera won't work locally, but API calls should work)

---

## Updating the Frontend

After initial deployment, updates are automatic:

```bash
# Make your changes
git add .
git commit -m "Your changes"
git push origin main

# Vercel will automatically redeploy
```

Or manually trigger:

```bash
vercel --prod
```

---

## Troubleshooting

### Build Fails
- **Error**: "Cannot find module"
  - Solution: Check that `frontend/node_modules` is in .gitignore
  - Vercel installs dependencies automatically

- **Error**: "Environment variable not found"
  - Solution: Add `REACT_APP_API_URL` in Vercel dashboard

### API Connection Issues
- **Error**: "Network Error" or CORS
  - Solution: Ensure backend has CORS enabled
  - Check backend is accessible from browser
  - Verify `REACT_APP_API_URL` is correct

### Camera Not Working
- **Expected**: Camera cannot work on web servers
- This app requires local backend for webcam access
- Consider alternative architecture for production

---

## Current Limitations

Due to browser security, this application has limitations in a production environment:

1. **Camera Access**: Requires backend on same machine
2. **Security**: CORS and HTTPS requirements
3. **WebRTC**: Would require WebRTC implementation for remote camera

---

## Alternative Architectures

For a fully web-based solution, consider:

### Option 1: WebRTC + PeerJS
- Client captures camera in browser
- Stream to backend via WebRTC
- More complex but fully web-based

### Option 2: Browser ML (TensorFlow.js)
- Run emotion detection in browser
- No backend needed for detection
- Limited by browser performance

### Option 3: Hybrid Approach
- Deploy frontend on Vercel
- Deploy backend on Railway/Render
- Use WebSockets for real-time data
- Client-side camera capture

---

## Environment Variables Summary

### Frontend (Vercel)
```env
REACT_APP_API_URL=https://your-backend.railway.app/api
```

### Backend (Railway/Render)
```env
SECRET_KEY=your-secret-key
DEBUG=False
CAMERA_INDEX=0
FRAME_SKIP=1
```

---

## Next Steps

1. ✅ Deploy backend to Railway/Render
2. ✅ Deploy frontend to Vercel
3. ✅ Configure environment variables
4. ✅ Test deployment
5. ⚠️ Note: Full camera functionality requires local backend

---

## Support

If you encounter issues:
1. Check Vercel deployment logs
2. Check backend logs
3. Check browser console
4. Verify environment variables
5. Review CORS settings

---

## Useful Links

- [Vercel Documentation](https://vercel.com/docs)
- [Railway Documentation](https://docs.railway.app)
- [Render Documentation](https://render.com/docs)
- [React Build Configuration](https://create-react-app.dev/docs/deployment/)

---

**Note**: This application works best when running backend locally. For production, consider the alternative architectures mentioned above.

