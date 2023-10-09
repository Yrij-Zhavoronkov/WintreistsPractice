$eventIdentifier = "FileChanged"

# Проверяем, существует ли объект события с указанным идентификатором
if (Get-EventSubscriber -SourceIdentifier $eventIdentifier -ErrorAction SilentlyContinue) {
    # Отключаем объект события
    Unregister-Event -SourceIdentifier $eventIdentifier
    Write-Host "File change tracking for .ui files has been disabled."
} else {
    Write-Host "File change tracking for .ui files is not currently active."
}