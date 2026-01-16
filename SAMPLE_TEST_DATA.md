# 🧪 Sample Test Data for SOP Generator Web Application

Access the application at: **http://127.0.0.1:5000**

## 📊 Current Database Status

- **Total Incidents in MongoDB:** 9,633
- **Resolution Notes Coverage:** 100%
- **Ready for Testing:** ✅ All systems operational

---

## 📋 Test Case 1: Single Incident Analysis (Invoice Issue)

**Use the "Single Incident" tab and enter:**

| Field | Value |
|-------|-------|
| **Incident Number** | TEST001 |
| **Category** | Financial |
| **Priority** | 4 - Medium |
| **Short Description** | Invoice amount incorrect - transport charges error |
| **Detailed Description** | In invoice 405025, the transport was charged in error. The customer was charged 99 EUR for transport but should only be 49 EUR according to the order. Customer is requesting immediate correction and credit note. |
| **Resolution Notes** | Issue - Invoice 405025 transport charged in error. Resolution - Resolved by RIMS and they confirmed that Credit note and debit note will be created by tomorrow. Correct invoice will be generated once night batch runs. User confirmed resolution and ticket closed. |

**Expected Result:** Generates SOP for invoice correction issues (will find 50+ similar incidents in MongoDB).

---

## 📋 Test Case 2: Single Incident Analysis (Order Issue)

| Field | Value |
|-------|-------|
| **Incident Number** | TEST002 |
| **Category** | Order Management |
| **Priority** | 4 - Medium |
| **Short Description** | iSell order stuck in read-only status cannot cancel |
| **Detailed Description** | Order 1566227215 has been paid in full and is now in read-only status. Customer wants to cancel the order but system does not allow any changes. Order shows as "Loaded on delivery truck" but delivery was never completed. Customer requesting immediate cancellation and refund. |
| **Resolution Notes** | Issue - Order 1566227215 in read-only status preventing cancellation. Resolution - Unlocked order from read-only mode in iSell system. Performed manual cancellation as per procedure. Initiated refund process through payment gateway. Confirmed with customer that refund will be processed within 3-5 business days. Ticket resolved. |

---

## 🔄 Test Case 3: Batch Analysis (Multiple Invoice Issues)

**Use the "Batch Analysis" tab and add these 3 incidents:**

### Incident 1:
- **Short Description:** Invoice 442794 incorrect service amount charged
- **Category:** Financial
- **Detailed Description:** The invoice amount is incorrect as the service amount shown is 69.90 but the system has deducted the 10% discount twice. Customer requesting corrected invoice with proper discount calculation.
- **Resolution Notes:** Issue - Invoice 442794 double discount applied in error. Resolution - As per RIMS team update, Credit note has been created. Kindly release it from RIMS UI application. Correct invoice will be created once night batch runs. User confirmed and ticket resolved.

### Incident 2:
- **Short Description:** Invoice missing customer reference and delivery address
- **Category:** Financial
- **Detailed Description:** OnDemand invoice is missing customer reference number and the delivery address information. Customer cannot process payment without complete invoice details.
- **Resolution Notes:** Issue - Invoice missing customer reference and delivery address. Resolution - Updated invoice template with missing customer reference from order system. Added complete delivery address from shipping records. Regenerated invoice and sent to customer. User confirmed receipt of corrected invoice.

### Incident 3:
- **Short Description:** Invoice 443699 incorrect transport discount amount
- **Category:** Financial
- **Detailed Description:** Invoice 443699 is incorrect because the service amount is not right. It should show 598.83 but shows different amount. Transport discount for delivery was not applied correctly.
- **Resolution Notes:** Issue - Invoice 443699 transport discount not applied. Resolution - RIMS team created credit note but stuck due to control number error. Corrected control number 940325 from RIMS UI screen. Correct invoice generated after night batch runs. User confirmed resolution.

**After adding all 3, click "Generate SOPs"**

**Expected Result:** ML categorizes these into one Invoice cluster (will find 39+ similar incidents in MongoDB) and generates comprehensive invoice correction SOP.

---

## 🔄 Test Case 4: Batch Analysis (Mixed Order Categories)

**Add these 4 incidents for multi-category clustering:**

### Incident 1:
- **Short Description:** iSell order 1565168142 read-only cannot modify
- **Category:** Order Management
- **Detailed Description:** The order has been paid for in full and no changes can be made. System shows read-only status. Customer needs to add additional items to the order before delivery.
- **Resolution Notes:** Issue - Order 1565168142 in read-only mode after payment. Resolution - Contacted second-level support to unlock order temporarily. Added additional items as per customer request. Recalculated total amount and processed additional payment. Locked order again for fulfillment. Customer confirmed satisfaction.

### Incident 2:
- **Short Description:** Manual action for broken orders partial cancellation
- **Category:** Order Management
- **Detailed Description:** RITM1002025855 requires manual action for broken orders. Partial cancellation needed but automated process failing. Order structure appears corrupted in system.
- **Resolution Notes:** Issue - Broken order structure preventing automated cancellation. Resolution - Manual actions performed but failed due to order structure corruption. Order parked in Failure List for handling through Force Closure activity. Escalated to development team for database correction.

