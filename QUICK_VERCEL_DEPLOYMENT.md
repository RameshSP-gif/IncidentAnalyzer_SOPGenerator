# Quick Vercel Deployment (5 Minutes)

## TL;DR - Deploy Now

### Step 1: Create MongoDB Atlas (2 min)
```
1. Go to https://www.mongodb.com/cloud/atlas
2. Sign up → Create free cluster
3. Create user: incident_user (auto password)
4. Network Access → Allow 0.0.0.0/0
5. Copy connection string → Save it
```

### Step 2: Deploy to Vercel (2 min)
```
1. Go to https://vercel.com
2. Import: IncidentAnalyzer_SOPGenerator repo
3. Add Environment Variable:
   - MONGODB_URI = <your connection string from Step 1>
4. Click Deploy
```

### Step 3: Verify (1 min)
```
- Visit: https://your-app.vercel.app
- Test upload CSV file
- Check /manage for knowledge base
```

---

## ✅ What's Already Configured

- ✅ `vercel.json` - Deployment config ready
- ✅ `api/index.py` - Serverless function entry point
- ✅ `requirements.txt` - All dependencies included
- ✅ `.vercelignore` - Optimized build size
- ✅ GitHub repo - Already contains all code

## 🔑 Key Files Needed

| File | Purpose | Status |
|------|---------|--------|
| `vercel.json` | Build & routing config | ✅ Created |
| `api/index.py` | Serverless entry point | ✅ Created |
| `requirements.txt` | Python dependencies | ✅ Updated |
| `.vercelignore` | Build optimization | ✅ Created |
| MongoDB URI | Environment variable | 📋 From Atlas |

## 🚀 Deployment Flow

```
1. Create MongoDB Cluster
   ↓
2. Get Connection String  
   ↓
3. Connect GitHub to Vercel
   ↓
4. Add MONGODB_URI as environment variable
   ↓
5. Deploy (automatic)
   ↓
6. App live at: https://your-project-name.vercel.app
```

## 📊 Live Application Features

Once deployed, you get:

| Feature | URL | Details |
|---------|-----|---------|
| **Main UI** | `/` | Upload CSV, generate SOP |
| **Knowledge Base** | `/manage` | View/Edit/Delete incidents |
| **API** | `/api/*` | Programmatic access |
| **Status** | All endpoints work 24/7 with auto-scaling |

## 💾 Data Storage

- **All data** → MongoDB Atlas (cloud database)
- **All files** → Vercel CDN (static files)
- **Logs** → Vercel Dashboard

## 🎯 First 30 Seconds After Deploy

1. Click "Visit" button in Vercel dashboard
2. Should see upload interface
3. Test: Upload `SAMPLE_DATA_TEST.html` or create CSV
4. Click "/manage" link
5. Should see incidents with pagination

## ⚠️ Common Issues

### "MongoDB connection failed"
→ Check environment variable MONGODB_URI in Vercel dashboard

### "Build failed"  
→ Check Vercel build logs for error
→ Ensure Python 3.11+ is available

### "Static files not showing"
→ Clear browser cache (Ctrl+Shift+Del)
→ Refresh page

### "Upload returns 413"
→ File too large (Vercel max ~5MB per request)
→ Split into smaller files

## 🔒 Security Checklist

- ⚠️ **IMPORTANT**: Database user password is visible in MONGODB_URI
- [ ] Use environment variables (already done in vercel.json)
- [ ] For production: Use IP whitelist instead of 0.0.0.0/0
- [ ] Enable MongoDB encryption (free tier includes it)

## 📈 Expected Performance

| Metric | Value | Notes |
|--------|-------|-------|
| **Startup Time** | 2-3 sec | First cold start |
| **Response Time** | <500ms | Typical request |
| **Concurrent Users** | 3 | Free MongoDB limit |
| **Storage** | 512MB | Free MongoDB tier |
| **Uptime** | 99.95% | Vercel SLA |

## 🆘 If Something Goes Wrong

1. **Check Vercel logs:**
   - Dashboard → Deployments → Click latest → Function Logs

2. **Check MongoDB status:**
   - Atlas Dashboard → Cluster → Overview

3. **Redeploy:**
   - Vercel Dashboard → Deployments → Click Redeploy button

4. **Manual debugging:**
   - See VERCEL_DEPLOYMENT.md for detailed troubleshooting

## 📱 Share Your App

Once live, share the URL:
```
🎉 Check out my Incident Analyzer!
https://your-project-name.vercel.app

Features:
- 📊 Generate SOPs from incidents
- 🔍 Search knowledge base
- 💾 Cloud-hosted with MongoDB
```

## 📚 Full Documentation

For detailed setup, troubleshooting, and production deployment:
→ See **VERCEL_DEPLOYMENT.md** in the repo

---

**Estimated Time:** 5-10 minutes  
**Cost:** FREE (for development)  
**Ready to Deploy:** ✅ Yes  
