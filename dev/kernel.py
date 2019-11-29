import ast
import symtable
import code

class Kernel:
    def __init__(self, fileName):
        self.fileName = fileName
    def load():
        pass
    def feed(self, source):
        tree = ast.parse(source, filename=self.fileName)
        print(tree)


if __name__ == '__main__':
    from pathlib import Path
    import sys
    n = sys.argv[1]
    source = Path(n).read_text()
    kernel = Kernel(n)
    kernel.feed(source)
