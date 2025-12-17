from textnode import TextNode, TextType
from static import deltree
from static import deep_copy
from generate import generate_page, generate_pages_recursive
import sys


def main():

    basepath = sys.argv[1] if len(sys.argv) > 1 else "/"

    print(basepath)

    deltree("docs")
    deep_copy("static", "docs")
    #generate_page("content", ".", "docs")
    generate_pages_recursive("content", ".", "docs", basepath)
    
    open("docs/.nojekyll", "w").close()



main()
