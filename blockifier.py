import tokenizer
import values
from codeobj import *
class Block:
    def __init__(self):
        self.header = tokenizer.TokenList()
        self.contents = tokenizer.TokenList()

        self.parent = None
        self.type = None
        self.readPos = -1

        self.objData = [] # List of local symbols
        self.blockData = [] # List of header info
        self.statements = [] # List of internal symbols

    def appendObjData(self, obj):
        if not self.parent or "local" in obj.attr:
            self.objData.append(obj)
        else:
            self.parent.appendObjData(obj)

    def readContent(self):
        self.readPos += 1
        if self.readPos >= len(self.contents.list): return None
        return self.contents.list[self.readPos]

    def searchDefinition(self, symbol):
        for obj in self.objData:
            if obj.symbol == symbol: return obj
        if not self.parent: return None
        return self.parent.searchDefinition(symbol)

    def setType(self, type):
        self.type = type

    def setHeader(self, header):
        self.header.list = header

    def appendContents(self, contents):
        self.contents.appendTokens(contents)

    def setParent(self, parent):
        self.parent = parent

    def print(self, lv=0):
        out = f"\t"*lv+f"({self.type}):" + str([el.data for el in self.header.list]) + "\n" + f"\t"*lv
        for token in self.contents.list:
            if isinstance(token, Block):
                out += "\n" + token.print(lv+1) + "\n"
            else:
                out += " " + token.data
        return out

    def __str__(self):
        return self.print()

    def parseFunctionHeader(self):
        tokens = self.header

        symbol = tokens.readToken()

        tokens.expectSymbol("(")
        out = []
        tkn = tokens.readToken()
        while tkn.data != ")":
            out.append(Variable())
            out[-1].isLocal = True
            out[-1] = tkn.data
            tkn = tokens.readToken()

        obj = Function(symbol.data, out)
        self.blockData = obj
        self.appendObjData(obj)

    def parseForLoopHeader(self):
        tokens = self.header
        counter, id = tokens.expectObjectVariable()

        b = tokens.readToken()
        if b.hasData("="):  # Generic for with counter.
            start = tokens.expectNumber()
            tokens.expectSymbol(",")

            aa = tokens.expectObjectVariable()  # raise Exception if aa != a !!
            operator = tokens.readToken()
            limit = tokens.expectNumber()

            tokens.expectSymbol(",")

            delta = tokens.expectNumber()
            self.blockData = ForLoop(VariableUse(counter, id), start, operator, limit, delta)
        elif b.hasData("in"): # For each, only value
            array = tokens.expectObjectVariable()
            self.blockData = ForEachLoop(counter, None, array)
        elif b.hasData(","): # For each, index, value
            index = tokens.expectObjectVariable()
            tokens.expectSymbol("in")
            array = tokens.expectObjectVariable()
            self.blockData = ForEachLoop(counter, index, array)
        else:
            raise ValueError("Invalid for loop syntax!")

    def parseIfHeader(self):
        self.blockData = If(self.header.expectObjectEquation())
    def parseWhileHeader(self):
        self.blockData = While(self.header.expectObjectEquation())
    def parseHeader(self):
        if self.type == "function" or self.type == "trigger" or self.type == "on_action":
            self.parseFunctionHeader()
        elif self.type == "for":
            self.parseForLoopHeader()
        elif self.type == "object":
            pass # TODO
        elif self.type == "if":
            self.parseIfHeader()
        elif self.type == "while":
            self.parseWhileHeader()


    def parseContents(self):
        tokens = self.contents
        tokens.resetCursor()

        out = []

        while not tokens.finished():
            obj = tokens.readToken()
            while isinstance(obj, tokenizer.Token) and obj.hasData("\n"): obj = tokens.readToken()
            if not obj and tokens.finished(): break

            next = tokens.readToken()
            tokens.returnCursor(2)
            if isinstance(obj, Block):
                tokens.returnCursor(-1)
                obj.parseHeader()
                obj.parseContents()
                out.append(obj)
            elif next is not None and next.hasData("="):
                tokens.returnCursor(-2)
                out.append(tokens.expectObjectEquation())
            elif next is not None and next.hasData("("):
                out.append(tokens.expectObjectFunctionCall())
            else:
                out.append(tokens.expectDeclaration())
                self.appendObjData(Variable(out[-1].attr, [out[-1].scope, out[-1].symbol, out[-1].member], out[-1].value, out[-1].size))

        self.statements = out


    def evaluateContents(self):
        out = ""
        for statement in self.statements:
            out += statement.evaluate(self)

        return out

    def operatorToAction(self, op):
        if op == "+": return "add_to"
        if op == "-": return "subtract_from"
        if op == "*": return "multiply"
        if op == "/": return "divide"
        if op == ">": return "greater_than"
        if op == "<": return "less_than"
        if op == "=": return "equals"

        raise Exception( op )

    def evaluateHeader(self):
        if self.type == "function" or self.type == "trigger":
            return self.blockData.symbol + " = {"
        elif self.type == "on_action":
            return self.blockData.symbol + " = { effect = {"
        elif self.type == "else":
            return "ELSE = {"
        elif self.type == "for":
            if isinstance(self.blockData, ForLoop):
                out = "for_loop_effect = { compare = " + self.operatorToAction(self.blockData.compare.data) + ""
                out += " add = " + self.blockData.delta.data
                out += " start = " + self.blockData.begin.data
                out += " end = " + self.blockData.limit.data
                out += " value = " + self.blockData.var.getAccessName(self)
                out += " break = break"
                out += "\n"
                return out
            elif isinstance(self.blockData, ForEachLoop):
                out = "for_each_loop = { array = " + self.blockData.array
                out += " start = " + self.blockData.value
                if self.blockData.index:
                    out += " add = " + self.blockData.index
                out += " break = break"
                out += "\n"
        elif self.type == "while":
            return "while_loop_effect = { limit = { " + self.blockData.evaluateTrigger(self) + " }"
        elif self.type == "if":
            return "IF = { limit = { " + self.blockData.evaluateTrigger(self) + " }"

    def evaluateFooter(self):
        if self.type == "on_action": return "} }"
        return "}"

    def evaluate(self, block):
        out = self.evaluateHeader()
        out += self.evaluateContents()
        out += self.evaluateFooter()

        return out


