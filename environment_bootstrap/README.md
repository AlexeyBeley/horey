# jenkins_manager
Class to control several aspects of Jenkins jobs' lifecycle:

## Jobs execution flow:
```
. Trigger asynchronously N jobs.
. Uses protection mechanism (uid_parameter_name) - to identify the build. It overcomes Jenkins' bug of "loosing" queue_item build
  This is a regular parameter. But it used for system functionality. No need to be set explicitly. The code handles it. 
. Report any failures.
```

## Job creation and dumping:
```
. Dump jobs' configuration
. Create jobs from dumps.
```

## Jobs cleanup:
```
. Various methods to clean faulty jobs
```

## Example
Several use case examples in `tests` dir.



#Development:
```buildoutcfg
make recursive_install_from_source_local_venv-jenkins_manager
```
Then set the interpreter to build/_build/_venv

Packer file Provisioner
#{
#  "type": "file",
#  "source": "app.tar.gz",
#  "destination": "/tmp/app.tar.gz"
#}

SSH:
eval `ssh-agent -s`
sudo chmod 400 /tmp/tmp.p 
ssh-add -K /tmp/tmp.p
ssh -o StrictHostKeyChecking=no ubuntu@1.1.1.1

#ppk to pem
brew install putty
puttygen key.ppk -O private-openssh -o key.pem

GIT_SSH_COMMAND="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" git clone
GIT_SSH_COMMAND="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" git push

#/Users/alexey.beley/Library/Caches/JetBrains/PyCharmCE2021.1/index/filetypes


#tmux
##List
tmux ls
##New 
tmux new -s horey

##Detach
Ctrl+b d

##Attach 
tmux attach-session -t horey 

#Options
    Ctrl+b c Create a new window (with shell)
    Ctrl+b w Choose window from a list
    Ctrl+b 0 Switch to window 0 (by number )
    Ctrl+b , Rename the current window
    Ctrl+b % Split current pane horizontally into two panes
    Ctrl+b " Split current pane vertically into two panes
    Ctrl+b o Go to the next pane
    Ctrl+b ; Toggle between the current and previous pane
    Ctrl+b x Close the current pane

~/.ssh/conf
Host github
  HostName github.com
  User git
  IdentityFile /home/whoever/.ssh/id_dsa.bob
  IdentitiesOnly yes

origin	git@github.com:AlexeyBeley/horey.git (fetch)
origin	git@github.com:AlexeyBeley/horey.git (push)

git remote set-url origin git@github:AlexeyBeley/horey.git