
# Daily Tasks Reporting Automation
We spend 15-40 minutes a day for sharing our YTB (Yesterday, Today, Blockers) status.
However, most of the time we forget to "document" the status or do it inaccurate.
This happens because it's annoying to work with graphical task management systems.
Below I'm presenting my experience in automating this daily routine using textual UI.


## Work management systems
There are many out there:
Jira, Azure Devops, Monday etc.

### Benefits:
* Transparency - You know the shared work's status.
* Unification- Common language. Task, Bug, Sprint, YTB etc.
* Flow management- Rules to move from stage to stage.
* Predictability- Ability to plan the future work.

### Drawback: Human factor
All the benefits are achievable only if the system's data is accurate.
So...
How many times did you hear/tell/think during your Dalies/Stand up meetings/STUMs/YTBs:
"It was couple of hours, was lazy to open a task/bug".
"Forgot to add working hours to this task"
"Had lots of context switches. No idea how much total time did it take"
"I'll fill it tomorrow before the daily meeting..."
"Any way nobody will read this..."


## TL/DR
Daily actions - actions you do on your tasks: Status changes, work planning, work hours updates, commenting.
Below is an example of a textual format for reporting workers' daily actions:
```
>ClLOSED:
[user_story 1002 #Backend] -> task 1003 # Kubernetes Service :actions: +2, comment Created YAML file generator.
[user_story 1002 #Backend] -> bug # QA Nginx cache configuration :actions: 2, +1, comment Time units misconfiguration- hours instead of seconds.
```
* Task 1003- Add 2 hours to the effort
* Task 1003- Add a comment "Created YAML file generator".
* Task 1003- Move to closed.
* Bug QA Nginx- Created, with estimation 2 hours
* Bug QA Nginx- Add 1 hour to the effort
* Bug QA Nginx- Add a comment "Time units misconfiguration....".
* Bug QA Nginx- Move to closed.

Filled by each team member. Checked for input/format errors and pushed to the Task Management System via API.


## My solutions' Benefits:
* Simplifying the world to the minimal needed set of statuses and actions.
* Easy arithmetic calculations help understand time proportions:
  - Reporting +2 hours on a planned task
  - Reporting +4 hours on a planned bug
  - Oh! Forgot to open new bug on yesterdays prod issue: Reporting 2 planned, +4 hours spent, title and comment.
  total: +2 +4 +4 = 10 hours of work, sound correct for yesterday.
* Pre submission validations:
  - Do you have a parent, title, comment, planned time in a new task/bug?


## Assumptions
* Automate everything you do recurrently.
* Typing is quicker than clicking.
* Use API as much as you can.
* DIY program = fun. Customizable solution configuration, reconfiguration, rereconfiguration ... = not fun.


#Task lifetime <Status> and your `action`:
* `Creating` task- <New> task. No work performed on the task yet.
* `Working` on a task- <Active> task. You are investing yours and only yours time in the task.
* `Informing` other worker you are waiting for him- <Blocked> task. Active waiting: sending reminders, escalating.
* `Reaching` the desired state- <Closed> task. From now on - only new tasks and bugs.

Status neutral actions:


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