class Blockifier:
    def __init__(self):
        self.root = Block()
        self.block = self.root
        self.tokens = None

    def enterBlock(self, block):
        self.block = block

    def quitBlock(self):
        self.block = self.block.parent

    def appendTokens(self, tokens):
        self.block.appendContents(tokens)

    def setType(self, type):
        self.block.type = type

    def appendBlock(self, block):
        block.parent = self.block
        self.block.appendContents([block])

    def setHeader(self, header):
        self.block.setHeader(header)

    def processBlockContents(self):
        while not self.tokens.finished():
            skip, block = self.tokens.skipTil("", values.TKN_BLOCK | values.TKN_BLOCK_END)
            self.appendTokens(skip)
            if block.hasFlag(values.TKN_BLOCK) and block.hasFlag(values.TKN_BLOCK_END):
                self.quitBlock()
                self.processBlock(block)
                return
            elif block.hasFlag(values.TKN_BLOCK):
                self.processBlock(block)
            else:
                self.quitBlock()
                return

    def processBlock(self, start):
        if not start: return
        block = Block()
        self.appendBlock(block)
        self.enterBlock(block)
        self.setType(start.data)

        skip, _ = self.tokens.skipTil(":", 0)
        self.setHeader(skip)

        self.processBlockContents()

    def blockify(self, tokens:tokenizer.TokenList):
        self.tokens = tokens
        tokens.resetCursor()

        while not tokens.finished():
            tkn = tokens.expectBlock()
            self.processBlock(tkn)

        return self.root