### Incident 3:
- **Short Description:** Order 483444667 needs marked delivered by another carrier
- **Category:** Order Management
- **Detailed Description:** iSell order 483444667 needs to be marked as delivered by another carrier. Customer used alternative delivery method (Dolly) on 11/4/25 but system still shows as pending delivery.
- **Resolution Notes:** Issue - Order 483444667 delivery status incorrect. Resolution - Second-level support team updated delivery status to "Delivered by another carrier". Added carrier information (Dolly) and delivery date in system. Order completed successfully. Customer confirmed receipt.

### Incident 4:
- **Short Description:** Order 486344005 mark picked up by customer
- **Category:** Order Management
- **Detailed Description:** iSell order 486344005 needs to be marked as picked up by customer. Customer collected order from store but system still shows waiting for delivery. Store confirmed pickup completed.
- **Resolution Notes:** Issue - Order 486344005 pickup status not updated. Resolution - Changed delivery status to "Picked up by customer" in system. Verified store confirmation and pickup timestamp. Updated order completion date. Customer notified of status update. Ticket resolved.

**Expected Result:** ML creates 1-2 clusters from these similar order management issues and generates SOPs with common resolution patterns found in MongoDB.

---

## ✅ Quick Test Checklist

- [ ] Single Incident: Enter invoice issue → Click "Generate SOP" → View formatted SOP with real resolution steps
- [ ] Single Incident: Clear form → Test with order issue → Verify different SOP generated
- [ ] Batch: Add 3 similar invoice incidents → Stats show 3 incidents → Click "Generate SOPs"
- [ ] Batch: View generated SOP with ML cluster analysis (should find 39+ similar in MongoDB)
- [ ] Batch: Click "Clear All" → Confirm stats reset to 0
- [ ] Batch: Add 4 order management incidents → Verify clustering with real data
- [ ] Test form validation: Try submitting with descriptions < 20 characters
- [ ] Test copy SOP button (single incident mode)
- [ ] Switch between tabs to verify navigation works
- [ ] Verify resolution steps in generated SOPs match MongoDB patterns
- [ ] Check that average resolution time is calculated from actual incident data

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
**SOP Information** (ID, category, incident count, timestamp, average resolution time)
- **Overview** section explaining the procedure
- **Problem Statement** (extracted from actual incidents in MongoDB)
- **Symptoms** (common issues from real user reports)
- **Prerequisites** (system access requirements)
- **Resolution Steps** (detailed steps from 9,633 real incident resolutions)
- **Verification** checklist for confirming resolution
- **Related Incidents** list with actual incident numbers
- **Priority Distribution** from historical data
- **Average Resolution Time** calculated from MongoDB incidentsents list
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

## 📊 Expected BehavSOP generation using ML to find similar incidents from 9,633 in MongoDB
2. **Batch Mode (2-3 similar incidents):** Single SOP with combined analysis + MongoDB patterns
3. **Batch Mode (4+ incidents):** ML clustering groups into categories, generates multiple SOPs
4. **ML Categorization:** DBSCAN algorithm automatically clusters based on description similarity
5. **Resolution Extraction:** Real resolution steps from 100% of MongoDB incidents
6. **Metrics:** Average resolution time, priority distribution from actual historical data

---

## 🗄️ MongoDB Integration

**The system has 9,633 real incidents with:**
- ✅ Short descriptions (incident summaries)
- ✅ Detailed descriptions (full problem details)
- ✅ Resolution notes (100% coverage - every incident has resolution steps)
- ✅ Priority levels (1-5 scale)
- ✅ State information (Closed, Resolved, etc.)
- ✅ Assignment groups (support teams)
- ✅ Contact type (Portal, Email, Phone)
- ✅ Service offering (iSell EU, RIMS, etc.)
- ✅ Timestamps (created, updated, resolved)

**When you test, your incidents will be:**
1. Combined with similar incidents from MongoDB
2. Clustered using ML (sentence embeddings + DBSCAN)
3. Analyzed for common patterns
4. Used to generate SOPs with real resolution procedures

**Example Test Results:**
- 100 incidents → 92 valid → 3 clusters → 3 SOPs (Test completed successfully)
- 500 incidents → 476 valid → 12 clusters → 12 SOPs (Average 75-168 hours resolution time)

---

## 🧪 Alternative Testing Methods

### Command Line Testing:
```powershell
# Test with 100 incidents from MongoDB
python test_pipeline.py --limit 100

# Test with custom incident data
python test_custom_incident.py

# View working data samples
python show_working_data.py

# Run demonstration
python demo_resolution_sop.py
```

### Direct MongoDB Query:
```python
from src.database.mongodb import MongoDBClient
client = MongoDBClient()
incidents = client.get_all_incidents(limit=10)
print(f"Sample incidents: {len(incidents)}")
```

Enjoy testing with real production dataorization:** Automatically groups similar issues regardless of manual category selection

Enjoy testing! 🚀
