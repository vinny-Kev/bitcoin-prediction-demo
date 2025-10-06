# 🚀 DEPLOY STREAMLIT APP - MANUAL STEPS

Since GitHub CLI needs authentication, follow these manual steps:

---

## 📦 STEP 1: Create GitHub Repository

1. **Go to**: https://github.com/new

2. **Fill in details**:
   - Repository name: `bitcoin-prediction-demo`
   - Description: `Bitcoin AI Price Prediction Demo with 3 Free Predictions`
   - Visibility: **Public** ✅
   - Initialize: **NO** (we already have files)

3. **Click**: "Create repository"

---

## 📤 STEP 2: Push Code to GitHub

Copy and run these commands in PowerShell:

```powershell
cd "d:\CODE ALL HERE PLEASE\bitcoin-streamlit-demo"

# Add GitHub remote (replace YOUR_USERNAME with vinny-Kev or your actual username)
git remote add origin https://github.com/vinny-Kev/bitcoin-prediction-demo.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Enter your GitHub credentials when prompted**

---

## 🎨 STEP 3: Deploy to Streamlit Cloud

1. **Go to**: https://share.streamlit.io

2. **Sign in** with GitHub

3. **Click**: "New app" (top right)

4. **Select repository**: `vinny-Kev/bitcoin-prediction-demo`

5. **Configure**:
   ```
   Repository:     vinny-Kev/bitcoin-prediction-demo
   Branch:         main
   Main file path: app.py
   App URL:        bitcoin-ai-predictor (or choose your own)
   ```

6. **Advanced Settings** (optional):
   - Python version: 3.11
   - No secrets needed

7. **Click**: "Deploy!"

8. **Wait**: 2-3 minutes

9. **Your app URL**:
   ```
   https://vinny-kev-bitcoin-prediction-demo.streamlit.app
   ```
   or
   ```
   https://bitcoin-ai-predictor.streamlit.app
   ```

---

## ✅ VERIFICATION

Once deployed:

1. **Visit your URL**
2. **Check**:
   - [ ] Page loads
   - [ ] Shows "3 / 3 Predictions Remaining"
   - [ ] Sidebar has model info
   
3. **Wait for API** to finish on Render (might show "API offline" temporarily)

4. **Once API is ready**, test:
   - [ ] Click "Predict Now"
   - [ ] Prediction appears
   - [ ] Counter: 2 / 3
   - [ ] Make 2 more predictions
   - [ ] After 3rd: Contact info shows

---

## 🎉 YOU'RE LIVE!

Share your demo:
- LinkedIn
- Twitter
- Reddit (r/algotrading, r/Bitcoin)
- Friends & colleagues

**Your demo URL**: 
```
https://your-app-name.streamlit.app
```

---

## 📊 WHAT'S NEXT?

While the API finishes deploying on Render:

1. **Monitor Render logs**: https://dashboard.render.com
2. **Test API when ready**: https://btc-forecast-api.onrender.com/
3. **Test Streamlit app**: Your Streamlit URL
4. **Share and gather feedback**! 🚀

---

**Need help?** Check the logs or let me know what you see!
