
from values import TKN_NUMBER

internalIdCount = 0
class CodeObjectUse:
    def __init__(self, symbol, declaration=None):
        self.declaration = declaration
        self.symbol = symbol
        self.internal = not self.declaration

    def getObject(self):
        return self.declaration

    def setDeclaration(self, declaration):
        self.declaration = declaration
        self.internal = not self.declaration
class VariableUse(CodeObjectUse):
    def __init__(self, parts, id):
        super().__init__(".".join(parts), None)

        self.scope = len(parts) > 1 and parts[0] or ""
        self.name = len(parts) > 1 and parts[1] or parts[0]
        self.member = len(parts) > 2 and parts[2] or ""
        self.id = id

    def getAccessName(self, block):
        data = block.searchDefinition(self.symbol)
        if data: return data.getAccessName()

        return self.symbol

class VariableDeclaration(VariableUse):
    def __init__(self, attr, parts, size, value, id ):
        super().__init__(parts, id)
        self.value = value
        self.size = size
        self.attr = attr

    def evaluate(self, block):
        var = block.searchDefinition(self.symbol)
        if var.isArray:
            return "resize_array = { " + "size = " + self.size + "array = " + var.getAccessName() + "value = " + self.value + " }"
        return var.generateAction("set", self.value)


class FunctionCall(CodeObjectUse):
    def __init__(self, symbol, arguments=None):
        super().__init__(symbol, None)
        if arguments is None: arguments = {}
        self.argumentList = arguments
        self.localArgumentArray = [] # When evaluating arguments, additional local variables may be used

    def reserveLocalVariable(self, id):
        if id > len(self.localArgumentArray): return
        self.localArgumentArray.append(Variable())
        self.localArgumentArray[-1].isLocal = True

    def getAccessName(self):  # Returns PDXScript name by which this data can be accessed
        return self.declaration.getAccessName()

    def evaluate(self, values):  # Returns PDXScript code required to run in order to access this data
        out = ""
        id = 0

        arguments = []
        for value in values:
            if isinstance(value, Equation) or isinstance(value, FunctionCall):
                out += value.evaluate(value.argumentList) + "\n"
                self.reserveLocalVariable(id)
                out += self.localArgumentArray[id].generateAction("set", value.getAccessName()) + "\n"
                arguments.append(self.localArgumentArray[id].getAccessName())
                id += 1
            else:
                arguments.append(isinstance(value, str) and value or value.getAccessName())

        out += not self.internal and self.declaration.evaluate(arguments)
        return out

    def pushArgument(self, name, value):
        self.argumentList[name] = value
