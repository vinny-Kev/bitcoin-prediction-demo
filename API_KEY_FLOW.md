# 🎯 API Key Flow - How It Actually Works

## 📱 User Experience Flow

### Stage 1: Guest Access (Predictions 1-3)
```
┌─────────────────────────────────────┐
│  User visits app (no API key)      │
│  👤 Guest Mode: 0/3 free used      │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  User clicks "Generate Prediction"  │
│  ✅ Works! Shows prediction         │
│  👤 Guest Mode: 1/3 free used      │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  User makes 2nd prediction          │
│  ✅ Works! Shows prediction         │
│  👤 Guest Mode: 2/3 free used      │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  User makes 3rd prediction          │
│  ✅ Works! Shows prediction         │
│  👤 Guest Mode: 3/3 free used      │
└─────────────────────────────────────┘
```

### Stage 2: Trial Expired (After 3 predictions)
```
┌─────────────────────────────────────┐
│  User tries 4th prediction          │
│  🚫 BLOCKED                         │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Error message shows:               │
│  ────────────────────────────────   │
│  🚫 Free trial limit reached (3)    │
│                                     │
│  Contact Kevin Maglaqui at          │
│  kevinroymaglaqui29@gmail.com       │
│  for an API key to continue         │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Sidebar shows:                     │
│  ────────────────────────────────   │
│  🚫 Trial Expired                   │
│                                     │
│  📧 Email kevinroymaglaqui29@...    │
│  with:                              │
│  • Your name                        │
│  • Your email                       │
│  • Use case (optional)              │
│                                     │
│  [🔐 Enter API Key (Required)] ←    │
│      [Password Input: ______]       │
│      [✅ Activate] [📧 Request Key] │
└─────────────────────────────────────┘
```

### Stage 3: User Contacts Owner
```
┌─────────────────────────────────────┐
│  User emails owner:                   │
│  ────────────────────────────────   │
│  To: kevinroymaglaqui29@gmail.com   │
│  Subject: API Key Request           │
│                                     │
│  Hi Kevin,                          │
│  Name: John Doe                     │
│  Email: john@example.com            │
│  Would like to continue using       │
│  the Bitcoin AI app!                │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  YOU (Kevin) generate key:          │
│  ────────────────────────────────   │
│  $ curl -X POST \                   │
│    "https://btc-forecast-api...\    │
│    /api-keys/generate" \            │
│    -H "X-Admin-Secret: YOUR_SEC" \  │
│    -H "Content-Type: app/json" \    │
│    -d '{                            │
│      "name": "John Doe",            │
│      "email": "john@example.com"    │
│    }'                               │
│                                     │
│  Response:                          │
│  {                                  │
│    "api_key": "btc_abc123xyz...",   │
│    "rate_limit": "3 per minute"     │
│  }                                  │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  YOU email back to user:            │
│  ────────────────────────────────   │
│  Hi John,                           │
│                                     │
│  Here's your API key:               │
│  btc_abc123xyz...                   │
│                                     │
│  Paste this in the sidebar to       │
│  unlock 3 predictions per minute!   │
│                                     │
│  Thanks!                            │
│  Kevin                              │
└─────────────────────────────────────┘
```

### Stage 4: User Enters Key
```
┌─────────────────────────────────────┐
│  User pastes key in sidebar:        │
│  ────────────────────────────────   │
│  [Password Input: btc_abc123xyz...] │
│  [✅ Activate] ← User clicks this   │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Frontend calls:                    │
│  GET /api-keys/usage                │
│  Authorization: Bearer btc_abc123   │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Backend validates:                 │
│  ✅ Key exists in database          │
│  ✅ Returns user info               │
│                                     │
│  {                                  │
│    "user_type": "authenticated",    │
│    "name": "John Doe",              │
│    "rate_limit": "3 per minute",    │
│    "calls_remaining": 3             │
│  }                                  │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Sidebar now shows:                 │
│  ────────────────────────────────   │
│  ✅ API Key Active                  │
│  👤 John Doe                        │
│  Limit: 3 predictions per minute    │
│  Calls Available: 3 calls/min       │
│                                     │
│  [🔄 Change API Key]                │
└─────────────────────────────────────┘
```

### Stage 5: Authenticated Predictions
```
┌─────────────────────────────────────┐
│  User clicks "Generate Prediction"  │
│  ✅ Works! (1st in this minute)     │
│  Calls Available: 2 calls/min       │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  User clicks again                  │
│  ✅ Works! (2nd in this minute)     │
│  Calls Available: 1 calls/min       │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  User clicks again                  │
│  ✅ Works! (3rd in this minute)     │
│  Calls Available: 0 calls/min       │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  User clicks again (4th time)       │
│  🚫 RATE LIMITED                    │
│                                     │
│  ⏱️ Rate limit exceeded.            │
│  You can make 3 predictions per     │
│  minute. Try again in 45 seconds.   │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  User waits 60 seconds...           │
│  ✅ Counter resets                  │
│  Calls Available: 3 calls/min       │
│  User can make predictions again!   │
└─────────────────────────────────────┘
```

---

## 🔑 Two Types of Users

### 👤 Guest Users
- **Limit**: 3 predictions TOTAL (lifetime, not per minute)
- **Tracking**: By IP address
- **After limit**: Must get API key to continue
- **No payment required**: Free trial

### 🔐 Authenticated Users (with API key)
- **Limit**: 3 predictions PER MINUTE
- **Tracking**: By API key (Bearer token)
- **After limit**: Wait 60 seconds, counter resets
- **Requires**: Email you to get key (manual approval)

---

## 🛠️ Admin Process (What YOU Do)

### When Someone Emails You:

1. **Receive email** from user requesting key

2. **Decide** if you want to give them access

3. **Generate key** via curl:
```bash
curl -X POST "https://btc-forecast-api.onrender.com/api-keys/generate" \
  -H "X-Admin-Secret: YOUR_SECRET_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com"
  }'
```

4. **Get response**:
```json
{
  "success": true,
  "api_key": "btc_WvR9xKj3mP8nL2qH5sT1yU6vZ4",
  "name": "John Doe",
  "email": "john@example.com",
  "rate_limit": "3 predictions per minute",
  "usage": "Include header: Authorization: Bearer btc_WvR9xKj3mP8nL2qH5sT1yU6vZ4"
}
```

5. **Email the key** to the user

6. **They paste it** in the app

7. **Done!** They now have 3 predictions per minute

---

## 💡 Key Points

✅ **NO self-service** - Users must email you  
✅ **NO payment integration** - You manually decide who gets keys  
✅ **Manual process** - You run curl command for each user  
✅ **Rate limited** - 3 per minute for authenticated, 3 total for guests  
✅ **Persistent** - Keys stored in `api_keys.json` file on your server  

---

## 🚀 Future Enhancements (Optional)

If you want to automate this later, you could add:

1. **Stripe integration** - Auto-generate keys after payment
2. **Admin dashboard** - Web UI to manage keys instead of curl
3. **Subscription tiers** - Different limits for different plans
4. **Usage analytics** - Track who uses how much
5. **Key expiration** - Auto-expire keys after X days

But for now, **manual approval via email is perfectly fine!**

---

**Current Status**: ✅ Working as designed  
**Manual process**: Email → You generate → You send key → User enters → Activated  
**No self-service**: By design (you control who gets access)
