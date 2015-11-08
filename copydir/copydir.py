#################################################################################
# DESC  : copy directory by re-building, not copying data. when you want to copy
#         a very big size directory which exists in remote network, and you dont
#         care about what the data in the direcotry is, you just want to simulate
#         the directory structure and size, then you neednt to copy it by network. 
# AUTHOR: Teck
# DATE  : 2015/11/08
#################################################################################
import pickle, getopt, sys, os
from enum import Enum

'''
Operation type
'''
class OperType(Enum):
    NONE    = 0
    COPY    = 1 # copy directory info, and create a pickle file
    BUILD   = 2 # rebuild directory from pickle file

#--------------------------------------------------------------------------------

'''
Simulate direcotry tree
'''
class FileItem:
    def __init__(self, item_type, item_name, item_size):
        print("FileItem: %s - %s" % (item_name, item_type))
        self.sub_items = []
        self.type = item_type # 0: dir 1: file
        self.name = item_name
        self.size = item_size # 0 for directory

    def AddSubItem(self, item):
        self.sub_items.append(item)

    def Construct(self, path):
        pass

#--------------------------------------------------------------------------------
    
'''
Help info
'''
def Usage():
    print("copydir.py {-c -s src_dir | -b -d dst_dir | -h} [-p pickle_file]")
    print("-h: help message")
    print("-c: copy directory structure to pickle file")
    print("-b: build directory structure from pickle file")
    print("-s: source direcotry to be copied")
    print("-d: dest directory to build in")
    print("-p: specify pickle file, if not specified, default is data.pickle")
    sys.exit(0)

#--------------------------------------------------------------------------------

'''
Create file or directory
'''
def MakeFileItem(dst_dir, file_item):
    if not os.path.exists(dst_dir):
        print("Failed: Dest path (%s) is not exists" % dst_dir)
        sys.exit(1)

    abs_path = os.path.join(dst_dir, file_item.name);
    if os.path.exists(abs_path):
        print("Failed: Path to be build (%s) exists" % abs_path)
        sys.exit(1)

    if file_item.type == 0: # directory
        os.mkdir(abs_path)
    elif file_item.type == 1: # file
        with open(abs_path, 'w') as f:
            f.seek(file_item.size)
            f.write('\0') # make file size
    else:
        print("Failed: Invalid file item type: %d" % file_item.type)

#--------------------------------------------------------------------------------

'''
Copy directory
'''
def CopyDir(src_dir):
    file_item = FileItem(0, os.path.basename(src_dir), 0)
    for item in os.listdir(src_dir):
        abs_item = os.path.join(src_dir, item)
        if os.path.isfile(abs_item):
            print("- " + abs_item)
            sub_item = FileItem(1, item, os.path.getsize(abs_item))
            file_item.AddSubItem(sub_item)
        elif os.path.isdir(abs_item):
            print("+ " + abs_item)
            sub_item = CopyDir(abs_item)
            file_item.AddSubItem(sub_item)
    return file_item

#--------------------------------------------------------------------------------

'''
Build direcotry recursively
'''
def BuildDir(dst_dir, file_item):
    MakeFileItem(dst_dir, file_item)
    for sub_item in file_item.sub_items:
        BuildDir(os.path.join(dst_dir, file_item.name), sub_item)

#--------------------------------------------------------------------------------

'''
Get command line opertion and parameters
'''
def GetCommandLinePara():
    short_args = 'hcbs:d:p:'
    try:
        opts, args = getopt.getopt(sys.argv[1:], short_args, '')
    except:
        print("Failed: Command line error")
        sys.exit(1)
        
    src_dir = ''
    dst_dir = ''
    pickle_file = 'data.pickle' # default pickle file
    oper_type = OperType.NONE

    for o, a in opts:
        if o == '-h':
            Usage()
        elif o == '-c':
            oper_type = OperType.COPY
        elif o == '-b':
            oper_type = OperType.BUILD
        elif o == '-s':
            src_dir = a
        elif o == '-d':
            dst_dir = a
        elif o == '-p':
            pickle_file = a
        else:
            print("Invalid options")
            sys.exit(1)
            
    return (oper_type, src_dir, dst_dir, pickle_file)

#--------------------------------------------------------------------------------

def Main():
    oper_type, src_dir, dst_dir, pickle_file = GetCommandLinePara()
  
    if oper_type == OperType.COPY:
        if src_dir == '':
            print("Failed: You should specify source direcotry")
            sys.exit(1)
        file_item = CopyDir(src_dir)
        with open(pickle_file, 'wb') as f:
            pickle.dump(file_item, f)
    elif oper_type == OperType.BUILD:
        if dst_dir == '':
            print("Failed: You should specify dest directory")
            sys.exit(1)
        file_item = None
        with open(pickle_file, 'rb') as f:
            file_item = pickle.load(f)
        BuildDir(dst_dir, file_item)
    else:
        print("Failed: did not specify operation type")

#--------------------------------------------------------------------------------

if __name__ == '__main__':
    Main()
