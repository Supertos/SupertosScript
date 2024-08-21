
TKN_BLOCK = 1
TKN_KEYWORD = 2
TKN_ATTRIBUTE = 4
TKN_NUMBER = 8
TKN_OPERATOR = 16
TKN_BRACKETS = 64
TKN_HEADER_END = 128
TKN_BLOCK_END = 256

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
    "exact"
]

TokensKeywords = [
    "array",
    "number"
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
    "\t",
    "\n"
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
    ",",
    "^"
]

TokensBrackets = [
    "(",
    ")",
    "{",
    "}"
]