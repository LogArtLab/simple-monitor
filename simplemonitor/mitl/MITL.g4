grammar MITL;

prog	:	formula
	    ;

formula: formula op=(AND|OR|IMPL) formula                  # AndOrImpl
	|	 NOT formula                                       # Not
	|    PARAMETERS                                        # Atom
	|    LPAR formula RPAR                                 # parensFormula
	|    op =(TRUE|FALSE)                                  # trueFalse
	|	 formula U  interval formula                       # U
	|    F  interval formula                               # F
	|	 G  interval formula                               # G
	;

interval : LBRAT NUMBER COMMA NUMBER RBRAT
	;

PARAMETERS:     [a-z]+ ;

LPAR    :       '(';
RPAR    :       ')';
COMMA   :       ',';
LBRAT   :       '[';
RBRAT   :       ']';
U       :	'U';
F       :	'F';
G       :	'G';

TRUE	:	'True';
FALSE	:	'False';

AND	:	'&';
OR	:	'|';
NOT	:	'!';
IMPL : '-->';

NUMBER
	:   ('0'..'9')+ ('.')* ('0'..'9')* EXPONENT?
	|   '.' ('0'..'9')+ EXPONENT?
	|   ('0'..'9')+ EXPONENT
	|   'INF'
	;

fragment
EXPONENT : ('e'|'E') ('+'|'-')? ('0'..'9')+ ;
COMMENT
    :   ('//' ~('\n'|'\r')*)->channel(HIDDEN)
    ;
WS
    :   (' ' | '\t')->channel(HIDDEN)
    ;