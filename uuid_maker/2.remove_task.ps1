$eventIdentifier = "FileChanged"

# ���������, ���������� �� ������ ������� � ��������� ���������������
if (Get-EventSubscriber -SourceIdentifier $eventIdentifier -ErrorAction SilentlyContinue) {
    # ��������� ������ �������
    Unregister-Event -SourceIdentifier $eventIdentifier
    Write-Host "File change tracking for .ui files has been disabled."
} else {
    Write-Host "File change tracking for .ui files is not currently active."
}