
# Daily Reporting Automation

"Daly", "Stand up meeting", "STUM", "YTB"...
Jira, Azure Devops, Monday...

## Assumptions
* Automate everything you do recurrently. 
* Typing is quicker then clicking.


## Line format:
* ParentType - Task/Bug/UserStory/Feature etc.
* ParentID - System UID, if empty parent will be created.
* ParentTitle - Brief summary of the job to be done. 5-7 words.
* ChildType - Task/Bug
* ChildID - System UID, if empty - child will be created.
* ChildTitle - Brief summary of the job to be done. 5-7 words.
* CommaSeparatedActions - Actions to be performed on the Child.

```
[<ParentType> <ParentID> #<ParentTitle>] -> <ChildType> <ChildID> #<ChildTitle> :actions: <CommaSeparatedActions>
```

## Possible content demonstration:
```
[user_story 1000 #Frontend CI/CD] -> task 1001 #Nginx Configuration CI/CD :actions:
[task 1001 #Frontend CI/CD] -> task 1003 #CORS configuration :actions:
[user_story 1000 #Frontend CI/CD] -> bug 1002 #Python version deprecated :actions:
```

## Daily actions' report file types:
* daily.hapi - Current status retrieved from Task management API.
* daily_input.hapi - Reported status. The changes you want to report since the last Daily.
* daily_output.hapi - Generated YTB report. A small bonus, chows you the summary of the above input.

## daily.hapi
* NEW - Nobody works on it: eg. New, Reopen etc.
* ACTIVE - Somebody is working on it or planning to work today.
* BLOCKED - Waiting for human response. eg. On hold, In review, Blocked, Waiting for QA, Waiting For deployment etc.
* CLOSED - Nobody will work on it. eg. Closed, Resolved etc.

```
worker_id:horey@sample.com
>NEW:
[user_story 1000 #Frontend CI/CD] -> task 1001 #Nginx Configuration CI/CD :actions:

>ACTIVE:
[user_story 1002 #Backend] -> task 1003 # Kubernetes Service :actions:
[user_story 1004 #Sprint 888 CI/CD Bugs] -> bug 1005 # Prod Frontend deployment failed :actions:

>BLOCKED:
[user_story 1000 #Frontend CI/CD] -> task 1007 #Nginx Configuration CORS :actions:

>CLOSED:
[user_story 1002 #Backend] -> bug 1009 # Kubernetes Infrastructure :actions:
```

## daily_input.hapi example 1. Reporting task changes.

Updating ACTIVE task 1003 from the example below with following actions:
* Add time spent on the task.
* Move to closed.
* Add comment.
```
>CLOSED:
[user_story 1002 #Backend] -> task 1003 # Kubernetes Service :actions: +2, comment Created YAML file generator.
```


## daily_input.hapi example 2. Creating child (Task/Bug) under existing Parent (UserStory/Feature/Task/Bug/):
* Remove ChildID
* Add assumed time action
```
>NEW:
[user_story 1000 #Frontend CI/CD] -> bug #Nginx config generator breaks QA :actions: 4, comment After adding new options build fail in QA.
```

## daily_input.hapi example 3. Reporting daily changes.
* task 1007: Blocked Moved to closed with a comment.
* task 1001: Moved from new to closed + comment + 6 work hours update.
* user_story 1000: Added new bug- as a result of our 1001 task we broke QA. Making it Active + Added 8 hours estimate + added 1 hour already spent.
* bug 1005: Moved from Active to closed + comment + 2 work hours update
* Creating new task to add test for user signeout failure, Adding 2 hours work estimation and a comment.
* Moving task 1003 back to new since we will work on the bug in Frontend QA today
```
worker_id:horey@sample.com
>NEW:
[user_story #Frontend test enhancemet] -> task #User signout failure test :actions: 2, comment New test use case related to bug 1005.
[user_story 1002 #Backend] -> task 1003 # Kubernetes Service :actions:

>ACTIVE:
[user_story 1000 #Frontend CI/CD] -> bug #Nginx config generator breaks QA :actions: 8, +1 comment After Changing worker type builds are failing in QA.

>BLOCKED:

>CLOSED:
[user_story 1004 #Sprint 888 CI/CD Bugs] -> bug 1005 # Prod Frontend deployment failed :actions: +2, comment Untested bug found
[user_story 1000 #Frontend CI/CD] -> task 1001 #Nginx Configuration CI/CD :actions: +6, comment Changed worker type.
[user_story 1000 #Frontend CI/CD] -> task 1007 #Nginx Configuration CORS :actions: +2, comment Added proper CORS configuration into CI/CD.
[user_story 1002 #Backend] -> bug 1009 # Kubernetes Infrastructure :actions:
```

## daily_output.hapi
* All report lines with action "+hours" - go to "Y"
* All report lines in "active" - go to "T"
```
[30/02/2023] horey
Y:
[user_story 1000 #Frontend CI/CD] -> 1011-Nginx config generator breaks QA
[user_story 1004 #Sprint 888 CI/CD Bugs] -> 1005 -Prod Frontend deployment failed
[user_story 1000 #Frontend CI/CD] -> 1001 #Nginx Configuration CI/CD
[user_story 1000 #Frontend CI/CD] -> 1007 #Nginx Configuration CORS
T:
[user_story 1000 #Frontend CI/CD] -> 1011-Nginx config generator breaks QA
B:
```
