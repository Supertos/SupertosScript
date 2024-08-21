import tokenizer as tknzer
import blockifier as blkfw

tokenizer = tknzer.Tokenizer()
blockifier = blkfw.Blockifier()
with open("input.txt") as f:
    tokens = tokenizer.tokenize(tokenizer.preprocess(f.read()))
    print(tokens)
    tree = blockifier.blockify(tokens)
    print(":", tree)
