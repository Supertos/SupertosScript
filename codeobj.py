
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

class VariableDeclaration(VariableUse):
    def __init__(self, attr, parts, size, value, id ):
        super().__init__(parts, id)
        self.value = value
        self.size = size
        self.attr = attr

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
        if contents is None: contents = []
        self.contents = contents

    def pushData(self, data):
        self.contents.append(data)

    def singleElement(self):
        if len(self.contents) == 1:
            return self.contents[0]
        else:
            return None


class Function:
    def __init__(self, symbol, argList):
        self.symbol = symbol

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
class Variable:
    def __init__(self):
        global internalIdCount
        self.exact = False # Has no effect on local variables
        self.isLocal = False
        self.localised = False
        self.isArray = False # No array can be local.

        self.symbol = "" # Source name
        self.size = 0
        self.value = 0
        self.internalID = internalIdCount # Used in naming for global variables and as stack offset in local variables
        internalIdCount += 1
        self.scope = ""

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
