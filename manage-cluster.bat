@echo off
SET COMMAND=%1
IF "%COMMAND%"=="" SET COMMAND=start

wsl -d Ubuntu -e bash -c "/mnt/d/'FOLLOW UP FINDER'/followupfinder/manage-cluster.sh %COMMAND%"

