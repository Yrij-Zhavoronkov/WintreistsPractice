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

    # ���������, �������� �� ���� ������ ���� .ui
    if ($filePath -like "*.ui") {
        Write-Host "File $filePath $changeType"
        
        # ��������� .bat ���� compile.bat �� ��� �� ����������
        $batFilePath = Join-Path -Path $PSScriptRoot -ChildPath "compile.bat"
        Start-Process -FilePath $batFilePath -NoNewWindow
    }
}

# ���������, ���������� �� ��� ������ ������� � ����� ���������������
if (Get-EventSubscriber -SourceIdentifier "FileChanged" -ErrorAction SilentlyContinue) {
    Unregister-Event -SourceIdentifier "FileChanged"
}

# ������������ ����� ������ �������
Register-ObjectEvent $watcher Changed -SourceIdentifier FileChanged -Action $action

# ������ ����������
$watcher.EnableRaisingEvents = $true

# �������� ������� ���������� ������� (��� ����������� �����������)
while ($true) {
    Start-Sleep -Seconds 1
}