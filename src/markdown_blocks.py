from enum import Enum
from htmlnode import ParentNode, LeafNode
from textnode import text_node_to_html_node, TextNode, TextType
from inline_markdown import text_to_textnodes
import re

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    OLIST = "ordered_list"
    ULIST = "unordered_list"


def markdown_to_blocks(markdown):
    blocks = markdown.split("\n\n")
    filtered_blocks = []
    for block in blocks:
        if block == "":
            continue
        block = block.strip()
        filtered_blocks.append(block)
    return filtered_blocks


def block_to_block_type(block):
    lines = block.split("\n")

    if block.startswith(("# ", "## ", "### ", "#### ", "##### ", "###### ")):
        return BlockType.HEADING
    if len(lines) > 1 and lines[0].startswith("```") and lines[-1].startswith("```"):
        return BlockType.CODE
    if block.startswith(">"):
        for line in lines:
            if not line.startswith(">"):
                return BlockType.PARAGRAPH
        return BlockType.QUOTE
    if block.startswith("- "):
        for line in lines:
            if not line.startswith("- "):
                return BlockType.PARAGRAPH
        return BlockType.ULIST
    if block.startswith("1. "):
        i = 1
        for line in lines:
            if not line.startswith(f"{i}. "):
                return BlockType.PARAGRAPH
            i += 1
        return BlockType.OLIST
    return BlockType.PARAGRAPH

def text_to_children(text):
    return [text_node_to_html_node(n) for n in text_to_textnodes(text)]

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    html_blocks = []

    for block in blocks:
        btype = block_to_block_type(block)

        if btype == BlockType.HEADING:
            parts = block.split()
            level = len(parts[0])
            text = " ".join(parts[1:])
            node = ParentNode(f"h{level}", text_to_children(text))

        elif btype == BlockType.ULIST:
            items = []
            for line in block.split("\n"):
                text = line[2:].strip()
                items.append(ParentNode("li", text_to_children(text)))
            node = ParentNode("ul", items)

        elif btype == BlockType.OLIST:
            items = []
            for line in block.split("\n"):
                text = re.sub(r"^\d+\.\s*", "", line)
                items.append(ParentNode("li", text_to_children(text)))
            node = ParentNode("ol", items)

        elif btype == BlockType.QUOTE:
            cleaned = "\n".join(line.lstrip("> ").strip() for line in block.split("\n"))
            node = ParentNode("blockquote", text_to_children(cleaned))

        elif btype == BlockType.CODE:
            lines = block.split("\n")[1:-1]
            code = "\n".join(lines) + "\n"
            code_node = text_node_to_html_node(TextNode(code, TextType.CODE))
            node = ParentNode("pre", [code_node])

        else:
            cleaned = " ".join(line.strip() for line in block.split("\n"))
            node = ParentNode("p", text_to_children(cleaned))

        html_blocks.append(node)

    return ParentNode("div", html_blocks)
