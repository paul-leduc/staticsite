from textnode import TextNode, TextType, BlockType, text_node_to_html_node
import re
from htmlnode import HTMLNode
from parentnode import ParentNode
from leafnode import LeafNode

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    # Validate that text_type is one of the supported ones
    valid_text_types = {TextType.BOLD, TextType.ITALIC, TextType.CODE}
    if text_type not in valid_text_types:
        raise Exception(f"Unsupported text type: {text_type}")

    new_nodes = []

    for node in old_nodes:
        # Append non-text nodes as-is
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        # Process text nodes by splitting repeatedly on the delimiter
        text = node.text
        while delimiter in text:
            # Split the text on the first occurrence of the delimiter
            pre_delimiter, rest = text.split(delimiter, 1)

            # Ensure the rest includes a closing delimiter
            if delimiter not in rest:
                raise Exception(f"Invalid or unbalanced markdown detected for delimiter '{delimiter}'")

            # Split again to extract the content within the delimiters
            delimited_text, post_delimiter = rest.split(delimiter, 1)

            # Append the parts: text before, delimited text, and continue
            if pre_delimiter:
                new_nodes.append(TextNode(pre_delimiter, TextType.TEXT))
            new_nodes.append(TextNode(delimited_text, text_type))
            text = post_delimiter

        # Append any remaining text after the last closing delimiter
        if text:
            new_nodes.append(TextNode(text, TextType.TEXT))

    return new_nodes

def extract_markdown_images(text):
    matches = re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches

def extract_markdown_links(text):
    matches = re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches

