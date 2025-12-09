# __init__.py
from .sandbox_node import DockerSandboxRunner

# Mapeia a string usada no JSON do workflow para a classe Python
NODE_CLASS_MAPPINGS = {
    "DockerSandboxRunner": DockerSandboxRunner
}

# Mapeia o nome da classe para o nome de exibição no menu do ComfyUI
NODE_DISPLAY_NAME_MAPPINGS = {
    "DockerSandboxRunner": "Docker Sandbox Runner"
}

# ESTE CAMPO É CRÍTICO para o carregamento do JavaScript!
WEB_DIRECTORY = "./web" 

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']

# No final do arquivo __init__.py
print("✅ CUSTOM NODE DOCKER SANDBOX REGISTRADO COM SUCESSO.")