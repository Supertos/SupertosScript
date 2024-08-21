import tokenizer
import values

class Block:
    def __init__(self):
        self.header = []
        self.contents = []
        self.parent = None
        self.type = None
        self.readPos = -1

    def readContent(self):
        self.readPos += 1
        if self.readPos >= len(self.contents): return None
        return self.contents[self.readPos]

    def setType(self, type):
        self.type = type

    def setHeader(self, header):
        self.header = header

    def setContents(self, contents):
        self.contents = contents

    def setParent(self, parent):
        self.parent = parent

    def print(self, lv=0):
        out = f"\t"*lv+f"({self.type}):" + str([el.data for el in self.header]) + "\n" + f"\t"*lv
        for token in self.contents:
            if isinstance(token, Block):
                out += "\n" + token.print(lv+1) + "\n"
            else:
                out += " " + token.data
        return out

    def __str__(self):
        return self.print()

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
        self.block.contents += tokens


    def setType(self, type):
        self.block.type = type

    def appendBlock(self, block):
        block.parent = self.block
        self.block.contents.append(block)

    def setHeader(self, header):
        self.block.header = header

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


