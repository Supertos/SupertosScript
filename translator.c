/* -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
	*Supertos Industries
	Author: Supertos, 2024
	Version: 1.0
	SupertosScript (SS) to PDXScript (Bullshit)
*/
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>
#include "helper.c"
#include "symbols.h"

bool is_keyword( char* c ) {
	return !strcmp( c, "for" ) || !strcmp( c, "on_action" ) || !strcmp( c, "struct" ) || !strcmp( c, "function" ) || !strcmp( c, "if" ) || !strcmp( c, "else" ) || !strcmp( c, "while" ) || !strcmp( c, "for_each" ) || !strcmp( c, "end" ) || !strcmp( c, "then" ) || !strcmp( c, "do" );
}
bool is_space( char c ) { return c == ' '; }
bool is_newline( char c ) { return c == '\n'; }
bool is_number( char c ) { return c == '.' || (c >= '0' && c <= '9'); }
bool is_variable( char c ) { return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z'); }
bool is_operator( char c ) { return c == '-' || c == '<' || c == '>' || c == '+' || c == '*' || c == '/' || c == '^' || c == '=' || c == ':'; }
bool is_one_char_token( char c ) { return c == '-' || c == '+' || c == '*' || c == '/' || c == '^' || c == '(' || c == ')' || c == '='; }
bool is_rbracket( char c ) { return c == ')'; }
bool is_lbracket( char c ) { return c == '('; }


char readChar( FILE* from ) {
	char c = getc( from );
	while (is_space(c))
		c = getc( from );
	return c;
}

// void printToken( token* tkn ) { printf("Token(Type=%d, Contents=%s)\n", tkn->type, tkn->contents); }
void printToken( token* tkn ) { 
	
	switch( tkn->type ) {
		case op:
			printf("\033[0;37m");
			break;
		case lbr:
		case rbr:
			printf("\033[0;34m");
			break;
		case num:
			printf("\033[0;36m");
			break;
		case keyword:
			printf("\033[0;32m");
			break;
		case var:
			printf("\033[0;35m");
			break;
		
	}
	printf("%s", tkn->contents); 
	printf("\033[0;37m");
	printf("|");
	
	
}

token readToken( FILE* from ) {
	token newToken = {.type = none, .contents= ' '};
	char str[32];
	
	char c = readChar( from );
	
	if( is_newline( c ) ) {
		newToken.type = nl;
		newToken.contents[0] = c;
		return newToken;
	}
	
	if( c == EOF ) {
		return newToken;
	}
	if( is_operator( c ) ) {
		newToken.type = op;
		ungetc(c, from);
		fscanf( from, "%[><=+-/*^:]", newToken.contents );
		return newToken;
	}else if( is_lbracket( c ) ) {
		newToken.type = lbr;
		newToken.contents[0] = c;
		return newToken;
	}else if( is_rbracket( c ) ) {
		newToken.type = rbr;
		newToken.contents[0] = c;
		return newToken;
	}
	ungetc(c, from);
	
	if( is_number( c ) ) {
		newToken.type = num;
		fscanf( from, "%[.0-9]", newToken.contents );
	}else if( is_variable( c ) ) {
		newToken.type = var;
		fscanf( from, "%[a-zA-Z_]", newToken.contents );
		
		if( is_keyword( newToken.contents ) ) {
			newToken.type = keyword;
		}
	}else{
		c = readChar( from );
		return readToken( from );
	}
	
	return newToken;
}

void generate_constructions( queue* que ) {
	
}

int main() {
	FILE* f = fopen("input.txt", "r");
	
	queue* que = initQueue(32768);
	
	token a = readToken( f );
	while( a.type != none ) {
		printToken( &a ); 
		a = readToken( f ); 
		
	}
	
	generate_constructions( que );
	
	fclose( f );
	return 0;
}