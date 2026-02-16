# PowerShell script to update smart-input.html
$filePath = "c:\Users\User\eazzycalculator\frontend\smart-input.html"

Write-Host "Reading file..." -ForegroundColor Cyan
$content = Get-Content $filePath -Raw -Encoding UTF8

Write-Host "Step 1: Updating API_BASE..." -ForegroundColor Yellow
$content = $content -replace "const API_BASE = 'http://localhost:8000/api';", "const API_BASE = 'http://localhost:8881/api/unified';"

Write-Host "Step 2: Updating API endpoints..." -ForegroundColor Yellow
$content = $content -replace '\$\{API_BASE\}/session/sessions', '${API_BASE}/session'

Write-Host "Step 3: Adding lottery schedule management functions..." -ForegroundColor Yellow
$lotteryFunctions = @"

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

            container.innerHTML = lotterySchedule.map((item, index) => ``
                <div style="display: grid; grid-template-columns: auto 1fr auto; gap: 10px; align-items: center; padding: 8px; background: white; border-radius: 5px; margin-bottom: 5px;">
                    <span style="width: 80px;">`${dayNames[item.day_offset]}</span>
                    <span>`${item.lottery_name}</span>
                    <button type="button" onclick="removeLotteryFromSchedule(`${index})" style="width: 80px; padding: 5px; background: #ff4d4f; color: white; border: none; border-radius: 5px; cursor: pointer;">Retirer</button>
                </div>
            ``).join('');
        }

"@

# Insert before showCreateSessionModal
$content = $content -replace '(        // Gestion du modal)', "$lotteryFunctions`$1"

Write-Host "Step 4: Updating showCreateSessionModal..." -ForegroundColor Yellow
$oldModal = @"
        function showCreateSessionModal\(\) \{
            document\.getElementById\('createSessionModal'\)\.style\.display = 'block';
        \}
"@

$newModal = @"
        function showCreateSessionModal() {
            // Set start date to today
            const today = new Date().toISOString().split('T')[0];
            document.getElementById('startDate').value = today;

            // Reset and display schedule
            lotterySchedule = [];
            updateScheduleDisplay();

            document.getElementById('createSessionModal').style.display = 'block';
        }
"@

$content = $content -replace $oldModal, $newModal

Write-Host "Step 5: Updating session creation form..." -ForegroundColor Yellow
$oldSessionData = @"
            const range = document\.getElementById\('numberRange'\)\.value\.split\('-'\);
            const sessionData = \{
                name: document\.getElementById\('sessionName'\)\.value,
                description: document\.getElementById\('sessionDescription'\)\.value,
                lottery_type: document\.getElementById\('lotteryType'\)\.value,
                numbers_per_draw: parseInt\(document\.getElementById\('numbersPerDraw'\)\.value\),
                total_draws: parseInt\(document\.getElementById\('totalDraws'\)\.value\),
                number_range_min: parseInt\(range\[0\]\),
                number_range_max: parseInt\(range\[1\]\)
            \};

            try \{
                const response = await fetch\(`\$\{API_BASE\}/session`, \{
                    method: 'POST',
                    headers: \{ 'Content-Type': 'application/json' \},
                    body: JSON\.stringify\(sessionData\)
                \}\);

                const result = await response\.json\(\);

                if \(response\.ok\) \{
                    showMessage\('✨ Session créée avec succès!', 'success'\);
                    closeCreateSessionModal\(\);
                    await loadSessions\(\);
                    await loadActiveSession\(\);
"@

$newSessionData = @"
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
"@

$content = $content -replace $oldSessionData, $newSessionData

Write-Host "Saving updated file..." -ForegroundColor Cyan
$content | Set-Content $filePath -Encoding UTF8 -NoNewline

Write-Host "✅ Update complete!" -ForegroundColor Green
Write-Host "File updated: $filePath" -ForegroundColor Green
