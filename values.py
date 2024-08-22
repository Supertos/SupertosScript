
TKN_BLOCK = 1
TKN_KEYWORD = 2
TKN_ATTRIBUTE = 4
TKN_NUMBER = 8
TKN_OPERATOR = 16
TKN_BRACKETS = 64
TKN_HEADER_END = 128
TKN_BLOCK_END = 256
TKN_VAR_DECLARATION = 512

TokensBlock = [
    "function",
    "object",
    "for",
    "trigger",
    "while",
    "on_action",
    "else",
    "if"
]

TokensAttributes = [
    "local",
    "localisation",
    "exact",
    "array",
    "number"
]

TokensSplit = [
    "\n",
    ","
]

TokensKeywords = [
    "array",
    "number"
]

TokenVariableDefinition = [
    "array",
    "number",
    "local",
    "localisation",
    "exact"

]

TokensBlockEnd = [
    "end",
    "else"
]

TokensBlockHeaderEnd = [
    ":"
]

TokensSplitIgnore = [
    " ",
    "\t"
]

TokensOperator = [
    ".",
    ">",
    "<",
    "=",
    "*",
    "/",
    "-",
    "+",
    "^"
]

TokensBrackets = [
    "(",
    ")",
    "{",
    "}"
]