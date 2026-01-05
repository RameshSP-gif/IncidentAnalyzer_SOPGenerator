# 🧪 Sample Test Data for SOP Generator Web Application

Access the application at: **http://127.0.0.1:5000**

---

## 📋 Test Case 1: Single Incident Analysis (Email Issue)

**Use the "Single Incident" tab and enter:**

| Field | Value |
|-------|-------|
| **Incident Number** | INC0001 |
| **Category** | Email |
| **Priority** | 3 - Medium |
| **Short Description** | User unable to access email account |
| **Detailed Description** | User reports that they cannot log into their email account. Error message "Invalid credentials" appears when attempting to sign in. User has tried resetting password but still cannot access. This issue started this morning after system maintenance. |
| **Resolution Notes** | Verified user account was locked due to multiple failed login attempts. Unlocked the account in Active Directory. Reset password following company policy. Tested login - successful. Advised user to clear browser cache and cookies. Confirmed user can now access email normally. Issue resolved. |

**Expected Result:** Generates a professional SOP document for email access issues.

---

## 📋 Test Case 2: Single Incident Analysis (Network Issue)

| Field | Value |
|-------|-------|
| **Incident Number** | INC0002 |
| **Category** | Network |
| **Priority** | 2 - High |
| **Short Description** | Intermittent network connectivity drops |
| **Detailed Description** | User experiencing frequent disconnections from corporate network. Connection drops every 15-20 minutes requiring manual reconnection. Affecting productivity and ongoing video conferences. Problem occurs on both wired and wireless connections. |
| **Resolution Notes** | Diagnosed network adapter driver issue. Updated network adapter driver to latest version from manufacturer website. Disabled power management settings that were causing adapter to sleep. Monitored connection for 2 hours - no disconnections observed. Tested with video conference - stable connection maintained. User confirmed issue resolved. |

---

## 🔄 Test Case 3: Batch Analysis (Multiple Email Issues)

**Use the "Batch Analysis" tab and add these 3 incidents:**

### Incident 1:
- **Short Description:** Cannot send emails with attachments
- **Category:** Email
- **Detailed Description:** User reports that emails with attachments larger than 5MB fail to send. Error message "Message too large" appears. Smaller emails without attachments send successfully.
- **Resolution Notes:** Checked mailbox settings and increased attachment size limit from 5MB to 25MB in Exchange admin center. Tested sending 10MB attachment - successful. User confirmed can now send large attachments.

### Incident 2:
- **Short Description:** Emails stuck in outbox
- **Category:** Email
- **Detailed Description:** Multiple emails are stuck in user's outbox and not sending. User tried restarting Outlook multiple times. Emails have been stuck for over 2 hours. No error messages displayed.
- **Resolution Notes:** Identified corrupt message in outbox causing queue blockage. Switched Outlook to work offline mode. Deleted problematic email from outbox. Switched back to online mode. All other emails sent successfully. Advised user to avoid sending very large attachments.

### Incident 3:
- **Short Description:** Email synchronization not working on mobile
- **Category:** Email
- **Detailed Description:** User's mobile device not syncing with corporate email. Last sync was 24 hours ago. Desktop email works fine. User using company iPhone with native Mail app.
- **Resolution Notes:** Removed email account from mobile device. Re-added account using correct Exchange settings. Verified SSL and port settings (443). Performed manual sync - successful. All emails from past 24 hours downloaded. User confirmed continuous sync working.

**After adding all 3, click "Generate SOPs"**

**Expected Result:** ML categorizes these into one Email cluster and generates a comprehensive SOP.

---

## 🔄 Test Case 4: Batch Analysis (Mixed Categories)

**Add these 4 incidents for multi-category clustering:**

### Incident 1:
- **Short Description:** Password reset request
- **Category:** Access
- **Detailed Description:** User forgot domain password and cannot log into workstation. Account not locked. User needs immediate access to complete urgent report deadline today.
- **Resolution Notes:** Verified user identity using security questions. Generated temporary password following security policy. User successfully logged in. Instructed user to change password on next login per company policy. Documented password reset in audit log.

