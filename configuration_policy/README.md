# Configuration

## Avoid unneeded inharitance. For example:
Jenkins_Deployment_configuration:
    infrastructure- host type (ec2/docker...)
        hostname - part of infrastructure
    provisioning- users, jobs, plugins
    
  
Jenkins_Operations_configuration:
    hostname,
    protocol,
    port,
    username,
    password
    
These are 2 configurations with a very different parameters with a single
common parameter 

## Each configuration part parameters should start with common prefix 
For example "hostname" can be present in different configurations- you can't inherit from both.

## No lowering grade:
Once set to prod, in future assignments can't be set to stg.

## Parameter can't be redeclared after inheritance

    1) No methods. Configuration is a static data - you can set or get values.
    2) Configuration context is immutable - once you set context rules, ancestors can not change the rules.
    3) Every value being set must be defined in a property.
    * Property can be defined only at one level of inheritance.
    * Set attribute with name "attribute_name" only when self has "_attribute_name" attribute.

each step of configuration components change must be logged the most comfort for understanding way:
if there were N files applied at the end there should be complete list of files' full paths.

Policy rules examples:
* Static value
* Auto formated value - raise exception if required components' values were not set.
  e.g. dns_name = "{host_name}-{environment_grade}.{environment_name}.{domain}.com"
  if host_name is None: raise
* Restricted by number of possibilities: Enum
* Type/Regex/range restrictions
* Custom rules: see more detailed examples below.
* Sanity check - check whether all configs were set.  
* Aliases - if the same thing has multiple names
