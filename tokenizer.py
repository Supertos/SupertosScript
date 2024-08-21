import re
import values


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

    def lastToken(self):
        return self.list[-1]

    def resetCursor(self):
        self.readPos = -1

    def readToken(self):
        self.readPos += 1
        if self.readPos >= len(self.list): return None
        return self.list[self.readPos]

    def returnCursor(self):
        self.readPos -= 1

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
            out.append(tkn)
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
        return "[" + ",".join([f"({el.flags}) "+el.data for el in self.list]) + "]"


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
            elif char in values.TokensOperator or char in values.TokensBrackets or char in values.TokensBlockHeaderEnd:
                self.flush()
                self.pushChar(char)
                self.flush()
            elif Tokenizer.isNumber(self.savedString) and not Tokenizer.isNumber(char):
                self.flush()
                self.pushChar(char)
            else:
                self.pushChar(char)
        return self.tokens






