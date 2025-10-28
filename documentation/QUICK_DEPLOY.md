# Quick Deploy to Vercel

## 🚀 Fastest Deployment Method

### Step 1: Install Vercel CLI
```bash
npm i -g vercel
```

### Step 2: Login
```bash
vercel login
```

### Step 3: Deploy
```bash
vercel
```

Follow the prompts:
- Set up and deploy? **Yes**
- Which scope? (Your account)
- Link to existing project? **No**
- Project name? **safe-drive** (or your choice)
- In which directory is your code located? **./** (current directory)

### Step 4: Add Environment Variable
```bash
vercel env add REACT_APP_API_URL
```
Enter your backend URL when prompted (e.g., `https://your-backend.railway.app/api`)

### Step 5: Deploy to Production
```bash
vercel --prod
```

Done! Your app is now live at `https://your-project.vercel.app`

---

## 🐛 Troubleshooting

**Build fails?**
```bash
# Clear cache and rebuild
vercel --prod --force
```

**Need to update backend URL?**
```bash
vercel env rm REACT_APP_API_URL
vercel env add REACT_APP_API_URL
```

**Check deployment logs:**
Visit your Vercel dashboard → Deployments → Latest → Logs

---

## 📝 Important Notes

1. **Backend Required**: This app needs a separate backend. Deploy it to Railway or Render first.
2. **Camera Won't Work**: Web cameras require local backend. This is a limitation of web apps.
3. **Environment Variables**: Must be set in Vercel dashboard or via CLI.

---

## 🔄 Update Frontend

After making changes:
```bash
git add .
git commit -m "Update frontend"
git push
# Vercel will auto-deploy
```

Or manually:
```bash
vercel --prod
```

