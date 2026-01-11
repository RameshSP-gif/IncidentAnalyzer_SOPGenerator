# Vercel Cloud Deployment Guide

## Overview
This guide walks you through deploying the Incident Analyzer & SOP Generator on Vercel cloud platform.

## Prerequisites

1. **GitHub Account** - Your code is already on GitHub
2. **Vercel Account** - Create free account at https://vercel.com
3. **MongoDB Atlas Account** - Create free cluster at https://www.mongodb.com/cloud/atlas

## Step 1: Set Up MongoDB Atlas

### 1.1 Create MongoDB Cluster
1. Go to https://www.mongodb.com/cloud/atlas
2. Create a free account or sign in
3. Create a new project named "IncidentAnalyzer"
4. Create a **M0 (free) cluster**
   - Choose AWS as provider
   - Select closest region
   - Wait 3-5 minutes for cluster creation

### 1.2 Create Database User
1. In MongoDB Atlas, go to **Database Access**
2. Create a new database user
   - Username: `incident_user`
   - Auto-generate secure password
   - Copy and save the password securely
3. Grant **Read and write to any database** role

### 1.3 Whitelist IP & Get Connection String
1. Go to **Network Access**
2. Click **Add IP Address** → Select "Allow Access from Anywhere" (0.0.0.0/0)
   - ⚠️ Note: For production, use specific IPs. This is fine for development.
3. Go to **Database** → Click **Connect** → **Drivers**
4. Select **Python 3.6 or later**
5. Copy the connection string:
   ```
   mongodb+srv://incident_user:<password>@cluster0.xxxxx.mongodb.net/incident_analyzer?retryWrites=true&w=majority
   ```
6. Replace `<password>` with your actual password

## Step 2: Deploy to Vercel

### 2.1 Connect GitHub Repository
1. Go to https://vercel.com/dashboard
2. Click **Add New...** → **Project**
3. Import your GitHub repository: `IncidentAnalyzer_SOPGenerator`
4. Vercel will auto-detect the project structure

### 2.2 Configure Environment Variables
1. In Vercel project settings, go to **Environment Variables**
2. Add the following variables:

| Name | Value | Notes |
|------|-------|-------|
| `MONGODB_URI` | `mongodb+srv://incident_user:PASSWORD@cluster0.xxxxx.mongodb.net/incident_analyzer?retryWrites=true&w=majority` | Your MongoDB connection string (replace PASSWORD) |
| `FLASK_ENV` | `production` | Production environment |

### 2.3 Deploy
1. Click **Deploy**
2. Wait for build to complete (2-3 minutes)
3. Your app is live at: `https://your-project-name.vercel.app`

## Step 3: Verify Deployment

### 3.1 Test Main Interface
- Visit: `https://your-project-name.vercel.app/`
- You should see the Incident Analyzer UI with upload interface

### 3.2 Test Knowledge Base Management
- Visit: `https://your-project-name.vercel.app/manage`
- Should show Knowledge Base Management interface with pagination

### 3.3 Test API Endpoints
```bash
# Get knowledge base
curl https://your-project-name.vercel.app/get_knowledge_base

# Upload and generate SOP
curl -X POST https://your-project-name.vercel.app/upload_file \
  -F "file=@sample.csv"
```

## Step 4: Load Sample Data

### 4.1 Using Web Interface
1. Download sample CSV from repository or create test incidents
2. Upload via web interface: `https://your-project-name.vercel.app/`
3. Data automatically saves to MongoDB Atlas

### 4.2 Using API
```bash
curl -X POST https://your-project-name.vercel.app/add_incident \
  -H "Content-Type: application/json" \
  -d '{
    "number": "INC001",
    "short_description": "Database Connection Timeout",
    "details": "Application unable to connect to database",
    "resolution_notes": "Restarted database service. Verified connection pooling settings.",
    "category": "Database"
  }'
```

## Vercel Deployment Architecture

```
┌─────────────────────────┐
│    Your Vercel App      │
│  yourapp.vercel.app     │
└───────────┬─────────────┘
            │
     ┌──────┴──────────┐
     │                 │
┌────▼──────┐   ┌─────▼──────────────┐
│   Static  │   │   Flask API        │
│  Files    │   │   Serverless Fn    │
│  (CSS/JS) │   │                    │
└───────────┘   └────────┬───────────┘
                         │
                ┌────────▼──────────┐
                │  MongoDB Atlas    │
                │  Cloud Database   │
                └───────────────────┘
```

## Configuration Details

### vercel.json
- Specifies Python 3.11 runtime
- Routes all requests to Flask app
- Caches static files (CSS/JS) for 1 hour
- Loads environment variables from Vercel dashboard

