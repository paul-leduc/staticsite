import os
import shutil
from markdown_blocks import markdown_to_html_node
from inline_markdown import extract_title

def generate_page(from_path, template_path, dest_path):
    print(f'Generating page from {from_path} to {dest_path} using {template_path}')
    #markdown_file = os.path.join(from_path, 'index.md')
    markdown_file = from_path
    markdown = None

    template_file = os.path.join(template_path, 'template.html')
    template = None

    #page = os.path.join(dest_path, 'index.html')
    page = dest_path

    with open(markdown_file, 'r') as md_file:
        markdown = md_file.read()    
    
    with open(template_file, 'r') as template_file:
        template = template_file.read()
    
    html = markdown_to_html_node(markdown=markdown)
    title = extract_title(markdown=markdown)

    dest_parent = os.path.dirname(dest_path)
    if not os.path.exists(dest_parent):
        os.makedirs(dest_parent)
    #print(f"Page is {page}")
    with open(page, 'w') as pg:
        template = template.replace('{{ Title }}', f'{title}')
        template = template.replace('{{ Content }}', f'{html.to_html()}')
        pg.write(f'{template}')

def crawl_content(dir_path_content):
    content = []

    if not os.path.exists(dir_path_content) or not os.path.isdir(dir_path_content):
        raise Exception(f'{dir_path_content} not found or is not a directory')
    
    # Loop on the directory contents
    for item in os.listdir(dir_path_content):
        
        # is the current item a directory?
        if os.path.isdir(os.path.join(dir_path_content, item)):
            #print(f"Processing directory {os.path.join(dir_path_content, item)}")
            content += crawl_content(os.path.join(dir_path_content, item))
        elif os.path.isfile(os.path.join(dir_path_content, item)):
        # Is the current item a file
            #print(f"Processing file {os.path.join(dir_path_content, item)}")
            content.append(os.path.join(dir_path_content, item))
            
        else:
        # Don't know what the item is
            print(f"{os.path.join(dir_path_content, item)} is not a file or directory")
        #print(f"Content is {content}")

    return content

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    pages = crawl_content(dir_path_content)

    for page in pages:
        dest_dir_path = page.replace('content', 'public')
        dest_dir_path = os.path.splitext(dest_dir_path)[0] + ".html"
        print(page,template_path, dest_dir_path)   
        generate_page(page,template_path, dest_dir_path) 