class Equation:
    def __init__(self, contents=None):
        global internalIdCount
        self.internalId = internalIdCount
        internalIdCount += 1
        if contents is None: contents = []
        from tokenizer import TokenList
        self.contents = TokenList()
        self.contents.list = contents

    def pushData(self, data):
        self.contents.list.append(data)

    def singleElement(self):
        if len(self.contents.list) == 1:
            return self.contents.list[0]
        else:
            return None

    def operatorPriority(self, op):
        if op == "+" or op == "-": return 1
        if op == "*" or op == "/": return 2
        if op == "not" or op == "/": return 3
        if op == "and" or op == "/": return 2
        if op == "or" or op == "/": return 1
        raise Exception( "!", op, "!" )

    def evaluateDijkstra(self):
        # Dijkstra Sorting Station Algorithm
        out = []
        stack = []
        while not self.contents.finished():
            tkn = self.contents.readToken()
            from tokenizer import Token
            if isinstance(tkn, Token) and tkn.hasData("\n"):
                pass
            elif isinstance(tkn, Token) and tkn.hasFlag( TKN_NUMBER ):
                out.append( tkn )
            elif isinstance(tkn, FunctionCall) or isinstance(tkn, VariableUse):
                out.append( tkn )
            elif isinstance(tkn, Token) and tkn.hasData( "(" ):
                stack.append( tkn )
            elif isinstance(tkn, Token) and tkn.hasData( ")" ):
                while not stack[-1].hasData("("):
                    out.append( stack.pop() )
                stack.pop()
            else:
                while len(stack) > 0 and stack[-1].data != "(" and self.operatorPriority(stack[-1].data) >= self.operatorPriority(tkn.data):
                    out.append( stack.pop() )
                stack.append( tkn )
        while len(stack) > 0:
            el = stack.pop()
            out.append( el )
        out.reverse()
        return out

    def operatorToAction(self, op):
        if op == "+": return "add_to"
        if op == "-": return "subtract_from"
        if op == "*": return "multiply"
        if op == "/": return "divide"
        if op == ">": return "greater_than"
        if op == ">": return "less_than"
        if op == "=": return "equals"
    def getAccessName(self):
        return "global.equ_"+str(self.internalId)
    def generateAction(self, action, value, id=0):
        name = self.getAccessName()
        out = action + "_temp_variable = {" + name
        return out + "=" + value + "}"

    def evaluateTrigger(self, block): # No calculation in here, sry. Чел это тумач
        stack = self.evaluateDijkstra()
        temp_stack = []
        out = "set_temp_variable = {" + self.getAccessName() + " = "
        from tokenizer import Token
        if isinstance(stack[-1], Token): out += stack[-1].data + "}\n"
        if isinstance(stack[-1], VariableUse): out += stack[-1].getAccessName() + "}\n"
        if isinstance(stack[-1], FunctionCall):
            out = stack[-1].evaluate() + out
            out += stack[-1].getAccessName(block) + "}\n"

        stack.pop()
        temp_stack.append(self.getAccessName())

        while len(stack) > 0:
            if isinstance(stack[-1], VariableUse) or isinstance(stack[-1], FunctionCall) or isinstance(stack[-1],
                                                                                                       Token) and stack[
                -1].hasFlag(TKN_NUMBER):
                temp_stack.append(stack.pop())
            else:  # Operator
                if not isinstance(temp_stack[-2], str): raise Exception(
                    "Too complex math! (TODO: Can this even happen?)")
                if isinstance(temp_stack[-1], VariableUse):
                    out += self.generateAction(self.operatorToAction(stack[-1].data),
                                               temp_stack[-1].getAccessName(block)) + "\n"
                elif isinstance(temp_stack[-1], FunctionCall):
                    out += temp_stack[-1].evaluate() + "\n"
                    out += self.generateAction(self.operatorToAction(stack[-1].data),
                                               temp_stack[-1].getAccessName(block)) + "\n"
                elif isinstance(temp_stack[-1], Token):
                    out += self.generateAction(self.operatorToAction(stack[-1].data), temp_stack[-1].data) + "\n"

                temp_stack.pop()
                stack.pop()

        return out




    def evaluate(self, block):
        stack = self.evaluateDijkstra()
        temp_stack = []
        out = "set_temp_variable = {" + self.getAccessName() + " = "
        from tokenizer import Token
        if isinstance(stack[-1], Token): out += stack[-1].data + "}\n"
        if isinstance(stack[-1], VariableUse): out += stack[-1].getAccessName() + "}\n"
        if isinstance(stack[-1], FunctionCall):
            out = stack[-1].evaluate() + out
            out += stack[-1].getAccessName(block) + "}\n"

        stack.pop()
        temp_stack.append(self.getAccessName())

        while len(stack) > 0:
            if isinstance(stack[-1], VariableUse) or isinstance(stack[-1], FunctionCall) or isinstance(stack[-1], Token) and stack[-1].hasFlag( TKN_NUMBER ):
                temp_stack.append( stack.pop() )
            else: # Operator
                if not isinstance(temp_stack[-2], str): raise Exception("Too complex math! (TODO: Can this even happen?)")
                if isinstance(temp_stack[-1], VariableUse):
                    out += self.generateAction(self.operatorToAction(stack[-1].data), temp_stack[-1].getAccessName(block)) + "\n"
                elif isinstance(temp_stack[-1], FunctionCall):
                    out += temp_stack[-1].evaluate() + "\n"
                    out += self.generateAction(self.operatorToAction(stack[-1].data), temp_stack[-1].getAccessName(block)) + "\n"
                elif isinstance(temp_stack[-1], Token):
                    out += self.generateAction(self.operatorToAction(stack[-1].data), temp_stack[-1].data) + "\n"

                temp_stack.pop()
                stack.pop()

        return out

