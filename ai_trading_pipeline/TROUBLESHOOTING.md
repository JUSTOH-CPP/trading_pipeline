# 🔧 Troubleshooting Guide

## Issue: "This site can't be reached - ERR_ADDRESS_INVALID"

### ❌ WRONG URLs (Don't use these)
```
http://0.0.0.0:8000/          ← ❌ Invalid - browser can't access 0.0.0.0
http://0.0.0.0:8000/          ← ❌ Error: ERR_ADDRESS_INVALID
```

### ✅ CORRECT URLs (Use these)
```
http://localhost:8000/        ← ✅ Recommended - most reliable
http://127.0.0.1:8000/        ← ✅ Alternative - also works
```

---

## Why This Happens

The bot server binds to `0.0.0.0:8000` which means:
- **Server perspective:** "Listen on all network interfaces"
- **Browser perspective:** `0.0.0.0` is not a valid address to navigate to

You must use `localhost` or `127.0.0.1` when accessing from your browser.

---

## Quick Fix - Try These Steps

### Step 1: Make sure bot is running
```powershell
cd C:\Users\User\source\repos\ai_trading_pipeline\ai_trading_pipeline
python ai_trading_pipeline.py
```

Expected output:
```
🌐 DASHBOARD READY! Open your browser to:
   → http://localhost:8000
   → or http://127.0.0.1:8000
```

### Step 2: Copy the URL from console
- Look at the output above
- Copy: `http://localhost:8000` 

### Step 3: Paste in browser
- Open a new browser tab
- Paste the URL: `http://localhost:8000`
- Press Enter

### Step 4: Dashboard appears! 🎉

---

## If Still Not Working

### Check 1: Is the bot running?
Look for console output showing:
```
🌐 DASHBOARD READY! Open your browser to:
   → http://localhost:8000
```

**If not showing:** Run the bot again (Step 1 above)

### Check 2: Is port 8000 available?
```powershell
netstat -ano | findstr :8000
```

If it shows a process on port 8000, either:
- Close that process, OR
- Use a different port (see advanced below)

### Check 3: Check firewall
Windows Defender might block port 8000:
- Open Windows Defender Firewall
- Click "Allow an app through firewall"
- Make sure Python is allowed

### Check 4: Try alternative URL
If `http://localhost:8000` doesn't work, try:
```
http://127.0.0.1:8000
```

### Check 5: Clear browser cache
```
Ctrl + Shift + Delete    (in browser)
```
Then refresh or try again

---

## Advanced: Change Port

If port 8000 is already in use, edit `ai_trading_pipeline.py`:

**Find this line:**
```python
kwargs={"host": "0.0.0.0", "port": 8000},
```

**Change to:**
```python
kwargs={"host": "0.0.0.0", "port": 9000},  # Changed 8000 to 9000
```

**Then use URL:**
```
http://localhost:9000
```

---

## Checklist

- [ ] Bot is running (`python ai_trading_pipeline.py`)
- [ ] Console shows "DASHBOARD READY!"
- [ ] Using `http://localhost:8000` (not `http://0.0.0.0:8000`)
- [ ] No firewall blocking port 8000
- [ ] Port 8000 is not in use by another app
- [ ] Browser is opening a new tab, not the address bar

---

## Quick Reference Card

| Need | Command |
|------|---------|
| **Start Bot** | `python ai_trading_pipeline.py` |
| **Open Dashboard** | `http://localhost:8000` |
| **Stop Bot** | `Ctrl + C` (in console) |
| **Check Port** | `netstat -ano \| findstr :8000` |
| **Clear Cache** | `Ctrl + Shift + Delete` (in browser) |
| **Restart Fresh** | Close bot, close browser tab, start bot, open new tab |

---

## Success Signals

When working correctly, you'll see:

**In Console:**
```
🌐 DASHBOARD READY! Open your browser to:
   → http://localhost:8000
Bot successfully synchronized on account XXXXXXXXX
Listening for market clock triggers...
[HH:MM:SS] Checked Bar...
```

**In Browser:**
- Dark themed dashboard loads
- Chart area on left
- Sidebar with account info on right
- Green candlesticks appear
- Connection indicator shows green

---

## Still Having Issues?

1. **Make sure you're using the exact URL from the console output**
2. **Check that port 8000 is not blocked by firewall**
3. **Try clearing browser cache and cookies**
4. **Try a different browser** (Chrome, Firefox, Edge)
5. **Restart your computer** (last resort)

---

**Remember:** Always use `localhost` or `127.0.0.1`, never `0.0.0.0` in your browser!