### api/index.py
- Serverless function entry point
- Imports Flask app and exports as handler
- Vercel automatically runs this for all requests

## Important Notes

### MongoDB Atlas Free Tier Limits
- ✅ 512MB storage (sufficient for sample data)
- ✅ Shared cluster (good for development)
- ✅ No automatic backups
- ⚠️ 3 simultaneous connections
- 📈 Upgrade to M2 ($9/month) for production with:
  - Automatic backups
  - Higher connection limits
  - Better performance

### Vercel Free Tier Limits
- ✅ Unlimited deployments
- ✅ Unlimited bandwidth
- ✅ 100GB monthly data transfer
- ⚠️ Function timeout: 10 seconds for Hobby plan
- 📈 Pro plan ($20/month) for production with:
  - 60 second timeout
  - Advanced monitoring
  - Priority support

## Troubleshooting

### Issue: "MongoDB connection failed"
**Solution:** 
1. Verify connection string in Vercel environment variables
2. Check MongoDB Atlas IP whitelist (should be 0.0.0.0/0)
3. Verify database user exists with correct password
4. Check Vercel function logs: Dashboard → Deployments → Function Logs

### Issue: "ModuleNotFoundError"
**Solution:**
1. Verify all packages in requirements.txt are compatible with Python 3.11
2. Check that api/index.py exists and is in correct directory
3. Redeploy: Go to Deployments → Redeploy

### Issue: "Static files not loading"
**Solution:**
1. Verify `static/` directory exists in root
2. Check CSS/JS files are in correct subdirectories
3. Vercel should auto-serve static files; clear cache and refresh

### Issue: "Knowledge base not showing data"
**Solution:**
1. Upload CSV file via web interface
2. Check MongoDB Atlas to verify data was inserted:
   - Go to Clusters → Collections
   - Select `incident_analyzer` database
   - Check `knowledge_base` collection
3. If empty, manually load sample data via API

## Production Deployment Best Practices

### Security
- [ ] Use strong MongoDB password (auto-generated is good)
- [ ] IP whitelist only your offices/servers (don't use 0.0.0.0/0)
- [ ] Enable MongoDB Network Encryption (always-on for free tier)
- [ ] Use HTTPS only (Vercel provides free SSL)

### Monitoring
- [ ] Set up Vercel Analytics: Dashboard → Analytics
- [ ] Enable MongoDB monitoring: Atlas → Monitoring
- [ ] Configure alerts for errors and high resource usage

### Scaling
- [ ] If hitting connection limits, upgrade MongoDB to M2
- [ ] If timeout issues, break large operations into smaller tasks
- [ ] Use Vercel Pro for better serverless function timeout (60s vs 10s)

### Backup
- [ ] Enable MongoDB automatic backups (M2+ only)
- [ ] Regularly export data: Atlas → Data Tools → Export

## Deployment Checklist

- [ ] Created MongoDB Atlas account and cluster
- [ ] Created database user with strong password
- [ ] Whitelisted IP in MongoDB
- [ ] Got MongoDB connection string
- [ ] Created Vercel account
- [ ] Connected GitHub repository to Vercel
- [ ] Added MONGODB_URI environment variable
- [ ] Deployed successfully
- [ ] Tested main interface (/​)
- [ ] Tested knowledge base management (/manage)
- [ ] Uploaded test CSV file
- [ ] Verified data in MongoDB Atlas
- [ ] Tested SOP generation

## Next Steps

1. **Share with Team:**
   ```
   Your app is live at: https://your-project-name.vercel.app
   ```

2. **Custom Domain (Optional):**
   - In Vercel Dashboard → Settings → Domains
   - Add your custom domain
   - Update DNS records as shown

3. **Continuous Deployment:**
   - Push changes to GitHub `main` branch
   - Vercel automatically redeploys
   - No manual deployment steps needed

4. **Monitor Performance:**
   - Check Vercel Analytics dashboard
   - Review MongoDB resource usage
   - Optimize if needed

## Support & Resources

- **Vercel Docs:** https://vercel.com/docs/concepts/functions/serverless-functions
- **MongoDB Docs:** https://docs.mongodb.com/manual/
- **Flask Docs:** https://flask.palletsprojects.com/
- **GitHub Repo:** https://github.com/RameshSP-gif/IncidentAnalyzer_SOPGenerator

## Estimated Costs

| Service | Tier | Cost |
|---------|------|------|
| **Vercel** | Hobby (Free) | $0 |
| **MongoDB** | M0 (Free) | $0 |
| **Total (Startup)** | - | **$0** |
| **Total (Production-Ready)** | Vercel Pro + MongoDB M2 | ~$29/month |

---

**Last Updated:** January 2026  
**Deployment Status:** Ready for Vercel  
**Python Version:** 3.11+