class Function:
    def __init__(self, symbol, argList):
        self.symbol = symbol
        self.attr = []

        self.argumentList = argList # Local Variables list

        self.localVariables = [] # This function local variables

    def getAccessName(self):
        return f"global.retvar_{self.symbol}"

    def generateSetStack(self, var, varId, value):
        out = "set_temp_variable = {" + var.getLocalAddressAccessName() + " = global.supertosscript_stacktop}\n"
        if varId != 0: out += "subtract_from_temp_variable = {" + var.getLocalAddressAccessName() + " = "+ str(varId) +"}\n"
        out += var.generateAction("set", value)  + f" # {var.symbol} \n"

        return out

    def evaluate(self, values): # Call Convention A: pass local variables to stack.
        out = "add_to_variable = { global.supertosscript_stacktop = " + str(len(self.localVariables) + len(self.argumentList)) + "}\n"

        id = 0
        for element in self.argumentList:
            out += self.generateSetStack(element, id, values[id])
            id += 1

        out += f"{self.symbol} = yes\n"
        out += "subtract_from_variable = { global.supertosscript_stacktop = " + str(len(self.localVariables) + len(self.argumentList)) + "}\n"

        id = 0
        for element in self.argumentList: # This allows recursion. We recompute offsets based on old stack top
            out += self.generateSetStack(element, id, values[id])
            id += 1
        return out

class ForLoop:
    def __init__(self, var, aa, operator, limit, delta):
        self.var = var
        self.begin = aa
        self.compare = operator
        self.limit = limit
        self.delta = delta

class ForEachLoop:
    def __init__(self, value, index, array):
        self.value = value
        self.index = index
        self.array = array

class If:
    def __init__(self, equation):
        self.equation = equation
class While:
    def __init__(self, equation):
        self.equation = equation
class Variable:
    def __init__(self, attr=None, parts=None, size=0, value=0):
        if attr is None:
            attr = []
        if parts is None:
            parts = [""]
        global internalIdCount
        self.attr = attr
        self.exact = "exact" in attr # Has no effect on local variables
        self.isLocal = "local" in attr
        self.localised = "localised" in attr
        self.isArray = "array" in attr # No array can be local.

        self.symbol = len(parts) > 1 and parts[1] or parts[0] # Source name
        self.size = size
        self.value = value
        self.internalID = internalIdCount # Used in naming for global variables and as stack offset in local variables
        internalIdCount += 1
        self.scope = len(parts) > 1 and parts[0] or ""

    def __str__(self):
        return f"SupertosScript Variable ({self.scope or "None"}|{self.symbol})"

    def getLocalAddressAccessName(self):
        return f"locvar_{self.internalID}"
    def getAccessName(self): # Returns PDXScript name by which this variable can be accessed
        if self.exact: return (self.scope != "" and self.scope + "." or "")+self.symbol
        if self.isLocal: return f"global.supertosscript_stack^{self.getLocalAddressAccessName()}"
        return (self.scope != "" and self.scope + "." or "") + "glovar_" + str(self.internalID)

    def evaluate(self, values): # Returns PDXScript code required to run in order to access this data
        return "" # Thank god we can access arrays and vars alike with no preparation

    def generateAction(self, action, value, id=0):
        name = self.getAccessName()
        out = action + (self.isLocal and "_temp_variable = {" or "_variable={") + name
        if self.isArray: out += f"^{id}"
        return out + "=" + value + "}"
