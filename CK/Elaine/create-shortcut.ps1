$ws = New-Object -ComObject WScript.Shell
$desktop = $ws.SpecialFolders("Desktop")
$sc = $ws.CreateShortcut("$desktop\ELAINE.lnk")
$sc.TargetPath = "$PSScriptRoot\launch-elaine.bat"
$sc.WorkingDirectory = $PSScriptRoot
$sc.Description = "ELAINE - Chief of Staff - Almost Magic Tech Lab"
$sc.IconLocation = "C:\Windows\System32\shell32.dll,13"
$sc.Save()
Write-Host "Desktop shortcut created: $desktop\ELAINE.lnk"
