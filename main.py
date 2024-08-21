import re

TKN_SCOPE = 1
TKN_ARGNAME = 2
TKN_KEYWORD = 4

TokensKeywords = [
    "function",
    "for",
    "if",
    "else",
    "end",
    "while",
    "scope",
    "object",
]
TokensKeywordsNonBlock = [
    "array",
    "local",
    "value",
    "localisation"
]
TokensSplits = [
    " "
]
TokensSplitsSave = [
    ".",
    ":",
    ">",
    "<",
    "=",
    "*",
    "/",
    "-",
    "+",
    "(",
    ")",
    ",",
    "}",
    "{",
    "\n"
]



class Token:
    def __init__(self, name, flags):
        self.name = name
        self.flags = flags


class Tokenizer:
    def __init__(self):
        self.tokens = []
        self.savedString = ""
        self.pos = 0

    def readToken(self):
        if self.pos == len(self.tokens): return None
        out = self.tokens[self.pos]
        self.pos += 1
        return out

    def skipTilToken(self, nameFilter, flagFilter):
        out = []
        tkn = self.readToken()
        while ( flagFilter == 0 or (tkn.flags & flagFilter) == 0 ) and ( nameFilter == "" or tkn.name != nameFilter ):
            out.append( tkn )
            tkn = self.readToken()
        return out, tkn

    def isNumber(self, string):
        try:
            float(string)
            return True
        except Exception:
            return False
    def appendToken(self):
        if self.savedString != "":
            if self.savedString in TokensKeywords:
                self.tokens.append( Token(self.savedString, TKN_KEYWORD ) )
            else:
                self.tokens.append( Token(self.savedString, 0 ) )
            self.savedString = ""

    def appendChar(self, char):
        self.savedString += char
    def tokenize(self, string):
        string = re.sub("#[^\n]*", "", string).replace("\t", "")

        for char in string:
            if char in TokensSplitsSave:
                self.appendToken()
                self.appendChar(char)
                self.appendToken()
            elif char in TokensSplits:
                self.appendToken()
            elif self.isNumber(self.savedString) != self.isNumber(char):
                self.appendToken()
                if char in TokensSplitsSave:
                    self.appendChar(char)
                    self.appendToken()
                elif char not in TokensSplits:
                    self.appendChar(char)

            else:
                self.appendChar(char)

        return self.tokens

class Block:
    def __init__(self):
        self.contents = []
        self.header = []
        self.parent = None
        self.type = None

class Blocker:
    def __init__(self):
        self.tree = Block()
        self.element = self.tree

    def pushBlock(self):
        if self.element:
            self.element.contents.append( Block() )
            self.element.contents[-1].parent = self.element
            self.element = self.element.contents[-1]

    def moveUp(self):
        if self.element:
            self.element = self.element.parent

    def setBlockHeader(self, header):
        self.element.header = header

    def setBlockType(self, header):
        self.element.type = header

    def pushBlockContents(self, contents):
        self.element.contents += contents

    def blockify(self, tokenizer, firsttkn=None):
        tkn = firsttkn or tokenizer.readToken()
        while tkn:
            while tkn.name == "\n":
                tkn = tokenizer.readToken()
            if tkn.flags & TKN_KEYWORD == 0:
                raise Exception(f"Token \"{tkn.name}\" outside block detected! Aborting...")
            elif tkn.name == "end":
                raise Exception("\"end\" token outside block detected! Aborting...")
            else:
                self.pushBlock()
                skip, tkn = tokenizer.skipTilToken(":", 0)
                self.setBlockHeader(skip)
                self.setBlockType(tkn)
                skip, tkn = tokenizer.skipTilToken("", TKN_KEYWORD)
                self.pushBlockContents(skip)
                if tkn.name == "end":
                    self.moveUp()
                    return
                else:
                    self.blockify(tokenizer, tkn)
                    while tkn.name != "end":
                        skip, tkn = tokenizer.skipTilToken("", TKN_KEYWORD)
                        self.pushBlockContents(skip)
                        if tkn.name == "end":
                            self.moveUp()
                            return
                        else:
                            self.blockify(tokenizer, tkn)
            tkn = tokenizer.readToken()


class Statement:
    def __init__(self):
        statement_type = 0

class StatementAssign(Statement):
    pass
class StatementDeclare(Statement):
    pass

class Statemizer:
    def __init__(self):
        self.blockStack = None
        self.blocker = None

    def setBlocker(self, blocker):
        self.blocker = blocker
        self.blockStack = [(self.blocker.tree,0)]

    def readToken(self):
        elements, pos = self.blockStack[-1]
        if pos == len(elements.contents): return None
        self.blockStack[-1] = (elements, pos + 1)
        return elements.contents[pos]

    def pushLayer(self, block):
        self.blockStack.append((block, 0))

    def quitLayer(self):
        self.blockStack = self.blockStack[:len(self.blockStack) - 2]

    def expectNumber(self, start):
        try:
            return int(self.readToken().name)
        except Exception:
            raise Exception(f"Numeric value expected near {start.name}!")
    def expectArrayDeclaration(self, start):
        tkn = self.readToken()
        if tkn.name != "{": raise Exception(f"Array Declaration expected near \"{start.name}\"!")
        len = int(self.readToken().name)
        tkn = self.readToken()
        val = 0
        if tkn.name == ",":
            val = self.expectNumber( tkn )
            tkn = self.readToken()
        if tkn.name != "}": raise Exception(f"Array Declaration expected near \"{start.name}\", got \"{tkn.name}\"!")
        return len, val

    def readDeclaration(self, start):
        tkn = start
        out = StatementDeclare()

        if tkn.name == "array" or tkn.name == "number":
            out.type = tkn.name
        elif tkn.name == "local":
            out.isLocal = True
            tkn = self.readToken()
            out.name = tkn.name

        tkn = self.readToken()
        out.symbol = tkn.name
        if out.type == "array":
            out.arrayLen, out.value = self.expectArrayDeclaration(tkn)
        else:
            out.value = self.expectNumber(tkn)
        return out, tkn


    def statemizeElement(self):
        tkn = self.readToken()
        out = []
        while tkn:
            if isinstance(tkn, Block):
                self.pushLayer(tkn)
                self.statemizeElement()
            else:
                if tkn.name == "\n":
                    pass
                elif tkn.name == "number" or tkn.name == "array" or tkn.name == "local":
                    statement, tkn = self.readDeclaration(tkn)
                    out.append(statement)
                    print( statement.type, statement.value, statement.arrayLen, statement.symbol)
                else:
                    raise Exception(f"Unknown wtf {tkn.name}")

            tkn = self.readToken()

        self.quitLayer()
        return out


    def statemize(self, blocker):
        self.setBlocker( blocker )
        self.statemizeElement()





t = Tokenizer()
b = Blocker()
s = Statemizer()
with open("input.txt") as f:
    t.tokenize(f.read())
    b.blockify(t)
    s.statemize(b)
