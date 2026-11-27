# Provision Constructor 
Provision Constructor used to provision linux based environments as a code.

##Concepts:
* System_function: some function of a system. It can be as small as an apt package or 
  set of package+cpnfiguration files. Or even a set of packages.
* System function has unit-test: a test performed in order to check weather the system function was already deployed.
* Provision Constructor is being deployed in the target and then provisions all the system_functions needed.  
  
