
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>

typedef struct token_list token_list;
typedef struct arg_list arg_list;
typedef struct dom_list dom_list;
typedef struct symbol symbol;
typedef struct scope scope;
typedef struct for_loop for_loop;
typedef struct for_each_loop for_each_loop;
typedef struct func_call func_call;
typedef struct assignation assignation;
typedef struct code_scope code_scope;
typedef struct condition condition;
typedef struct while_loop while_loop;
typedef enum assign_type assign_type;
typedef enum element_type element_type;
typedef union dom_element dom_element;

enum element_type {
	element_invalid,
	element_symbol,
	element_scope,
	element_for_loop,
	element_for_each_loop,
	element_func_call,
	element_assignation,
	element_condition,
	element_while_loop
};

enum assign_type {
	assign_set,
	assign_mul,
	assign_add,
	assign_sub,
	assign_div
};

struct token_list {
	token obj;
	
	dom_list* next;
};

struct arg_list {
	char name[32];
	
	arg_list* next;
};

struct code_scope {
	
};

struct dom_list {
	code_scope* info;
	
	element_type type;
	dom_element* obj;
	
	dom_list* next;
};

struct symbol {
	char name[32];
	unsigned int arg_count;
	unsigned int arg_len;
	char* arg_list;
	
	dom_list* body;
};

struct scope {
	char name[32];
	
	dom_list* body;
};

struct for_loop {
	char varname[32];
	int start;
	int end;
	int add;
	char comparison[2];
	
	dom_list* body;
};

struct for_each_loop {
	char key[32];
	char val[32];
	char array[32];
	
	bool is_scoped;
	
	dom_list* body;
};

struct func_call {
	char name[32];
	bool complex_func;
	bool internal_func;
	
	arg_list* args;
};

struct assignation {
	char varname[32];
	assign_type type;
	
	token_list* data;
};

struct condition {
	token_list cond;
	
	dom_list* body;
};

struct while_loop {
	token_list cond;
	
	dom_list* body;
};

union dom_element {
	symbol a;
	scope b;
	for_loop c;
	for_each_loop d;
	func_call e;
	assignation f;
	condition g;
	while_loop h;
};

dom_list* dom_push_child( dom_list* dom, element_type type, void* child );
dom_list* dom_next_sibling( dom_list* dom );
dom_list* dom_child( dom_list* dom );
dom_list* dom_last_sibling( dom_list* dom );
dom_list* dom_push_sibling( dom_list* dom, element_type type, void* child );

token_list* tokens_last_element( token_list* dom );
token_list* tokens_push( token_list* dom, token* el );






