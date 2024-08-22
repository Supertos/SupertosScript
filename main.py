import tokenizer as tknzer
import blockifier as blkfw
import statemizer as sttmz

tokenizer = tknzer.Tokenizer()
blockifier = blkfw.Blockifier()
statemizer = sttmz.Statemizer()
with open("input.txt") as f:
    tokens = tokenizer.tokenize(tokenizer.preprocess(f.read()))
    print(tokens)
    tree = blockifier.blockify(tokens)
    print(":", tree)
    tree = statemizer.statemize(tree)
