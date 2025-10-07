# 🔑 How to Generate API Keys - Step-by-Step Guide

## 🎯 What You're Trying to Do:
Generate an API key for yourself (or a user) so you can paste it into the Streamlit app and make unlimited predictions.

---

## 📝 Step-by-Step Instructions

### Step 1: Get Your Admin Secret

Your backend has this code:
```python
ADMIN_SECRET = os.getenv("ADMIN_SECRET", "change_this_secret_key")
```

**So your admin secret is either:**
- The value you set in Render's environment variables (`ADMIN_SECRET=whatever`)
- OR the default: `change_this_secret_key` (if you haven't set it)

**Check Render Dashboard:**
1. Go to https://dashboard.render.com
2. Click on your API service (`btc-forecast-api`)
3. Go to "Environment" tab
4. Look for `ADMIN_SECRET`
5. If it exists, use that value
6. If it doesn't exist, use `change_this_secret_key`

---

### Step 2: Open PowerShell

You're already in PowerShell! Perfect.

---

### Step 3: Run This Command

**Replace the parts in `< >`:**

```powershell
curl.exe -X POST "https://btc-forecast-api.onrender.com/api-keys/generate" `
  -H "X-Admin-Secret: change_this_secret_key" `
  -H "Content-Type: application/json" `
  -d '{\"name\":\"Kevin Maglaqui\",\"email\":\"kevinroymaglaqui29@gmail.com\"}'
```

**If you set a custom ADMIN_SECRET on Render, replace `change_this_secret_key` with your actual secret.**

---

### Step 4: You'll Get a Response Like This

**Success Response:**
```json
{
  "success": true,
  "api_key": "btc_WvR9xKj3mP8nL2qH5sT1yU6vZ4cX8dE2fG1",
  "name": "Kevin Maglaqui",
  "email": "kevinroymaglaqui29@gmail.com",
  "rate_limit": "3 predictions per minute",
  "usage": "Include header: Authorization: Bearer btc_WvR9xKj3mP8nL2qH5sT1yU6vZ4cX8dE2fG1"
}
```

**Error Response (if admin secret is wrong):**
```json
{
  "detail": "Unauthorized"
}
```

---

### Step 5: Copy Your API Key

From the response, copy the `api_key` value:
```
btc_WvR9xKj3mP8nL2qH5sT1yU6vZ4cX8dE2fG1
```

---

### Step 6: Paste It in Your Streamlit App

1. Open your app: https://bitcoin-prediction-demo.streamlit.app
2. Look at the **sidebar** (left side)
3. Find the section: **🔐 Enter API Key**
4. Paste your key: `btc_WvR9xKj3mP8nL2qH5sT1yU6vZ4cX8dE2fG1`
5. Click **✅ Activate**
6. You should see: **✅ API Key Active**

---

### Step 7: Make Predictions!

Now click **🔮 Generate Prediction** and it should work!

Currently you'll be limited to **3 predictions per minute** because the backend doesn't have admin tier yet (that's the next fix).

---

## 🧪 Quick Test - Run This Now:

**In your PowerShell terminal, run:**

```powershell
curl.exe -X POST "https://btc-forecast-api.onrender.com/api-keys/generate" `
  -H "X-Admin-Secret: change_this_secret_key" `
  -H "Content-Type: application/json" `
  -d '{\"name\":\"Kevin Maglaqui\",\"email\":\"kevinroymaglaqui29@gmail.com\"}'
```

**Expected result:**
```json
{
  "success": true,
  "api_key": "btc_xxxxxxxxxxxxx",
  ...
}
```

**If you get `"detail": "Unauthorized"`:**
- Your ADMIN_SECRET is NOT `change_this_secret_key`
- Check Render environment variables for the actual value
- Or set it to something you know

---

## 🔍 Troubleshooting

### Error: "Unauthorized" (403)
**Problem**: Wrong admin secret

**Solution**: 
1. Go to Render Dashboard
2. Find your ADMIN_SECRET environment variable
3. Use that exact value in the `-H "X-Admin-Secret: YOUR_VALUE"` header

### Error: "Not Found" (404)
**Problem**: Endpoint doesn't exist (wrong URL)

**Solution**: 
- Check that your backend is deployed
- Verify URL is correct: `https://btc-forecast-api.onrender.com/api-keys/generate`

### Error: "JSON decode error"
**Problem**: PowerShell is being weird with the JSON

**Solution**: Try this format instead:
```powershell
$body = @{
    name = "Kevin Maglaqui"
    email = "kevinroymaglaqui29@gmail.com"
} | ConvertTo-Json

curl.exe -X POST "https://btc-forecast-api.onrender.com/api-keys/generate" `
  -H "X-Admin-Secret: change_this_secret_key" `
  -H "Content-Type: application/json" `
  -d $body
```

---

## 📋 Checklist

- [ ] Find your ADMIN_SECRET (check Render or use default)
- [ ] Open PowerShell
- [ ] Run the curl command with correct admin secret
- [ ] Copy the `api_key` from response
- [ ] Paste it into Streamlit app sidebar
- [ ] Click ✅ Activate
- [ ] See "✅ API Key Active" message
- [ ] Test a prediction
- [ ] Success! 🎉

---

## 🎯 Quick Copy-Paste Commands

### Generate Key for Yourself:
```powershell
curl.exe -X POST "https://btc-forecast-api.onrender.com/api-keys/generate" -H "X-Admin-Secret: change_this_secret_key" -H "Content-Type: application/json" -d '{\"name\":\"Kevin Maglaqui\",\"email\":\"kevinroymaglaqui29@gmail.com\"}'
```

### Generate Key for a User:
```powershell
curl.exe -X POST "https://btc-forecast-api.onrender.com/api-keys/generate" -H "X-Admin-Secret: change_this_secret_key" -H "Content-Type: application/json" -d '{\"name\":\"John Doe\",\"email\":\"john@example.com\"}'
```

### Check Existing Keys (if you made any):
Your backend saves them in `api_keys.json` on the server. You can't view them via API right now (would need to add an endpoint for that).

---

## 💡 Pro Tip:

**Save your generated key somewhere safe!** Like a password manager. That way you don't have to generate a new one every time.

---

**You're not a dumbass!** This is genuinely confusing because there are TWO different authentication mechanisms (admin secret vs API keys). It's a common confusion in API design! 😊
