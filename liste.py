
soit Expression comme: Comparison or Operation or Identifier or Constant or Call or Path #Expression = une valeur

soit Statement comme: (Module or Declaration or Call or Assignement or Branch or While or For or Return) #Statement = une action

#Nb: une classe dérivée de NObject aura les propriétés de NObject + les siennes sauf si une propriété est overridée

NObject:
    #classe de base, jamais fournie directement, mais tous les constructeurs se basent dessus
    parent : NObject #pas fourni dans le json car obvious, mais tu peux quand même le définir dans tes classes, c'est pratique pour la stacktrace
    start : int #emplacement de l'objet en nombre de caractères depuis le début du fichier -> utile pour les erreurs

### MODULES ###

Module < NObject:
    #ne peut contenir que des autres modules (Module, Class, Fun)
    identifier : Identifier #l'id du module
    children : list of Module #les instructions dans le corps du module, par ordre d'apparition

Fun < Module:
    #peut aussi contenir des instructions ( Declaration, Assignement, Call, Branch, While, For, Return )
    return_type : Identifier or Path
    parameters : list of Assignement or Declaration #en principe, des assignements/déclarations n'ayant que des constantes comme termes
    children : list of Statement

Class < Module:
    #TODO

### STATEMENTS ###

While < NObject:
    do_while : bool #est-ce que la boucle est une boucle do_while ? 
    loop_condition :  Expression #Expression = une valeur. Si cette valeur n'est pas booléenne, elle vaut True si et seulement si elle est différente de null. 
    #testée à chaque itération (au début ou à la fin en fonction de do_while), pour savoir si on exécute encore une fois children
    children : list of Statement #même chose que dans le children de Fun 

For < NObject:
    start : Assignement # première chose exécutée, 1 seule fois #ex: int i = 0
    condition : Expression # Même principe que pour un while normal : on boucle tant que c'est vrai
    step : Expression #Valeur incrémentée à chaque itération à la variable de [start]
    children : list of Statement

Declaration < NObject:
    type : Identifier or Path
    id : Identifier #nom de la variable déclarée

Assignement < NObject:
    type : Identifier or Path #si non null, alors on peut considérer l'assignement comme Declaration suivi Assignement. Sinon, c'est juste Assignement.
    value : Expression #valeur assignée à la variable
    id : Identifier or Path #si type est non null, id DOIT être un Identifier. Sinon, ça peut aussi être un Path

Call < NObject:
    id : Identifier or Path
    arguments : list of Expression

Return < NObject:
    return_value : Expression #... la valeur de retour

Branch < NObject:
    if_condition : Expression #même principe que la condition du while pour les valeurs de vérité. Exécute if_body si vrai, else_body sinon.
    if_body : list of Statement
    else_body : list of Statement  #peut être null s'il n'y a pas de else

### EXPRESSIONS ###

Path < NObject:
    #exemple : Parent.Name
    right_term : Identifier
    left_term : Identifier or Path

Comparison < NObject:
    left_term : Expression 
    operator : string #l'opérateur, exemple "or"
    right_term : Expression #peut être null si et seulement si operator vaut "not"

Operation < Comparison:
    #exactement comme Comparison, c'est juste pour pouvoir rendre le code lisible en python

### CONSTANTS ###

Constant < NObject:
    #Valeur écrite telle quelle dans le code, comme un string ou un chiffre
    type: string #le type de la valeur (exemple : "bool")
    value: string or float or int or bool or ... #valeur (exemple : "true") #les yep et nope sont convertis en true false

Identifier < NObject:
    # un nom commençant par [a-zA-Z_] et pouvant ensuite contenir des chiffres
    id: string 



