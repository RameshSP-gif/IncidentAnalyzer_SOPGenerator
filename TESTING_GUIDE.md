# 🚀 SOP Generator - Testing Instructions

## ✅ Server Status
✔️ Flask application is running at: **http://127.0.0.1:5000**

---

## 📝 How to Test (Step-by-Step)

### **Option 1: Use QUICK_TEST.html (Easiest)**
I've created a helper file that shows all sample data in a formatted view.

1. Open file: `QUICK_TEST.html` (should auto-open in your browser)
2. Click on any field to **copy it to clipboard**
3. Switch to http://127.0.0.1:5000
4. Paste each field into the corresponding form field
5. Click "Generate SOP"

---

### **Option 2: Manual Entry (Copy-Paste from Here)**

**Go to http://127.0.0.1:5000 and enter these values:**

#### 🎯 Test Case 1: Email Issue

```
Incident Number: INC0001

Category: Select "Email" from dropdown

Priority: 3 - Medium (default)

Short Description:
User unable to access email account

Detailed Description:
User reports that they cannot log into their email account. Error message "Invalid credentials" appears when attempting to sign in. User has tried resetting password but still cannot access. This issue started this morning after system maintenance.

Resolution Notes:
Verified user account was locked due to multiple failed login attempts. Unlocked the account in Active Directory. Reset password following company policy. Tested login - successful. Advised user to clear browser cache and cookies. Confirmed user can now access email normally. Issue resolved.
```

**Then click the blue "Generate SOP" button**

---

## 🔍 What to Expect

### ✅ Success Indicators:
1. **Loading spinner** appears for 1-2 seconds
2. **Green toast notification** (bottom right): "SOP generated successfully!"
3. **New section appears below** with "Generated SOP" header
4. **Professional SOP document** with:
   - SOP Information table
   - Overview section
   - Problem Statement
   - Symptoms list
   - Resolution Steps
   - Verification checklist
   - Related Incidents
   - Priority Distribution

### ❌ If You See Errors:

**Check Terminal Output:**
Look at the PowerShell terminal where `py web_app.py` is running. You should see:
```
[DEBUG] Received data: {...}
[DEBUG] Created incident: INC0001
[DEBUG] Validation result: {'is_valid': True, ...}
[DEBUG] Generating SOP...
[DEBUG] SOP generated, length: 1234
```

**Common Issues:**

| Issue | Solution |
|-------|----------|
| "Error: [object Object]" | Check browser console (F12) for JavaScript errors |
| Field validation error | Ensure descriptions are 20+ chars, resolution 30+ chars |
| Nothing happens | Check if Flask server is still running in terminal |
| Blank page | Hard refresh (Ctrl+F5) or clear browser cache |

---

## 🎨 Visual Walkthrough

### Step 1: Open Application
![Header should show blue gradient with title "Incident Analyzer & SOP Generator"]

### Step 2: Fill Form
![Form with labeled fields and dropdown menus]

### Step 3: Submit
![Blue "Generate SOP" button with lightning icon]

### Step 4: View Result
![Professional markdown-formatted SOP with sections]

---

## 🧪 Additional Test Cases

### Test Case 2: Network Issue
```
Incident Number: INC0002
Category: Network
Priority: 2 - High
Short Description: Intermittent network connectivity drops
Detailed Description: User experiencing frequent disconnections from corporate network. Connection drops every 15-20 minutes requiring manual reconnection. Affecting productivity and ongoing video conferences.
Resolution Notes: Diagnosed network adapter driver issue. Updated network adapter driver to latest version. Disabled power management settings. Monitored connection for 2 hours - stable. User confirmed issue resolved.
```

### Test Case 3: Hardware Issue
```
Incident Number: INC0003
Category: Hardware
Priority: 3 - Medium
Short Description: Printer not responding to print jobs
Detailed Description: Office printer not printing documents. All print jobs stuck in queue. Printer shows online status but nothing prints. Multiple users affected.
Resolution Notes: Restarted printer and print spooler service. Cleared print queue. Reinstalled printer driver. Sent test page - successful. All queued jobs printed successfully.
```

---

## 🔧 Troubleshooting Commands

**Check if Flask is running:**
```powershell
Get-Process python
```

**Restart Flask server:**
```powershell
# Stop: Press Ctrl+C in the terminal running Flask
# Start: py web_app.py
```

**View real-time logs:**
Look at the PowerShell terminal where Flask is running - it shows all requests and debug information.

---

## 📊 Features to Test

- [x] Form validation (try submitting with empty fields)
- [x] Single incident SOP generation
- [x] Tab switching (Single Incident ↔ Batch Analysis)
- [x] Clear Form button
- [x] Copy SOP button (after generation)
- [x] Toast notifications
- [x] Loading overlay
- [x] Responsive design (try resizing window)

---

## 🎯 Quick Debug Steps

1. **Open Browser DevTools** (F12)
2. Go to **Console tab**
3. Click "Generate SOP"
4. Look for:
   - Red errors (JavaScript issues)
   - Network requests to `/analyze_single`
   - Response data

If you see any errors, share them and I'll fix immediately!

---

## 💡 Pro Tips

- **Click on field values** in QUICK_TEST.html to copy them instantly
- Use **Ctrl+F5** to hard refresh if CSS doesn't load
- Keep the **terminal visible** to see backend logs
- The **first SOP generation** might take 2-3 seconds (normal)
- Subsequent generations are faster

---

## ✅ Success Criteria

You should be able to:
1. ✅ Fill out the form completely
2. ✅ Click "Generate SOP" without errors
3. ✅ See a loading spinner briefly
4. ✅ Get a success toast notification
5. ✅ View a professionally formatted SOP below the form
6. ✅ Copy the SOP content

If ALL checkboxes pass - the application is working perfectly! 🎉

---

## 📞 Need Help?

If something isn't working:
1. Check the **terminal output** for error messages
2. Open **browser console** (F12) and check for JavaScript errors
3. Share the error message and I'll fix it immediately

The application is designed to be simple and intuitive. If you encounter any issues, they're likely quick to resolve!
