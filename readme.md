# Supertos Script language
This readme.md covers Supertos Script (SS in the following text) concepts and syntax.
Supertos Script is still under development and as for now lacks even basic functionality.
## Variables
Variables in SS may only contain number. **As PDXScript limits variable range to ~2M and allows precision up to 3 digits it is also the case with SS**. Variables do not have to be declared, instead it is assumed that any undeclared variable has value of 0 by default. These are common actions with the variables in SS:

 - Set variable value
	> a = b 
- Add value to variable
	> a += b
- Substract value from variable
	> a -= b
- Multiple variable by value:
	> a *= b
- Divide variable by value:
	> a /= b

**As PDXScript does not allow raising to the power, is is also the case with SS.**

## Arrays
Arrays are continous sequence of numbers. Every array element may be accessed by it's id.
To mark specific variable as array:
> array array_name array_size

To access array element use:
> array_name^element_id

## Functions
Functions are the piece of code that can be referenced from the other place in your code. **As PDXScript categorizes functions as second-class citizens, that's also the case with SS**. **As Clausewitz engine requires functions to be declared in separate file, an output reflecting this will be produced**. Functions declared as follows:
> function function_name( argument_a, argument_b, argument_c )
>  \# Function body
> end

**It is important to note that since PDXScript uses questionable variable scoping at best, it is important to mention that argument names and external variables shall not share common name.**

Function may return numeric value at the end of their execution using "return" keyword (**Since PDXScript has no way of returning values from functions, execution of the function will not be terminated prematurely on return keyword encounter.**

>function func()
>return 1
>end

**Since PDXScript has no way of returning value from function, variable called "__return" is used. It is recommended to not use this name for variables.**

## On Actions
Special type of function called On Action is the piece of code that runs once engine issues event. **Since PDXScript does not support custom events, special naming to these functions shall be applied.** Refer to Paradox wiki for info. Example:
> on_action on_startup() \# on_actions has no arguments
>
>end

## Scoping
Special feature of PDXScript is scoping: almost every function (effect in PDXScript) requires at least some scoping. Scoping means that certain function (effect) is applied to the scope it used in. To have scoping, function (effect) shall be placed inside scope block. Scope blocks declared as follows:
>every_owned_state: \# Or any other scope name such as SOV or GER
>  \# Block contents
> end

To refer to the current scope, use THIS. To refer to the previous scope, use PREV, to refer to the special scope that is **hardcoded** in PDXScript, use FROM. To use the first scope, from which current code is called, use ROOT.

**It is important to remember that scope is a number too: every specific scope has it's id.**

Every variable belongs to certain scope. If scope is undeclared, "global" scope is used. **PDXScript applies variable to the current scope if none specified, SS overrides this feature in order to save programmer's mental health and to ensure coherent and predictable behaivour.**
To declare variable scope use:
> SCOPE:variable

## Structures
In order to structure data, and save programmer a headache, collection of variables may be referred as if they contained in some artificial scope. However, such structures shall be properly declared:
>struct structure_name:
> [element_1_name]
> [element_2_name]
> [element_3_name]
> end

To access structure member use:
>SCOPE:struct_name.struct_member

**PDXScript does not has structures as feature. SS emulates this by accessing variable named "__[struct_name]__[struct_member]". Avoid name collisions!**

## Conditions
Condition is the block of code that runs only and only if specified conditions met:
>if [condition] then
>
>else
>
>end

Conditions consist out of special hardcoded functions (called triggers in Clausewitz) and and/or/not keywords.

## Loops
Loops are pieces of code that run multiple times. (**PDXScript by default limits loops to running no more than 1000 times.**) For loop (Loop that has counter, that travels from one value to another) declared as follows:
>for [counter_name] = [initial_value] [counter_name] [</<=/>=/>/==] [compare_value] [counter_change] do
>
>end

While loop:
>while [condition] do
>
>end

For each loop (Goes through every element in the given array):
>for_each [id_variable_name] [array_element_variable_name] [array_name] do
>
>end

Loops may be quit prematurely. Use keyword break to do so.
**Since PDXScript uses break as variable (while allowing to change it's name) to determine if it should quit loop it is strongly recommended to not use variable called break**
