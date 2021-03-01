# Configuration Policy


## In a nutshell
Class implementing base initiating functions.
All attributes are properties. They control values behavior. 


## First rule of ConfigurationPolicy
Never ever redefine properties at other levels. You need to redefine a property->
it means you need another behavior -> it means you need another property! Do not be afraid to have alike values for
different properties - remember this is the place to put your UGLY but necessary code!
However, remember "Beautiful is better than ugly."(c)


## Main concept
ConfigurationPolicy should be capt slim. No complex rules. In case you need to generate a helper function for the value validation - sounds like you are doing something wrong.
Try to split it to multiple properties. I believe this will greatly improve bugs hunting time as you won't need to 
simulate the environment to run the code.


### Every value being accessed must be defined in a property
Properties, which can be set must have corresponding attribute with "_" prefix. This way I can know the exposed attributes
and generate a parser.   


## Avoid unnecessary inheritance
You may think it's easier to make a large configuration policy from multiple distinct smaller than handling an
array of them. However, in this case you block further inheritance and code reuse in different environments.
"Flat is better than nested."(c) 
"Sparse is better than dense."(c)



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
