grammar BoundScript

entry SystemNode:
    'system' name=ID '{'
        types+=RecordTypeNode*
        boxes+=BoxNode*
        director=DirectorNode
    '}'
;

RecordTypeNode:
    'type' name=ID '{' fields+=FieldNode* '}'
;

FieldNode:
    name=ID ':' type=TypeName
;

TypeName returns string:
    'string' | 'number' | 'boolean' | 'void' | ID
;

BoxNode:
    'box' name=ID '{'
        'operation' operation=ID '(' input=ID ':' inputType=TypeName ')' ':' resultType=TypeName
    '}'
;

DirectorNode:
    'director' name=ID '{'
        start=StartHandlerNode
    '}'
;

StartHandlerNode:
    'on' 'start' '{'
        statements+=StatementNode*
    '}'
;

StatementNode:
    PrintStatementNode | InvocationStatementNode
;

PrintStatementNode:
    'print' '(' (value=STRING | variable=ID) ')'
;

InvocationStatementNode:
    ('let' name=ID '=')? box=ID '.' operation=ID '(' (argument=STRING | variable=ID) ')'
;

terminal ID: /[A-Za-z_][A-Za-z0-9_]*/;
terminal STRING: /"([^"\\\r\n]|\\.)*"/;
hidden terminal WS: /\s+/;
