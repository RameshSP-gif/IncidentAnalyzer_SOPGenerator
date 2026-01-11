# Knowledge Base Management Guide

## Overview

The Knowledge Base Management interface allows you to view, search, edit, and delete all incidents stored in MongoDB. This is a complete CRUD (Create, Read, Update, Delete) management system for your incident knowledge base.

## Accessing Knowledge Base Management

### From Main Page
Click the **"Manage Knowledge Base"** button in the header of the main page at **http://127.0.0.1:5000**

### Direct URL
Navigate directly to: **http://127.0.0.1:5000/manage**

## Features

### 1. **Statistics Bar**
At the top of the page, you'll see real-time statistics:
- **Total Incidents**: Total number of incidents in knowledge base
- **Resolved Incidents**: Number of incidents with resolution notes
- **Filtered Results**: Number of results matching your current search/filter

### 2. **Search and Filter**
- **Search Box**: Search incidents by:
  - Incident number (e.g., "INC0001234")
  - Short description
  - Detailed description
  - Any text content
- **Category Filter**: Filter by incident category:
  - Email
  - Network
  - Hardware
  - Software
  - Database
  - Access/Security

### 3. **Pagination**
- Displays **10 incidents per page**
- Navigate between pages using **Previous** and **Next** buttons
- Shows current page number and total number of records
- Pagination respects search and filter criteria

### 4. **Incident Table**
Displays all incidents with the following columns:
- **Incident #**: Unique incident identifier (colored link)
- **Description**: Short description of the incident
- **Category**: Color-coded category badge
- **Priority**: Priority level (P1, P2, P3, P4)
- **Actions**: View, Edit, Delete buttons

### 5. **CRUD Operations**

#### **VIEW** (👁️ Eye Icon)
- Opens a read-only modal showing full incident details
- Includes:
  - Incident number
  - Short description
  - Detailed description
  - Category and priority
  - Resolution notes
- Click the X button to close

#### **EDIT** (✏️ Pencil Icon)
- Opens edit modal with all incident fields
- Editable fields:
  - Short Description
  - Detailed Description
  - Category (dropdown)
  - Priority (1-4)
  - Resolution Notes
- Click "Save Changes" to update
- Click "Cancel" to discard changes
- Changes are immediately reflected in MongoDB

#### **DELETE** (🗑️ Trash Icon)
- Removes incident from knowledge base
- Requires confirmation to prevent accidental deletion
- Deleted incidents are permanently removed from MongoDB

### 6. **Refresh Button**
- Reloads all incidents from MongoDB
- Clears search and filter
- Returns to page 1

### 7. **Back to Main Button**
- Returns to the main SOP Generator interface at http://127.0.0.1:5000

## Database Operations

### Data Storage
- All incidents are stored in **MongoDB** collection: `incident_analyzer.knowledge_base`
- Automatic fallback to JSON file if MongoDB is unavailable
- Real-time synchronization with RAG resolution finder

### Field Descriptions

| Field | Description | Required |
|-------|-------------|----------|
| **Incident Number** | Unique identifier (read-only) | Yes |
| **Short Description** | One-line summary (max 100 chars) | Yes |
| **Detailed Description** | Full problem description | Yes |
| **Category** | Incident classification | Yes |
| **Priority** | 1=Critical, 2=High, 3=Medium, 4=Low | Yes |
| **Resolution Notes** | Steps to resolve the incident | Yes |

### Automatic Fields
These are automatically managed by the system:
- `added_at`: When incident was added to KB
- `updated_at`: When incident was last modified
- `resolution_length`: Length of resolution notes (for RAG filtering)
- `source`: Where incident came from (CSV Import, Manual, etc.)

## Search Examples

### By Incident Number
Search for: `INC0001234`
Returns: All incidents with that number

### By Problem Type
Search for: `database connection`
Returns: All incidents with "database" or "connection" in any field

### Combined Search + Filter
- Search: `unable`
- Filter: `Database`
- Returns: All database incidents containing "unable"

## Workflow Examples

### Example 1: Find and Update a Resolution
1. Search for incident by number or description
2. Click the **Edit** button (✏️)
3. Update the "Resolution Notes" field
4. Click "Save Changes"
5. RAG system automatically reloads updated knowledge base

### Example 2: Remove Duplicate Incident
1. Search for the duplicate incident
2. Click the **Delete** button (🗑️)
3. Confirm deletion
4. Incident is removed from MongoDB

### Example 3: Review All Database Incidents
1. Select "Database" from Category Filter
2. Browse through pages
3. Click **View** (👁️) on any incident to see full details
4. Use **Previous/Next** to navigate pages

## Tips and Best Practices

### Data Quality
✅ **DO:**
- Keep descriptions concise but informative
- Include specific error messages in descriptions
- Document exact resolution steps
- Update resolutions with lessons learned

❌ **DON'T:**
- Leave fields empty
- Use vague descriptions like "Issue"
- Skip important resolution details

### Search Efficiency
- Use specific keywords from incident descriptions
- Filter by category first, then search
- Use incident numbers for exact matches

### Performance
- Knowledge base loads quickly even with 1000+ incidents
- Pagination ensures responsive table rendering
- Search is real-time and instant

## Technical Details

### API Endpoints Used
- `GET /get_knowledge_base` - Retrieve all incidents
- `PUT /update_incident/<number>` - Update incident
- `DELETE /delete_incident/<number>` - Delete incident

### Database Schema
```
{
  "_id": ObjectId,
  "number": "INC0001234",
  "short_description": "...",
  "description": "...",
  "category": "Database",
  "priority": "1",
  "resolution_notes": "...",
  "resolution_length": 150,
  "added_at": "2026-01-11T07:25:32.854542",
  "updated_at": "2026-01-11T07:52:48.711",
  "source": "CSV Import"
}
```

## Troubleshooting

### No Incidents Showing
- Click "Refresh" button
- Check MongoDB connection status in server logs
- Verify incidents were imported via CSV Import tab

### Search Not Working
- Ensure search text matches incident content
- Clear search box and try again
- Try category filter instead

### Edit/Delete Not Working
- Check server logs for errors
- Ensure MongoDB is connected
- Try refreshing the page

### Changes Not Reflecting
- Click "Refresh" button
- MongoDB may need a moment to sync
- Check browser console for JavaScript errors

## Support

For issues or questions:
1. Check server logs at application startup
2. Verify MongoDB connection: `[INFO] Connected to MongoDB`
3. Review incident data in `/data/knowledge_base.json` (backup location)
