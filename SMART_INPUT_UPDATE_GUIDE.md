# Smart-Input.html Update Guide

## Required Changes to Fix Smart-Input Modal Integration

The file `frontend/smart-input.html` has been successfully restored from the archive. Here's what needs to be updated:

### 1. Update API_BASE (Line 508)
**Current:**
```javascript
const API_BASE = 'http://localhost:8000/api';
```

**Change to:**
```javascript
const API_BASE = 'http://localhost:8881/api/unified';
```

### 2. Update All API Endpoint Paths
Replace all instances of `/session/sessions` with `/session`:

- Line 526: `${API_BASE}/session/sessions` → `${API_BASE}/session`
- Line 589: `${API_BASE}/session/sessions/active` → `${API_BASE}/session/active`
- Line 617: `${API_BASE}/session/sessions/${sessionId}/activate` → `${API_BASE}/session/${sessionId}/activate`
- Line 650: `${API_BASE}/session/sessions/${currentSession.id}/current-draw` → `${API_BASE}/session/${currentSession.id}/current-draw`
- Line 812: `${API_BASE}/session/sessions/${currentSession.id}/draws/${currentDrawData.draw_number}` → `${API_BASE}/session/${currentSession.id}/draws/${currentDrawData.draw_number}`
- Line 882: `${API_BASE}/session/sessions` → `${API_BASE}/session`
- Line 919: `${API_BASE}/session/sessions/${currentSession.id}/draws` → `${API_BASE}/session/${currentSession.id}/draws`
- Line 965: `${API_BASE}/session/sessions/${currentSession.id}/draws` → `${API_BASE}/session/${currentSession.id}/draws`
- Line 973: `${API_BASE}/session/sessions/${currentSession.id}/draws/${draw.draw_number}` → `${API_BASE}/session/${currentSession.id}/draws/${draw.draw_number}`

### 3. Add Lottery Schedule Management (Before line 858)
Insert these functions before `showCreateSessionModal()`:

```javascript
// Lottery Schedule Management
let lotterySchedule = [];

function addLotteryToSchedule() {
    const dayOffset = parseInt(document.getElementById('daySelect').value);
    const lotteryName = document.getElementById('lotteryNameInput').value.trim();

    if (!lotteryName) {
        showMessage('Veuillez entrer un nom de loto', 'error');
        return;
    }

    lotterySchedule.push({ day_offset: dayOffset, lottery_name: lotteryName });
    updateScheduleDisplay();

    // Reset inputs
    document.getElementById('lotteryNameInput').value = '';
}

function removeLotteryFromSchedule(index) {
    lotterySchedule.splice(index, 1);
    updateScheduleDisplay();
}

function updateScheduleDisplay() {
    const container = document.getElementById('scheduleItems');
    const dayNames = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'];

    if (lotterySchedule.length === 0) {
        container.innerHTML = '<div style="text-align:center;color:#888;padding:10px;">Aucun loto ajouté</div>';
        return;
    }

    container.innerHTML = lotterySchedule.map((item, index) => `
        <div style="display: grid; grid-template-columns: auto 1fr auto; gap: 10px; align-items: center; padding: 8px; background: white; border-radius: 5px; margin-bottom: 5px;">
            <span style="width: 80px;">${dayNames[item.day_offset]}</span>
            <span>${item.lottery_name}</span>
            <button type="button" onclick="removeLotteryFromSchedule(${index})" style="width: 80px; padding: 5px; background: #ff4d4f; color: white; border: none; border-radius: 5px; cursor: pointer;">Retirer</button>
        </div>
    `).join('');
}
```

### 4. Update showCreateSessionModal() (Line 858)
**Replace:**
```javascript
function showCreateSessionModal() {
    document.getElementById('createSessionModal').style.display = 'block';
}
```

**With:**
```javascript
function showCreateSessionModal() {
    // Set start date to today
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('startDate').value = today;

    // Reset and display schedule
    lotterySchedule = [];
    updateScheduleDisplay();

    document.getElementById('createSessionModal').style.display = 'block';
}
```

### 5. Update Session Creation Form Submission (Lines 867-895)
**Replace the sessionData object and fetch call:**

```javascript
const range = document.getElementById('numberRange').value.split('-');
const startDate = document.getElementById('startDate').value;
const lotteryType = document.getElementById('lotteryType').value;

// Create lottery schedule - use provided schedule or create default
let schedule = lotterySchedule.length > 0 ? lotterySchedule : [
    { day_offset: 0, lottery_name: lotteryType }
];

const sessionData = {
    name: document.getElementById('sessionName').value,
    description: document.getElementById('sessionDescription').value,
    lottery_type: lotteryType,
    numbers_per_draw: parseInt(document.getElementById('numbersPerDraw').value),
    total_draws: parseInt(document.getElementById('totalDraws').value),
    number_range_min: parseInt(range[0]),
    number_range_max: parseInt(range[1]),
    start_date: startDate,
    lottery_schedule: schedule,
    cycle_length: 7  // Weekly cycle
};

try {
    const response = await fetch(`${API_BASE}/session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sessionData)
    });

    const result = await response.json();

    if (response.ok) {
        showMessage('✨ Session créée avec succès!', 'success');
        closeCreateSessionModal();
        
        // Try to activate the newly created session
        if (result.session_id) {
            document.getElementById('sessionSelect').value = result.session_id;
            await activateSession();
        }
        
        await loadSessions();
        await loadActiveSession();
```

## Next Steps

1. Review these changes
2. I can apply them programmatically (with the risk of more tool errors) OR
3. You can manually edit the file using this guide

Which approach would you prefer?
