@echo off
echo Disabling local DEV.to posting service...
schtasks /delete /tn DEVtoPostingService /f
echo Done! The local service has been disabled.
echo The GitHub Actions workflow will now handle all posting.
pause
