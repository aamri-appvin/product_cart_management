import version
import json 
import os
from datetime import datetime
import subprocess
import argparse

VERSION_FILE="version.json"

def load_file():
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE,"r") as file:
            return json.load(file)
    return {}

def save_version(version_data):
    with open(VERSION_FILE,"w") as file:
        json.dump(version_data,file,indent=4)
    

def increement_version(current_version:str,part:str):
    major,minor,patch=map(int,current_version.split("."))
    if part=="major":
        major=major+1
        minor,patch=0,0
    elif part=="minor":
        minor=minor+1
        patch=0
    elif part=="patch":
        patch=patch+1
    else:
        raise ValueError("Invalid part provided")
    
    return f"{major}.{minor}.{patch}"


def update_version(component,part):

    if not os.path.exists(VERSION_FILE):
        raise ValueError("Version File Does Not Exist")
    
    version_data=load_file()

    if component not in version_data:
        raise ValueError("Component not in version file")
    
    current_version=version_data[component]

    print(f"v{current_version} is your current version")

    if not isinstance(current_version,str):
        current_version=str(current_version)

    if not current_version.count(".")==2:
        raise ValueError("Invalid version!")
    
    version_data[component]=increement_version(str(current_version),part)
    version_data["release_date"]=datetime.today().strftime("%Y-%m-%d")
    version_data["description"]=f"Version is updated for {component} from v{current_version} to v{version_data[component]}"
    commit_msg=f"Version is updated for {component} from v{current_version} to v{version_data[component]}"
    git_tag=f"{component}-v{version_data[component]}"
    save_version(version_data)
    try:
        subprocess.run(["git","add",VERSION_FILE],check=True)
        subprocess.run(["git","commit","-m",commit_msg],check=True)

        existing_tags=subprocess.run(["git","tag"],capture_output=True,text=True)
        print("Existing tags are",existing_tags.stdout)
        
        if git_tag in existing_tags.stdout.split():
            subprocess.run(["git","tag","-d",git_tag],check=True)
            subprocess.run(["git","push","origin","--delete",git_tag],check=True)

        subprocess.run(["git","tag",git_tag],check=True)
        subprocess.run(["git","push","origin","master"],check=True)
        subprocess.run(["git","push","origin",git_tag],check=True)
    except subprocess.CalledProcessError as error:
        raise RuntimeError(f"Git command failed with error {error}")

    print(f"v{version} is the updated version")

if __name__=="__main__":
    parser=argparse.ArgumentParser(description="To update the version of a specific component")
    parser.add_argument("component", help="Component to update")
    parser.add_argument("part",choices=["major","minor","patch"], help="New part")
    args=parser.parse_args()
    update_version(args.component,args.part)