$action = New-ScheduledTaskAction -Execute "repoagent" -Argument "daemon start"
$trigger = New-ScheduledTaskTrigger -AtLogOn
Register-ScheduledTask -TaskName "RepoAgent" -Action $action -Trigger $trigger -Description "Start Repo Agent daemon"
