grammar BoundScript

entry SystemNode:
    'system' name=ID '{'
        director=DirectorNode
    '}'
;

DirectorNode:
    'director' name=ID '{'
        start=StartHandlerNode
    '}'
;

StartHandlerNode:
    'on' 'start' '{'
        statements+=PrintStatementNode*
    '}'
;

PrintStatementNode:
    'print' '(' value=STRING ')'
;

terminal ID: /[A-Za-z_][A-Za-z0-9_]*/;
terminal STRING: /"([^"\\\r\n]|\\.)*"/;
hidden terminal WS: /\s+/;
