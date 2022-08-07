import maya.app.general.resourceBrowser as rB

def get_resource_path():
    """
    Shows Maya Factory Icon Browser

    Returns:
        str: path of of icon selected in the Icon Browser to use in custom interface
    """
    resource_browser = rB.resourceBrowser()
    resource_path = resource_browser.run()

    return resource_path

if __name__ == "__main__":
    resource_path = get_resource_path()
    if resource_path:
        print(resource_path)
