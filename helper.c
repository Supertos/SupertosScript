
typedef struct block block;
typedef struct token token;
typedef enum token_type token_type;
typedef enum block_type block_type;

typedef struct stack stack;
typedef struct queue queue;

enum token_type {
	none,
	num,
	var,
	op,
	lop,
	lbr,
	rbr,
	nl,
	keyword
};

struct token {
	token_type type;
	char contents[32];
};

struct stack {
	long int offset;
	token contents[];
};

stack* initStack( long int size ) {
	void* obj = calloc( size*sizeof(token) + sizeof(long int), 1 );
	return (stack*)obj;
}

void pushStack( stack* stk, token obj ) { stk->contents[stk->offset++] = obj; }
token popStack( stack* stk ) { stk->offset--; return stk->contents[stk->offset]; }
token* seekStack( stack* stk ) { return &stk->contents[stk->offset - 1]; }


struct queue {
	long int start;
	long int end;
	long int size;
	token contents[];
};

queue* initQueue( long int size ) {
	queue* obj = (queue*)calloc( size*sizeof(token) + sizeof(long int), 1 );
	obj->size = size;
	return obj;
}

void pushQueue( queue* stk, token obj ) { 
	stk->contents[stk->end] = obj; 
	stk->end = (stk->end + 1) % stk->size; 
}

token* peekQueue( queue* stk ) {  
	return &stk->contents[stk->start];
}
token* peekQueueBack( queue* stk ) {  
	return &stk->contents[stk->end];
}


token popQueue( queue* stk ) { 
	token out = stk->contents[stk->start];
	
	stk->start = (stk->start + 1) % stk->size;  
	return out;
}

token popQueueBack( queue* stk ) { 
	stk->end = (stk->end - 1) % stk->size;  
	token out = stk->contents[stk->end];
	
	return out;
}


// void dumpQueue( queue* obj ) {
	// while( obj->start != obj->end ) {
		// token tkn = popQueue( obj );
		// printToken(&tkn);
	// }
// }
