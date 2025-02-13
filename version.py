import json
import os
from datetime import datetime
import subprocess

VERSION_FILE="version.json"

default_version_info = {
    "fast_api": "0.1.0",
    "db_version": "0.1.0",
    "minio_version": "0.1.0",
    "grafana_version": "0.1.0",
    "release_date": "2025-02-13",
    "description": "Initial release with structured data processing"
}

if not os.path.exists(VERSION_FILE):
    with open(VERSION_FILE,"w") as file:
        json.dump(default_version_info,file,indent=4)


def load_version():
    with open(VERSION_FILE,"r") as file:
        return json.load(file)
    
def get_version():
    return json.dumps(load_version(),indent=4)

def update_version(component,version):
    version_data=load_version()
    version_data[component]=version
    version_data["release_date"]=datetime.today().strftime("%Y-%m-%d")

    if component not in version_data:
        raise ValueError("Component not in the version data")
    
    with open(VERSION_FILE,"w") as file:
        json.dump(version_data,file,indent=4)

    git_tag=f"{component}-v{version}"
    commit_msg=f"version for the project has been changed to {version} for the component {component}"


    try:
        subprocess.run(["git","add",VERSION_FILE],check=True)
        subprocess.run(["git","commit","-m",commit_msg],check=True)
        subprocess.run(["git","tag",git_tag],check=True)
        subprocess.run(["git","push","origin","master"],check=True)
        subprocess.run(["git","push","origin",git_tag],check=True)
    except subprocess.CalledProcessError as error:
        raise RuntimeError(f"Git command failed with error {error}")
    
    return {"message":commit_msg}