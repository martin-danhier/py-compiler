# py-compiler
compiler in python

## How the compiler works
TODO (dear compiler maintener)

## How the VM works
The app is divided into multiple NoKeObject. Each NoKedObject is characterised by a name, by a type and by multiple children that are, in fact, NoKedObject too. When you run your project, it begins at the main NoKeObject, your main function. At this point, the NoO (pfff, i'm tired ^^) will launch each of its children. And each of its children will be executed according to their type.
## Example
```
fun hello(){
    var michel : number;
    michel = 3;
    var jean : number;
    jean = 42;
    michel = michel * jean;
    mouais(michel, jean);
}
```
This NoO will have as characteristics :
type : fun
name : hello
content : *all text between {}*

children1 :
* type : init
* name : michel
* content : int
* *no child*

children2 :
* type : assign
* name : michel
* content : 3
* *no child*

children3 :
* type : init
* name : jean
* content : 42
* *no child*

children4 :
* type : assign
* name : jean
* content : 42
* *no child*

children5
* type : assign
* name : michel
* content : michel * jean

children6
* type : call
* name : mouais
* content : *list*([michel, jean])

So when you launch the NoO 'hello', all its children will be run by order of apparition. As simple as this.

## Event
### Variables
Major event in the history of programming, the creation of a new variable.
In fact, the process of our vm to register a new var is pretty simple. When a NoO need to create a var, it calls the module **TODO** that will register the name, the type and the id of the scope (the id of the parent NoO in fact).
Getting a variable is almost as simple as this. Provide me your current scope's id (current running NoO), the name of your var, its type and I will check if I can find a var that matchs with your settings.
