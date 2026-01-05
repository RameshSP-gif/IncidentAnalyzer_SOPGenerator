# How to Add New Categories

## Steps to Add a New Category (e.g., "Database")

### 1. Update Main Form (Single Incident Tab)
**File:** `templates/index.html`

Find the category dropdown (around line 68-76):
```html
<select id="category" name="category" class="form-select" required>
    <option value="">Select Category</option>
    <option value="Email">Email</option>
    <option value="Network">Network</option>
    <option value="Hardware">Hardware</option>
    <option value="Software">Software</option>
    <option value="Database">Database</option>  <!-- ADD THIS -->
    <option value="Access">Access/Security</option>
    <option value="Other">Other</option>
</select>
```

### 2. Update Batch Form
**File:** `templates/index.html`

Find the batch category dropdown (around line 182-190):
```html
<select id="batch_category" name="category" class="form-select" required>
    <option value="">Select Category</option>
    <option value="Email">Email</option>
    <option value="Network">Network</option>
    <option value="Hardware">Hardware</option>
    <option value="Software">Software</option>
    <option value="Database">Database</option>  <!-- ADD THIS -->
    <option value="Access">Access/Security</option>
    <option value="Other">Other</option>
</select>
```

### 3. Update Management Page Filter
**File:** `templates/manage.html`

Find the filter dropdown (around line 311-318):
```html
<select class="filter-select" id="category-filter" onchange="searchIncidents()">
    <option value="">All Categories</option>
    <option value="Email">Email</option>
    <option value="Network">Network</option>
    <option value="Hardware">Hardware</option>
    <option value="Software">Software</option>
    <option value="Database">Database</option>  <!-- ADD THIS -->
    <option value="Access">Access/Security</option>
</select>
```

### 4. Update Management Edit Form
**File:** `templates/manage.html`

Find the edit form dropdown (around line 367-373):
```html
<select id="edit-category" required>
    <option value="Email">Email</option>
    <option value="Network">Network</option>
    <option value="Hardware">Hardware</option>
    <option value="Software">Software</option>
    <option value="Database">Database</option>  <!-- ADD THIS -->
    <option value="Access">Access/Security</option>
</select>
```

### 5. Add CSS Styling for Category Badge
**File:** `templates/manage.html`

Find the category badge styles (around line 100-105) and add:
```css
.category-database { background: #e1f5fe; color: #0277bd; }
```

**Available Color Schemes:**
- Blue: `background: #e3f2fd; color: #1976d2;`
- Green: `background: #e8f5e9; color: #388e3c;`
- Orange: `background: #fff3e0; color: #f57c00;`
- Purple: `background: #f3e5f5; color: #7b1fa2;`
- Cyan: `background: #e1f5fe; color: #0277bd;`
- Pink: `background: #fce4ec; color: #c2185b;`
- Teal: `background: #e0f2f1; color: #00796b;`
- Amber: `background: #fff8e1; color: #f57f17;`

### 6. Restart Flask Server
```powershell
# Stop server (Ctrl+C or)
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Start server
py web_app.py
```

## Example: Adding Multiple Categories

To add "Database", "Security", and "Cloud" categories:

1. Add all three to each dropdown:
```html
<option value="Database">Database</option>
<option value="Security">Security</option>
<option value="Cloud">Cloud</option>
```

2. Add CSS for each:
```css
.category-database { background: #e1f5fe; color: #0277bd; }
.category-security { background: #ffebee; color: #c62828; }
.category-cloud { background: #e0f2f1; color: #00796b; }
```

## Quick Test

After adding new categories:
1. Go to http://127.0.0.1:5000
2. Check dropdown - new category should appear
3. Add test incident with new category
4. Go to http://127.0.0.1:5000/manage
5. Filter by new category - should work
6. Edit incident - new category in dropdown

## Already Added Categories

✅ **Email** - Email account, mailbox, synchronization issues
✅ **Network** - Connectivity, VPN, bandwidth problems  
✅ **Hardware** - Laptops, printers, physical devices
✅ **Software** - Applications, programs, licenses
✅ **Database** - SQL, NoSQL, database connection issues (NEW!)
✅ **Access** - Permissions, authentication, security access
✅ **Other** - Miscellaneous issues

## Notes

- Category names are case-sensitive (use exact spelling)
- Badge CSS uses lowercase with hyphens: `category-database`
- No backend code changes needed - categories stored as strings
- Changes take effect immediately after server restart
