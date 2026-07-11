# How-to: Record Manual Events with Google Forms

This guide shows how to record manual aquarium maintenance events (water changes, fertilizer additions) using Google Forms and Apps Script.

## Overview

Manual interventions are recorded in the `control_events` BigQuery table alongside automated events. This enables causal inference analysis (e.g., "Did the water change improve water quality?").

**Phase 1 Solution**: Google Forms + Apps Script
- **Setup time**: ~30 minutes
- **Cost**: Free (within Google Workspace limits)
- **UI**: Smartphone-friendly form

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Create Google Form](#create-google-form)
3. [Set Up Apps Script](#set-up-apps-script)
4. [Configure BigQuery Access](#configure-bigquery-access)
5. [Test the Integration](#test-the-integration)
6. [Usage](#usage)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Google account (same account used for GCP)
- BigQuery dataset with `control_events` table created (see [Implementation Guide](../guides/aquarium-thermostat-complete-manual.md))
- GCP project ID

---

## Create Google Form

### Step 1: Create Form

1. Go to [Google Forms](https://forms.google.com)
2. Click **+ Blank** to create a new form
3. Title: "AquaPulse Manual Events"

### Step 2: Add Form Fields

#### Field 1: Event Type (Required)

- **Question**: Event Type
- **Type**: Multiple choice
- **Options**:
  - Manual Maintenance
  - Manual Dosing (Fertilizer/Chemicals)
  - Other
- **Required**: Yes

#### Field 2: Action (Required)

- **Question**: Action
- **Type**: Dropdown
- **Options**:
  - Water Change
  - Water Addition
  - Filter Cleaning
  - Fertilizer Addition
  - Conditioner Addition
  - pH Adjuster Addition
  - Other
- **Required**: Yes

#### Field 3: Volume/Amount (Optional)

- **Question**: Volume or Amount
- **Type**: Short answer
- **Validation**: Number, Greater than 0
- **Description**: "Liters for water, mL for chemicals"
- **Required**: No

#### Field 4: Product Name (Optional)

- **Question**: Product Name (for chemicals/fertilizers)
- **Type**: Short answer
- **Required**: No

#### Field 5: Notes (Optional)

- **Question**: Notes
- **Type**: Paragraph
- **Description**: "Any additional information (e.g., reason for maintenance, observations)"
- **Required**: No

### Step 3: Configure Form Settings

1. Click **Settings** (gear icon)
2. Under **Responses**:
   - ☑ Collect email addresses (optional, for tracking)
   - ☑ Limit to 1 response (uncheck this)
3. Click **Save**

---

## Set Up Apps Script

### Step 1: Open Script Editor

1. In your Google Form, click **⋮** (More) → **Script editor**
2. This opens the Apps Script editor

### Step 2: Write Apps Script

Delete the default code and paste the following:

```javascript
// Configuration
const PROJECT_ID = 'your-gcp-project-id'; // Replace with your GCP project ID
const DATASET_ID = 'aquapulse';           // Replace if different
const TABLE_ID = 'control_events';

/**
 * Triggered when form is submitted
 */
function onFormSubmit(e) {
  try {
    const responses = e.response.getItemResponses();
    
    // Extract form data
    const eventType = getResponseValue(responses, 'Event Type');
    const action = getResponseValue(responses, 'Action');
    const volume = getResponseValue(responses, 'Volume or Amount');
    const productName = getResponseValue(responses, 'Product Name');
    const notes = getResponseValue(responses, 'Notes');
    
    // Map form values to BigQuery schema
    const eventTypeMap = {
      'Manual Maintenance': 'manual_maintenance',
      'Manual Dosing (Fertilizer/Chemicals)': 'manual_dosing',
      'Other': 'manual_other'
    };
    
    const actionMap = {
      'Water Change': 'water_change',
      'Water Addition': 'water_addition',
      'Filter Cleaning': 'filter_cleaning',
      'Fertilizer Addition': 'fertilizer_add',
      'Conditioner Addition': 'conditioner_add',
      'pH Adjuster Addition': 'ph_adjuster_add',
      'Other': 'other'
    };
    
    // Build action_details JSON
    const actionDetails = {};
    if (volume) {
      // Infer unit from action type
      if (action.includes('Water')) {
        actionDetails.volume_liters = parseFloat(volume);
      } else {
        actionDetails.volume_ml = parseFloat(volume);
      }
    }
    if (productName) actionDetails.product_name = productName;
    if (notes) actionDetails.notes = notes;
    
    // Build BigQuery row
    const row = {
      event_id: Utilities.getUuid(),
      timestamp: new Date().toISOString(),
      event_type: eventTypeMap[eventType] || 'manual_other',
      device_id: null,
      action: actionMap[action] || 'other',
      action_details: actionDetails,
      trigger_type: 'manual',
      trigger_sensor_id: null,
      trigger_value: null,
      trigger_threshold: null,
      success: true,
      error_message: null,
      duration_ms: null
    };
    
    // Insert into BigQuery
    insertBigQuery(row);
    
    Logger.log('Successfully inserted event: ' + row.event_id);
  } catch (error) {
    Logger.log('Error: ' + error.message);
    // Optionally, send email notification on error
    // MailApp.sendEmail('your-email@example.com', 'Form Error', error.message);
  }
}

/**
 * Helper: Get response value by question title
 */
function getResponseValue(responses, questionTitle) {
  for (let i = 0; i < responses.length; i++) {
    if (responses[i].getItem().getTitle() === questionTitle) {
      return responses[i].getResponse();
    }
  }
  return null;
}

/**
 * Insert row into BigQuery
 */
function insertBigQuery(row) {
  const tableUrl = `https://bigquery.googleapis.com/bigquery/v2/projects/${PROJECT_ID}/datasets/${DATASET_ID}/tables/${TABLE_ID}/insertAll`;
  
  const payload = {
    rows: [{
      insertId: row.event_id,
      json: row
    }]
  };
  
  const options = {
    method: 'post',
    contentType: 'application/json',
    headers: {
      'Authorization': 'Bearer ' + ScriptApp.getOAuthToken()
    },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };
  
  const response = UrlFetchApp.fetch(tableUrl, options);
  const result = JSON.parse(response.getContentText());
  
  if (result.insertErrors) {
    throw new Error('BigQuery insert failed: ' + JSON.stringify(result.insertErrors));
  }
}
```

### Step 3: Update Configuration

Replace the placeholders in the script:

```javascript
const PROJECT_ID = 'your-gcp-project-id'; // e.g., 'aquapulse-prod-123456'
const DATASET_ID = 'aquapulse';           // BigQuery dataset name
const TABLE_ID = 'control_events';        // Table name
```

### Step 4: Save Script

1. Click **💾 Save** (or Ctrl+S)
2. Name the project: "AquaPulse Form to BigQuery"

---

## Configure BigQuery Access

### Step 1: Enable BigQuery API

1. In Apps Script editor, click **Services** (+) icon
2. Search for "BigQuery API"
3. Click **Add**

### Step 2: Grant OAuth Scopes

1. In Apps Script, click **Project Settings** (gear icon)
2. Scroll to **OAuth Scopes**
3. Ensure these scopes are listed:
   - `https://www.googleapis.com/auth/bigquery`
   - `https://www.googleapis.com/auth/bigquery.insertdata`
   - `https://www.googleapis.com/auth/forms`

(These are added automatically when you use BigQuery API in the script)

### Step 3: Set Up Trigger

1. In Apps Script editor, click **⏰ Triggers** (clock icon)
2. Click **+ Add Trigger**
3. Configure:
   - **Function**: `onFormSubmit`
   - **Event source**: From form
   - **Event type**: On form submit
4. Click **Save**
5. **Authorize**: A popup will ask for permissions
   - Click **Review Permissions**
   - Select your Google account
   - Click **Advanced** → **Go to AquaPulse Form to BigQuery (unsafe)**
   - Click **Allow**

---

## Test the Integration

### Step 1: Submit Test Event

1. Open your Google Form
2. Fill in test data:
   - Event Type: Manual Maintenance
   - Action: Water Change
   - Volume: 5
   - Notes: Test submission
3. Click **Submit**

### Step 2: Check Apps Script Logs

1. In Apps Script editor, click **⚙️ Executions**
2. You should see a recent execution
3. Click to view logs
4. Look for: `Successfully inserted event: <UUID>`

### Step 3: Verify BigQuery

Run this query in BigQuery console:

```sql
SELECT *
FROM `your-project-id.aquapulse.control_events`
WHERE event_type = 'manual_maintenance'
ORDER BY timestamp DESC
LIMIT 5;
```

You should see your test event.

---

## Usage

### Daily Operations

1. **After water change**: Open form on smartphone, submit entry
2. **After fertilizer addition**: Submit with product name and volume
3. **Notes**: Add any observations (e.g., "Fish seemed stressed before water change")

### Best Practices

- **Record immediately**: Don't wait (easy to forget details)
- **Be specific**: Use notes field for context
- **Consistency**: Use same product names (helps with analysis)
- **Corrections**: If you make a mistake, you can:
  - Submit correction with note "Correction for event at HH:MM"
  - Or manually edit in BigQuery console (not recommended)

---

## Troubleshooting

### Issue 1: Form submission succeeds, but no BigQuery entry

**Check**:
1. Apps Script **Executions** tab for errors
2. Verify `PROJECT_ID`, `DATASET_ID`, `TABLE_ID` in script
3. Ensure BigQuery table exists

**Solution**:
- Open Apps Script editor → **Executions** → View error details
- Common issue: OAuth permissions not granted (re-authorize trigger)

### Issue 2: "Access Denied" error in Apps Script logs

**Check**:
- Service account or OAuth permissions

**Solution**:
1. Re-run authorization flow (delete and re-create trigger)
2. Ensure your Google account has BigQuery Data Editor role in GCP

### Issue 3: Volume field validation fails

**Check**:
- Form field validation is set to "Number, Greater than 0"

**Solution**:
- Remove validation temporarily
- Or adjust validation to "Text" (validation will happen in Apps Script)

### Issue 4: `action_details` is empty in BigQuery

**Check**:
- Optional fields were left blank

**This is normal**: `action_details` can be null/empty if volume/product/notes are not provided.

---

## Phase 2 Enhancements

Future improvements:

1. **Dropdown with autocomplete**: Pre-populate product names from past entries
2. **Photo upload**: Attach images to events (store in Cloud Storage)
3. **Offline support**: Queue submissions when offline, sync later
4. **Web UI**: Custom interface with better UX (replace Google Forms)

---

## Related Documents

- [ADR-0006: Simplified Schema Design](../decisions/0006-simplified-schema-design.md)
- [Schema Reference](../reference/schema.md)
- [Architecture Snapshot: 2026-07-11 Schema Finalization](../architecture/snapshots/2026-07-11-schema-finalization.md)
- [Implementation Guide: Aquarium Thermostat Complete Manual](../guides/aquarium-thermostat-complete-manual.md)

---

## Quick Reference

### Form Fields → BigQuery Mapping

| Form Field | BigQuery Field | Type |
|------------|----------------|------|
| Event Type | `event_type` | STRING |
| Action | `action` | STRING |
| Volume | `action_details.volume_liters` or `volume_ml` | FLOAT |
| Product Name | `action_details.product_name` | STRING |
| Notes | `action_details.notes` | STRING |
| (auto) | `event_id` | UUID |
| (auto) | `timestamp` | TIMESTAMP |
| (auto) | `trigger_type` | 'manual' |
| (auto) | `success` | true |

### Example BigQuery Entry

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-07-11T10:00:00Z",
  "event_type": "manual_maintenance",
  "device_id": null,
  "action": "water_change",
  "action_details": {
    "volume_liters": 5.0,
    "notes": "Weekly water change"
  },
  "trigger_type": "manual",
  "success": true
}
```