### Incident 2:
- **Short Description:** VPN connection timeout
- **Category:** Network
- **Detailed Description:** Remote user cannot establish VPN connection to corporate network. Connection times out after authentication. User working from home needs access to file servers. Problem started yesterday.
- **Resolution Notes:** Checked VPN server logs - certificate expired. Renewed SSL certificate on VPN gateway. Restarted VPN service. Tested connection from multiple locations - successful. User able to connect and access resources. No further issues reported.

### Incident 3:
- **Short Description:** Cannot access shared folder
- **Category:** Access
- **Detailed Description:** User recently transferred to new department. Cannot access shared department folder that colleagues can access. User gets "Access Denied" message. Permissions issue suspected.
- **Resolution Notes:** Reviewed Active Directory group memberships. Added user to appropriate security group for department share. Removed from old department group. Propagated changes across domain controllers (15 minutes). User successfully accessed shared folder. Verified read and write permissions working correctly.

### Incident 4:
- **Short Description:** Slow network file transfer
- **Category:** Network
- **Detailed Description:** File transfers to network drive extremely slow. 100MB file takes 20+ minutes to copy. Other users report normal speeds. Problem only affecting this user's computer. Internet speed tests show normal results.
- **Resolution Notes:** Discovered network cable had damaged connector causing packet loss. Replaced ethernet cable with new Cat6 cable. Tested file transfer speeds - improved to normal range (100MB in 2 minutes). Ran network diagnostics - no packet loss detected. User confirmed problem resolved.

**Expected Result:** ML creates 2 clusters (Access issues and Network issues) and generates 2 separate SOPs.

---

## ✅ Quick Test Checklist

- [ ] Single Incident: Enter email issue → Click "Generate SOP" → View formatted SOP
- [ ] Single Incident: Clear form → Test with network issue → Verify different SOP
- [ ] Batch: Add 3 similar email incidents → Stats show 3 incidents → Click "Generate SOPs"
- [ ] Batch: View generated SOP with cluster analysis
- [ ] Batch: Click "Clear All" → Confirm stats reset to 0
- [ ] Batch: Add 4 mixed category incidents → Verify 2 SOPs generated
- [ ] Test form validation: Try submitting with descriptions < 20 characters
- [ ] Test copy SOP button (single incident mode)
- [ ] Switch between tabs to verify navigation works

---

## 🎨 What to Look For

### Visual Elements:
✅ Professional gradient header with blue theme
✅ Tab navigation (Single Incident / Batch Analysis)
✅ Form fields with proper labels and hints
✅ Blue primary buttons with hover effects
✅ Stats cards showing incident counts (batch mode)
✅ Toast notifications (bottom right) for success/error messages
✅ Loading overlay with spinner during processing
✅ Formatted SOP output with proper headings and sections

### SOP Output Should Include:
- SOP Information (ID, category, incident count, timestamp)
- Overview section
- Problem Statement (extracted from incidents)
- Symptoms (user-reported issues)
- Prerequisites
- Resolution Steps
- Verification checklist
- Related Incidents list
- Priority Distribution
- Notes section

---

## 🐛 Troubleshooting

**Blank Page?**
- Check browser console (F12) for JavaScript errors
- Verify Flask server is running in terminal
- Try refreshing the page (Ctrl+F5)

**CSS Not Loading?**
- Check that static/css/style.css exists
- Verify Flask serving static files correctly

**Form Validation Errors?**
- Descriptions must be at least 20 characters
- Resolution notes must be at least 30 characters
- Category must be selected

**Batch Generate Button Disabled?**
- Need at least 2 incidents for ML clustering
- Add more incidents to enable the button

---

## 📊 Expected Behavior

1. **Single Mode:** Instant SOP generation for any valid incident
2. **Batch Mode (2-3 similar incidents):** Single SOP with combined analysis
3. **Batch Mode (4+ mixed incidents):** Multiple SOPs grouped by category
4. **ML Categorization:** Automatically groups similar issues regardless of manual category selection

Enjoy testing! 🚀
