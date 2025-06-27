def flatten_file(item, provider=None):
    """
    Convert a file object (Pydantic, DummyFile, or dict) to a flat dict for export.
    Flattens owners, parents, and last_modifying_user fields, and adds provider if given.
    """
    # Convert to dict
    if hasattr(item, "model_dump"):
        result = item.model_dump()
    elif hasattr(item, "__dict__"):
        result = dict(item.__dict__)
    else:
        result = dict(item)
    # Add provider field to output dict
    if provider:
        result["provider"] = provider
    # Flatten owners to email addresses
    owners = result.get("owners")
    if owners:
        emails = []
        for owner in owners:
            if isinstance(owner, dict):
                emails.append(owner.get("email_address") or owner.get("email") or str(owner))
            elif hasattr(owner, "email_address"):
                emails.append(owner.email_address)
            else:
                emails.append(str(owner))
        result["owners"] = ";".join(filter(None, emails))
    # Flatten parents to semicolon-separated string
    parents = result.get("parents")
    if isinstance(parents, list):
        result["parents"] = ";".join(str(p) for p in parents)
    elif parents is None:
        result["parents"] = ""
    else:
        result["parents"] = str(parents)
    # Flatten last_modifying_user to email address
    lmu = result.get("last_modifying_user")
    if lmu:
        if isinstance(lmu, dict):
            result["last_modifying_user"] = lmu.get("email_address") or lmu.get("email") or str(lmu)
        elif hasattr(lmu, "email_address"):
            result["last_modifying_user"] = lmu.email_address
        else:
            result["last_modifying_user"] = str(lmu)

    return result
