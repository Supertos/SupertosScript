import tokenizer as tknzer
import blockifier as blkfw

tokenizer = tknzer.Tokenizer()
blockifier = blkfw.Blockifier()
with open("input.txt") as f:
    tokens = tokenizer.tokenize(tokenizer.preprocess(f.read()))
    tree = blockifier.blockify(tokens)
    tree.parseHeader()
    tree.parseContents()

    print( tree.contents.list[-1].objData )
    print( tree.objData )
    print( tree.evaluateContents() )
