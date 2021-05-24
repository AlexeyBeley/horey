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
