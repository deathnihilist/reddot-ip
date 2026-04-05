# Reddot Auto-Push Sentinel
$path = Get-Location
Write-Host "Reddot Sentinel is watching: $path" -ForegroundColor Cyan

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $path
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true

# Action saat ada file berubah
$action = {
    $path = $Event.SourceEventArgs.FullPath
    $name = $Event.SourceEventArgs.Name
    $changeType = $Event.SourceEventArgs.ChangeType
    
    # Abaikan folder .git
    if ($path -notlike "*\.git\*") {
        Write-Host "Change detected in $name ($changeType). Syncing to GitHub..." -ForegroundColor Yellow
        git add .
        git commit -m "Auto-sync: $name modified"
        git push origin main
        Write-Host "Successfully synced to GitHub!" -ForegroundColor Green
    }
}

# Daftarkan event untuk file Changed, Created, dan Deleted
Register-ObjectEvent $watcher "Changed" -Action $action
Register-ObjectEvent $watcher "Created" -Action $action
Register-ObjectEvent $watcher "Deleted" -Action $action

while ($true) { Start-Sleep 1 }
