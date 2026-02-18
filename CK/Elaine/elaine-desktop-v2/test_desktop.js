/**
 * ELAINE Desktop v2.0 — Manual Test Checklist
 *
 * Run: npm start
 * Then verify each item below:
 *
 * [ ] App launches without errors
 * [ ] Server URL loads (not blank, not error page)
 * [ ] Tray icon visible (gold E)
 * [ ] Window close → goes to tray (balloon notification appears)
 * [ ] Tray click → toggles window visibility
 * [ ] Right-click tray → context menu with all items
 * [ ] "Open ELAINE" menu item → restores window
 * [ ] "Morning Briefing" menu item → triggers API call
 * [ ] "Open in Browser" → opens http://172.18.240.96:5000 in default browser
 * [ ] "Quit ELAINE" → exits cleanly (no process left behind)
 * [ ] Auto-start entry in registry confirmed:
 *     PowerShell: Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
 * [ ] Offline page shows when server is down (stop ELAINE server, then launch app)
 *
 * All items must pass before shipping.
 */

console.log('ELAINE Desktop v2.0 — Test Checklist')
console.log('Run this file for reference only. Tests are manual.')
console.log('See comments above for the full checklist.')
