
#include <symbols.c>


dom_list* dom_next_sibling( dom_list* dom  ) {
	return dom->next;
}

dom_list* dom_child( dom_list* dom ) {
	return dom->obj->body;
}

dom_list* dom_last_sibling( dom_list* dom ) {
	dom_list* cur = dom;
	while( dom_next_sibling(cur) ) cur = dom_next_sibling(cur);
	
	return cur;
}

dom_list* dom_push_child( dom_list* dom, element_type type, void* child ) {
	dom->obj->body = calloc( 1, sizeof( dom_list ) );
	
	dom->obj->body->type = type;
	dom->obj->body->obj = child;	

	return dom->obj->body;
}

dom_list* dom_push_sibling( dom_list* dom, element_type type, void* child ) {
	dom_list* el = calloc( 1, sizeof( dom_list ) );
	
	dom_last_sibling( dom )->next = el;
	
	el->type = type;
	el->obj = child;	

	return el;
}

arg_list* args_last_element( arg_list* dom ) {
	dom_list* cur = dom;
	while( cur->next ) cur = cur->next;
	
	return cur;
}

token_list* tokens_last_element( token_list* dom ) {
	dom_list* cur = dom;
	while( cur->next ) cur = cur->next;
	
	return cur;
}

token_list* tokens_push( token_list* dom, token* nel ) {
	token_list* el = calloc( 1, sizeof( token_list ) );
	
	tokens_last_element( dom )->next = el;
	
	el->obj = nel;
	
	return el;
}

arg_list* args_push( arg_list* dom, char nel[32] ) {
	token_list* el = calloc( 1, sizeof( token_list ) );
	
	args_last_element( dom )->next = el;
	
	el->name = nel;
	
	return el;
}