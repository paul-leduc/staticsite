from textnode import TextNode, TextType
from static import deltree
from static import deep_copy
from generate import generate_page, generate_pages_recursive



def main():
    deltree("public")
    deep_copy("static", "public")
    #generate_page("content", ".", "public")
    generate_pages_recursive("content", ".", "public")



main()
