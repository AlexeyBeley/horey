# jenkins_deployer


## Assumptions

* Master uses spot-fleet agents.
* Master accessible from outside and has no strong permissions. 
  All permissions are in agents' roles.
  * Jenkins master in public subnet.
  * Jenkins agents in private.
  * Master ssh-key unique.
  * Jenkins master connects agents using other ssh key. Nobody except master knows it.
  
* EBS device DeleteOnTermination = False. In order to attach existing volume to new ec2-instance,
I use a secondary drive to hold jenkins data in. /dev/sda1 can not be specified at ec2-creation time.
* Logs are stored in separate ebs - sometimes log rotation is misconfigured and can lead to storage leak.


```
. Trigger asynchronously N jobs.
. Uses protection mechanism (uid_parameter_name) - to identify the build. It overcomes Jenkins' bug of "loosing" queue_item build
  This is a regular parameter. But it used for system functionality. No need to be set explicitly. The code handles it. 
. Repo
```