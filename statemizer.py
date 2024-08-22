import blockifier
import codeobj
import tokenizer

class HeaderFunction:
    def __init__(self, type, name, argumentList):
        self.symbol = name
        self.type = type
        self.argumentList = argumentList


class Statemizer:
    def __init__(self):
        self.block = None
        self.objData = []

    def addGlobalDeclaration(self, decl):
        self.objData.append(decl)

    def enterBlock(self, block):
        self.block = block

    def quitBlock(self):
        self.block = self.block.parent
    def statemizeBlockHeader(self):
        if self.block.type == "function" or self.block.type == "trigger" or self.block.type == "on_action":
            symbol = self.block.header.readToken()

            self.block.header.expectSymbol("(")
            out = []
            tkn = self.block.header.readToken()
            while tkn.data != ")":
                out.append( codeobj.Variable() )
                out[-1].isLocal = True
                out[-1] = tkn.data
                tkn = self.block.header.readToken()

            obj = codeobj.Function(symbol, out)

            self.addGlobalDeclaration(obj)
        elif self.block.type == "if":
            pass # TODO

    def statemizeBlockContents(self):
        tokens = self.block.contents
        tokens.resetCursor()
        out = []
        obj = tokens.readToken()
        self.block.localVariableCount = 0
        while not tokens.finished():
            while isinstance(obj, tokenizer.Token) and obj.hasData("\n"): obj = tokens.readToken()

            next = tokens.readToken()

            tokens.returnCursor(2)
            if isinstance(obj, blockifier.Block):
                block = tokens.readToken()
                self.statemizeBlock(block)
                self.block.localVariableCount += block.localVariableCount
            elif next.hasData("="):
                out.append( tokens.expectObjectEquation() )
            elif next.hasData("("):
                out.append( tokens.expectObjectFunctionCall() )
            else:
                out.append( tokens.expectDeclaration() )
                if "local" in out[-1].attr: self.block.localVariableCount += 1

            obj = tokens.readToken()
        self.block.contents = tokenizer.TokenList()
        self.block.contents.list = out

    def statemizeBlock(self, block):
        self.enterBlock( block )
        self.statemizeBlockHeader()
        self.statemizeBlockContents()
        self.quitBlock()

    def statemize(self, root):
        self.enterBlock( root )
        for el in root.contents.list:
            self.statemizeBlock(el)