import re
import values
import codeobj

class Token:
    def __init__(self, data=None, flags=0):
        self.data = data
        self.flags = flags

    def setData(self, data):
        self.data = data

    def addFlags(self, flags):
        self.flags = self.flags | flags

    def hasFlag(self, flag):
        return not not (self.flags & flag)

    def hasData(self, data):
        return self.data == data


class TokenList:
    def __init__(self):
        self.list = []
        self.readPos = -1

    def pushToken(self, token):
        self.list.append(token)

    def appendTokens(self, lst):
        self.list += lst

    def lastToken(self):
        return self.list[-1]

    def resetCursor(self):
        self.readPos = -1

    def readToken(self):
        self.readPos += 1
        if self.readPos >= len(self.list): return None
        return self.list[self.readPos]

    def returnCursor(self, amount=1):
        self.readPos -= amount

    def getTokens(self):
        return self.list

    def expectNumber(self):
        tkn = self.readToken()
        if not tkn.hasFlag(values.TKN_NUMBER): return None
        return tkn

    def expectAttributes(self):
        out = []
        tkn = self.readToken()
        while tkn.hasFlag(values.TKN_ATTRIBUTE):
            out.append(tkn.data)
            tkn = self.readToken()
        self.returnCursor()

        return out

    def expectSymbol(self, data):
        tkn = self.readToken()
        if not tkn.hasData(data): return None
        return tkn

    def expectBlock(self):
        tkn = self.readToken()
        if not tkn.hasFlag(values.TKN_BLOCK): return None
        return tkn

    def expectObjectVariable(self):
        a = self.readToken()
        b = self.readToken()

        out = [a.data]
        id = ""
        while b.data == "." or b.data == "^":
            if b.data == "^":
                id = self.expectNumber()
            else:
                a = self.readToken()
                out.append(a.data)
            b = self.readToken()
        self.returnCursor()

        return out, id

    def expectObjectFunctionCall(self):
        name = self.readToken().data # Name
        self.expectSymbol( "(" )
        b = self.readToken()
        out = {}
        numerical_id = -1
        while not b.hasData(")"):
            expectEquals = self.readToken()
            if expectEquals and expectEquals.hasData("="):
                equ = self.expectObjectEquation()
                out[b] = equ.singleElement() or equ
            else:
                self.returnCursor()
                equ = self.expectObjectEquation()
                out[numerical_id] = equ.singleElement() or equ
                numerical_id += 1
            b = self.readToken()

        obj = codeobj.FunctionCall(name, out)
        return obj

    def expectObjectEquation(self):
        equationLv = 1
        a = self.readToken()

        out = []
        while isinstance(a, Token) and not a.data in values.TokensSplit and equationLv > 0:
            if a.hasData( "(" ): equationLv += 1
            if a.hasData( ")" ): equationLv -= 1

            if equationLv == 0: break

            if a.hasFlag( values.TKN_NUMBER ) or a.hasFlag( values.TKN_OPERATOR ) or a.hasFlag( values.TKN_BRACKETS ):
                out.append( a ) # Operators and numbers do not have associated info
            else:
                next = self.readToken()
                self.returnCursor(2)
                if next.hasData("("): # Das ist function!
                    out.append(self.expectObjectFunctionCall())
                else: # Meh, just a variable...
                    out.append(codeobj.VariableUse(*self.expectObjectVariable()))
            a = self.readToken()

        self.returnCursor()

        obj = codeobj.Equation(out)
        return obj

    def expectArrayDeclaration(self):
        self.expectSymbol("{")
        size = self.expectNumber().data
        value = 0
        comma = self.readToken()
        if comma.hasData(","):
            value = self.expectNumber().data
        else:
            self.returnCursor()
        self.expectSymbol("}")

        return size, value

    def expectDeclaration(self):
        attr = self.expectAttributes()
        var, id = self.expectObjectVariable()

        size = ""
        if "array" in attr:
            size, value = self.expectArrayDeclaration()
        else:
            value = self.expectNumber().data

        return codeobj.VariableDeclaration(attr, var, size, value, id)

    def finished(self):
        return self.readPos >= len(self.list) - 1

    def skipTil(self, name, flag):
        skipped = []
        tkn = self.readToken()
        while (flag == 0 or not tkn.hasFlag(flag)) and (name == "" or not tkn.hasData(name)):
            skipped.append( tkn )
            tkn = self.readToken()
        return skipped, tkn

    def __str__(self):
        f = [isinstance(el, Token) and el.data or "---" for el in self.list]
        return "[" + ",".join(f) + "]"


class Tokenizer:
    def __init__(self):
        self.tokens = TokenList()
        self.savedString = ""

    def pushChar(self, char):
        self.savedString += char

    def flush(self):
        if self.savedString == "": return

        tkn = Token(self.savedString)
        if Tokenizer.isNumber(self.savedString): tkn.addFlags(values.TKN_NUMBER)
        if self.savedString in values.TokensKeywords: tkn.addFlags(values.TKN_KEYWORD)
        if self.savedString in values.TokensBlock: tkn.addFlags(values.TKN_BLOCK)
        if self.savedString in values.TokensOperator: tkn.addFlags(values.TKN_OPERATOR)
        if self.savedString in values.TokensAttributes: tkn.addFlags(values.TKN_ATTRIBUTE)
        if self.savedString in values.TokensBrackets: tkn.addFlags(values.TKN_BRACKETS)
        if self.savedString in values.TokensBlockHeaderEnd: tkn.addFlags(values.TKN_HEADER_END)
        if self.savedString in values.TokensBlockEnd: tkn.addFlags(values.TKN_BLOCK_END)
        if self.savedString in values.TokenVariableDefinition: tkn.addFlags(values.TKN_VAR_DECLARATION)

        if tkn.hasFlag(values.TKN_HEADER_END) and not self.tokens.lastToken().hasFlag(
                values.TKN_BLOCK | values.TKN_OPERATOR | values.TKN_NUMBER | values.TKN_ATTRIBUTE | values.TKN_BRACKETS):
            self.tokens.lastToken().addFlags(values.TKN_BLOCK)

        self.tokens.pushToken(tkn)
        self.savedString = ""

    @staticmethod
    def isNumber(string):
        try:
            float(string)
            return True
        except ValueError:
            return False

    def preprocess(self, string):
        return re.sub("#[^\n]*", "", string)

    def tokenize(self, string):
        for char in string:
            if char in values.TokensSplitIgnore:
                self.flush()
            elif char in values.TokensOperator or char in values.TokensBrackets or char in values.TokensBlockHeaderEnd \
                 or char in values.TokensSplit:
                self.flush()
                self.pushChar(char)
                self.flush()
            elif Tokenizer.isNumber(self.savedString) and not Tokenizer.isNumber(char):
                self.flush()
                self.pushChar(char)
            else:
                self.pushChar(char)
        return self.tokens
