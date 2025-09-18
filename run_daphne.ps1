# run_daphne.ps1
$env:DJANGO_SETTINGS_MODULE="tracker.settings"
daphne tracker.asgi:application