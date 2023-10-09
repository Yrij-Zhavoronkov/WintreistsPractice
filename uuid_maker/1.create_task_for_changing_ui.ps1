$folderPath = "$PSScriptRoot"
$filter = "*.ui"
$includeSubdirectories = $false

$watcher = New-Object System.IO.FileSystemWatcher $folderPath, $filter -Property @{
    IncludeSubdirectories = $includeSubdirectories
    NotifyFilter = [System.IO.NotifyFilters]::LastWrite -bor [System.IO.NotifyFilters]::FileName
}

$action = { 
    $filePath = $Event.SourceEventArgs.FullPath
    $changeType = $Event.SourceEventArgs.ChangeType

    # Проверяем, является ли файл файлом типа .ui
    if ($filePath -like "*.ui") {
        Write-Host "File $filePath $changeType"
        
        # Запускаем .bat файл compile.bat из той же директории
        $batFilePath = Join-Path -Path $PSScriptRoot -ChildPath "compile.bat"
        Start-Process -FilePath $batFilePath -NoNewWindow
    }
}

# Проверяем, существует ли уже объект события с таким идентификатором
if (Get-EventSubscriber -SourceIdentifier "FileChanged" -ErrorAction SilentlyContinue) {
    Unregister-Event -SourceIdentifier "FileChanged"
}

# Регистрируем новый объект события
Register-ObjectEvent $watcher Changed -SourceIdentifier FileChanged -Action $action

# Начать мониторинг
$watcher.EnableRaisingEvents = $true

# Ожидание вечного выполнения скрипта (для продолжения мониторинга)
while ($true) {
    Start-Sleep -Seconds 1
}