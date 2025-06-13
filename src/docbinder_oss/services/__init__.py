import pkgutil
import importlib

# This dictionary will be built automatically
PROVIDER_REGISTRY = {}

# Discover and import all modules in the 'services' package
for _, name, _ in pkgutil.iter_modules(__path__):
    if name not in ('base_client', '__init__'): # Skip non-provider files
        # Dynamically import the module (e.g., providers.google)
        module = importlib.import_module(f".{name}", __package__)

        # Look for a 'register' function and call it
        if hasattr(module, "register"):
            provider_info = module.register()
            PROVIDER_REGISTRY[name] = {
                **provider_info,
            }