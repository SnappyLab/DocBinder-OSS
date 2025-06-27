def build_id_to_item(files):
    """
    Build a mapping from file/folder id to the file/folder object.
    """
    return {getattr(f, "id", None): f for f in files if hasattr(f, "id")}


def get_full_path(file, id_to_item, root_id="root", root_name="My Drive"):
    """
    Recursively build the full path for a file or folder using its parents.
    Returns a string like '/My Drive/Folder/Subfolder/File.pdf'.
    """
    path_parts = [file.name]
    current = file
    while True:
        parents = getattr(current, "parents", None)
        if not parents or not isinstance(parents, list) or not parents[0]:
            break
        parent_id = parents[0]
        if parent_id == root_id:
            path_parts.append(root_name)
            break
        parent = id_to_item.get(parent_id)
        if not parent:
            break
        path_parts.append(parent.name)
        current = parent
    return "/" + "/".join(reversed(path_parts))


def build_all_full_paths(files, root_id="root", root_name="My Drive", root_id_to_name=None):
    """
    Efficiently compute the full path for every file/folder in one pass using an iterative approach
    and memoization.
    Supports multiple drives by using a root_id_to_name mapping.
    Returns a dict: {file_id: full_path}
    """
    id_to_item = build_id_to_item(files)
    id_to_path = {}
    if root_id_to_name is None:
        root_id_to_name = {root_id: root_name}
    for item in files:
        if not hasattr(item, "id") or not hasattr(item, "name"):
            continue
        if item.id in id_to_path:
            continue
        # Iterative path construction
        current = item
        temp_stack = []
        while True:
            if current.id in id_to_path:
                break
            parents = getattr(current, "parents", None)
            if not parents or not isinstance(parents, list) or not parents[0]:
                temp_stack.append((current.id, "/" + current.name))
                break
            parent_id = parents[0]
            if parent_id in root_id_to_name:
                temp_stack.append((current.id, "/" + root_id_to_name[parent_id] + "/" + current.name))
                break
            parent = id_to_item.get(parent_id)
            if not parent:
                temp_stack.append((current.id, "/" + current.name))
                break
            temp_stack.append((current.id, None))  # Mark as not yet resolved
            current = parent
        # Now unwind the stack and build the paths
        while temp_stack:
            file_id, path = temp_stack.pop()
            if path is not None:
                id_to_path[file_id] = path
            else:
                parent_id = id_to_item[file_id].parents[0]
                parent_path = id_to_path.get(parent_id, "")
                id_to_path[file_id] = parent_path.rstrip("/") + "/" + id_to_item[file_id].name
        # Ensure root_name is present at the start (for legacy single-drive fallback)
        found_root = False
        for root_name_val in root_id_to_name.values():
            if id_to_path[item.id].lstrip("/").startswith(root_name_val + "/"):  # e.g. 'My Drive/'
                found_root = True
                break
        if not found_root:
            # Use the first root_name as fallback
            fallback_root = next(iter(root_id_to_name.values()))
            id_to_path[item.id] = (
                "/" + fallback_root + id_to_path[item.id]
                if not id_to_path[item.id].startswith("/")
                else "/" + fallback_root + id_to_path[item.id]
            )
    return id_to_path