def split_nodes_image(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        original_text = old_node.text
        images = extract_markdown_images(original_text)
        if len(images) == 0:
            new_nodes.append(old_node)
            continue
        for image in images:
            sections = original_text.split(f"![{image[0]}]({image[1]})", 1)
            if len(sections) != 2:
                raise ValueError("invalid markdown, image section not closed")
            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            new_nodes.append(
                TextNode(
                    image[0],
                    TextType.IMAGE,
                    image[1],
                )
            )
            original_text = sections[1]
        if original_text != "":
            new_nodes.append(TextNode(original_text, TextType.TEXT))
    return new_nodes


def split_nodes_link(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        original_text = old_node.text
        links = extract_markdown_links(original_text)
        if len(links) == 0:
            new_nodes.append(old_node)
            continue
        for link in links:
            sections = original_text.split(f"[{link[0]}]({link[1]})", 1)
            if len(sections) != 2:
                raise ValueError("invalid markdown, link section not closed")
            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            new_nodes.append(TextNode(link[0], TextType.LINK, link[1]))
            original_text = sections[1]
        if original_text != "":
            new_nodes.append(TextNode(original_text, TextType.TEXT))
    return new_nodes

def text_to_textnodes(text):
    node = TextNode(text, TextType.TEXT)
    new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
    new_nodes = split_nodes_delimiter(new_nodes, "_", TextType.ITALIC)
    new_nodes = split_nodes_delimiter(new_nodes, "`", TextType.CODE)
    new_nodes = split_nodes_image(new_nodes)
    new_nodes = split_nodes_link(new_nodes)
    return new_nodes
            

def markdown_to_blocks(markdown):
    blocks=[]
    blocks = markdown.strip().split("\n\n")
    blocks = list(filter(None, blocks))
    return blocks

def block_to_block_type(block):
    print(f"block_to_block_type received block: '{block}'")
    # Heading
    if block.startswith('#'):
        prefix = block.split()[0]
        if len(prefix) > 0 and len(prefix) < 7:
            print(f"block_to_block_type returning HEADING for: '{block}'")
            return BlockType.HEADING
    # Code
    elif block.startswith('```') and block.endswith('```'):
        print(f"block_to_block_type returning CODE for: '{block}'")
        return BlockType.CODE
    elif block.startswith('>'):
        # Quote
        isQuote = True
        for line in block.split('\n'):
            if not line.startswith('>'):
                isQuote = False
                break
        if isQuote:
            print(f"block_to_block_type returning QUOTE for: '{block}'")
            return BlockType.QUOTE
    # Unordered List
    elif block.startswith('- '):
        isList = True
        for line in block.split('\n'):
            if not line.startswith('- '):
                isList = False
                break
        if isList:
            print(f"block_to_block_type returning UNORDERED_LIST for: '{block}'")
            return BlockType.UNORDERED_LIST
    # Ordered List
    elif block.startswith('1. '):
        isList = True
        item = 1
        for line in block.split('\n')[1:]:
            this_item, _ = line.split('.')
            if this_item != item + 1:
                isList = False
                break
            else:
                item += 1
        if isList:
            print(f"block_to_block_type returning ORDERED_LIST for: '{block}'")
            return BlockType.ORDERED_LIST
        
    # Paragraph
    print(f"block_to_block_type returning PARAGRAPH for: '{block}'")
    return BlockType.PARAGRAPH

def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    children = []
    for text_node in text_nodes:
        html_node = text_node_to_html_node(text_node)
        children.append(html_node)
    return children


def markdown_to_html_node(markdown):
    block_nodes = []
    print(f"Markdown is: {markdown}")
    # Split the markdown into blocks
    markdown_blocks = markdown_to_blocks(markdown)

    # Loop over the blocks
    for markdown_block in markdown_blocks:

        if markdown_block.strip() == "":
            continue
        
        print(f"Processing block: '{markdown_block}'")

        # Determine the type of block
        block_type = block_to_block_type(markdown_block)
        print(f"Detected block type: {block_type}")

        # Based on the type of block, create a new HTMLNode with the proper data
        if block_type == BlockType.HEADING:
            parts = markdown_block.split()
            level = len(parts[0])
            clean_text = " ".join(parts[1:])

            children = text_to_children(clean_text)
            node = ParentNode(f"h{level}", children=children)
            
        elif block_type == BlockType.UNORDERED_LIST:
            li_nodes = []
            for line in markdown_block.splitlines():
                line = line.strip()
                if not line:
                    continue
                if line.startswith("- "):
                    item_text = line[2:]
                else:
                    item_text = line

                li_children = text_to_children(item_text)
                li_node = ParentNode("li", children=li_children)
                li_nodes.append(li_node)

            node = ParentNode("ul", children=li_nodes)
            
        elif block_type == BlockType.ORDERED_LIST:
            pattern = r"^\d+\.\s"
            li_nodes = []
            for line in markdown_block.splitlines():
                line = line.strip()
                if not line:
                    continue
                match = re.match(pattern, line)
                if match is not None:
                    matched_string = match.group(0)
                    l = len(matched_string)
                    item_text = line[l:]
                else:
                    item_text = line

                li_children = text_to_children(item_text)
                li_node = ParentNode("li", children=li_children)
                li_nodes.append(li_node)

            node = ParentNode("ol", children=li_nodes)

        elif block_type == BlockType.PARAGRAPH:
            clean_lines = []
            for line in markdown_block.splitlines():
                line = line.lstrip()
                if not line:
                    continue
                else:
                    clean_lines.append(line)

            clean_text = "\n".join(clean_lines).strip()
            children = text_to_children(clean_text)
            node = ParentNode("p", children=children)
        
        elif block_type == BlockType.QUOTE:
            clean_lines = []
            for line in markdown_block.splitlines():
                line = line.lstrip()
                if line.startswith("> "):
                    clean_lines.append(line[2:])
                elif line.startswith(">"):
                    clean_lines.append(line[1:])
                else:
                    clean_lines.append(line)
            clean_text = "\n".join(clean_lines).strip()
            children = text_to_children(clean_text)
            node = ParentNode("blockquote", children=children)

        elif block_type == BlockType.CODE:
            # The "code" block is a bit of a special case: it should not do any inline markdown parsing of its children.
            lines = markdown_block.splitlines()

            code_lines = lines[1:-1]
            code_text = "\n".join(code_lines) + "\n" 
            print(f"Code text is {code_text}")

            text_node = TextNode(code_text, TextType.CODE)
            code_node = text_node_to_html_node(text_node)

            node = ParentNode("pre", children=[code_node])

        # Assign the proper child HTMLNode objects to the block node.
        block_nodes.append(node)

    
    # Make all the block nodes children under a single parent HTML node (which should just be a div) and return it.
    doc = ParentNode("div",children=block_nodes)
    return doc