grammar BoundScript

entry SystemNode:
    'system' name=ID '{'
        boxes+=BoxNode*
        director=DirectorNode
    '}'
;

BoxNode:
    'box' name=ID '{'
        'operation' operation=ID '(' input=ID ':' 'string' ')' ':' 'string'
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
    'let' name=ID '=' box=ID '.' operation=ID '(' argument=STRING ')'
;

terminal ID: /[A-Za-z_][A-Za-z0-9_]*/;
terminal STRING: /"([^"\\\r\n]|\\.)*"/;
hidden terminal WS: /\s+/;
