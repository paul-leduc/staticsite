import os
import shutil


def copy_static(src_p, dst_p):
    # if destination path does not exist create it
    if not os.path.exists(dst_p):
        print(f"Creating destintion directory {dst_p}")
        os.mkdir(dst_p)
 
    if not os.path.exists(dst_p):
        raise Exception(f"{dst_p} does not exist could not create directory")
    
    deltree(dst_path=dst_p)
    deep_copy(src_path=src_p, dst_path=dst_p)

def deep_copy(src_path, dst_path):
    # if source path does not exist or is a file, error
    if not os.path.exists(src_path) or os.path.isfile(src_path):
        raise Exception(f"{src_path} does not exist or is not a directory")
    
    # Loop on the directory contents
    for item in os.listdir(src_path):
        
        # is the current item a directory?
        if os.path.isdir(os.path.join(src_path, item)):
            print(f"Creating destintion directory {os.path.join(dst_path, item)}")
            os.mkdir(os.path.join(dst_path, item))
            print(f"Deep copy with source directory {os.path.join(src_path, item)} and destintion directory {os.path.join(dst_path, item)}")
            deep_copy(os.path.join(src_path, item), os.path.join(dst_path, item))
        elif os.path.isfile(os.path.join(src_path, item)):
        # Is the current item a file
            print(f"Copying source file {os.path.join(src_path, item)} to destintion directory {os.path.join(dst_path, item)}")
            shutil.copy2(os.path.join(src_path, item), os.path.join(dst_path, item))
        else:
        # Don't know what the item is
            print(f"{os.path.join(src_path, item)} is not a file or directory")
            


def deltree(dst_path):
    if not os.path.exists(dst_path) or os.path.isfile(dst_path):
        raise Exception(f"{dst_path} does not exist or is not a directory")
    
    print(f"Deleting destintion directory {dst_path}")

    # Loop on the directory contents
    for item in os.listdir(dst_path):
        
        # is the current item a directory?
        if os.path.isdir(os.path.join(dst_path, item)):
            print(f"Deleting destintion directory {os.path.join(dst_path, item)}")
            deltree(os.path.join(dst_path, item))
            os.rmdir(os.path.join(dst_path, item))
            
        elif os.path.isfile(os.path.join(dst_path, item)):
        # Is the current item a file
            print(f"Deleting destintion file {os.path.join(dst_path, item)}")
            os.remove(os.path.join(dst_path, item))
        else:
        # Don't know what the item is
            print(f"{os.path.join(dst_path, item)} is not a file or directory")
    

