import docker
import json
import re
import uuid
import base64
import time

class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False
    def __eq__(self, __value: object) -> bool:
        return True

# CLASSE RENOMEADA
class DockerSandboxRunner:
    CONTAINER_NAME = "comfyui-sandbox-worker"
    DOCKER_IMAGE = "python:3.9-slim"
    SANDBOX_USER = "nobody" 

    def __init__(self):
        self.client = None
        try:
            self.client = docker.from_env()
        except Exception:
            print("⚠️ AVISO: Não foi possível conectar ao Docker. Verifique se o Docker Desktop está rodando.")
        
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "code": ("STRING", {"multiline": True, "placeholder": "# Código limpo, focado apenas na lógica de execução."}),
                # CAMPOS OCULTOS PARA CONFIGURAÇÃO TÉCNICA
                "timeout": ("INT", {"default": 10, "min": 1, "max": 60, "step": 1, "hidden": True}), 
                "memory_limit": ("STRING", {"default": "512m", "placeholder": "Ex: 512m, 1g, 2gb", "hidden": True}), 
            },
            "optional": {
                # Campo de ação removido (como solicitado anteriormente).
            } 
        }

    RETURN_TYPES = (
        AnyType("*"), AnyType("*"), AnyType("*"), AnyType("*"), AnyType("*"), AnyType("*"), 
        "STRING"
    )
    RETURN_NAMES = ("r1", "r2", "r3", "r4", "r5", "r6", "log")
    FUNCTION = "execute_sandbox"
    CATEGORY = "Advanced/Scripting"

    def _ensure_container_running(self, mem_limit):
        """Garante que o container worker está vivo e esperando comandos"""
        if not self.client:
            raise RuntimeError("Docker Client não inicializado. O Docker Desktop está rodando?")

        try:
            container = self.client.containers.get(self.CONTAINER_NAME)
            if container.status != 'running':
                print(f"🛠️ Docker Sandbox: Iniciando container: {self.CONTAINER_NAME}")
                container.start()
            return container
        except docker.errors.NotFound:
            print(f"🛠️ Criando container sandbox: {self.CONTAINER_NAME} com {mem_limit} de RAM...")
            return self.client.containers.run(
                self.DOCKER_IMAGE, 
                command="tail -f /dev/null", 
                name=self.CONTAINER_NAME,
                detach=True,
                mem_limit=mem_limit, 
                network_mode="none",
                user=self.SANDBOX_USER 
            )

    def execute_sandbox(self, code, timeout, memory_limit="512m", **kwargs):
        log_messages = []
        
        final_results = [None] * 6
        object_references = {}
        variable_injection_commands = []
        
        try:
            container = self._ensure_container_running(memory_limit) 
        except Exception as e:
            log_messages.append(f"Docker Error (Startup/Connect): {str(e)}")
            return (*final_results, "\n".join(log_messages))

        # 1. Prepara Variáveis (usando Literal Python)
        for key, value in kwargs.items():
            clean_key = key.split(" (")[0].strip().replace(" ", "_")
            
            if value is None or isinstance(value, bool):
                variable_injection_commands.append(f"{clean_key} = {str(value)}")
            elif isinstance(value, (int, float, str)):
                variable_injection_commands.append(f"{clean_key} = {repr(value)}")
            elif isinstance(value, (list, dict)):
                try:
                    variable_injection_commands.append(f"{clean_key} = {repr(value)}")
                except:
                    ref_id = f"__REF__{uuid.uuid4().hex}"
                    object_references[ref_id] = value
                    variable_injection_commands.append(f"{clean_key} = '{ref_id}'")
            else:
                ref_id = f"__REF__{uuid.uuid4().hex}"
                object_references[ref_id] = value
                variable_injection_commands.append(f"{clean_key} = '{ref_id}'")

        # 2. Constrói o Payload Final (Base64)
        injection_script = "\n".join(variable_injection_commands)

        payload_script = f"""
import json
import sys
import math, random, time, re
import signal

TIMEOUT_SECONDS = {timeout}

def signal_handler(signum, frame):
    print(f"__ERROR_START__TimeoutError: Script execution exceeded {{TIMEOUT_SECONDS}} seconds.__ERROR_END__")
    sys.exit(1)

signal.signal(signal.SIGALRM, signal_handler)
signal.alarm(TIMEOUT_SECONDS) 

{injection_script}

_user_error = None
try:
    exec({repr(code)})
finally:
    signal.alarm(0)

outputs = {{}}
if _user_error:
    outputs['error'] = _user_error
else:
    for i in range(1, 7):
        vname = f"r{{i}}"
        if vname in locals():
            val = locals()[vname]
            try:
                json.dumps(val) 
                outputs[vname] = val
            except:
                outputs[vname] = str(val)
        else:
            outputs[vname] = None

sys.stdout.write("__COMFY_RESULT_START__" + json.dumps(outputs) + "__COMFY_RESULT_END__")
"""
        
        b64_payload = base64.b64encode(payload_script.encode('utf-8')).decode('utf-8')
        cmd = f"python3 -c \"import base64; exec(base64.b64decode('{b64_payload}'))\""

        try:
            exec_result = container.exec_run(
                cmd=cmd,
                workdir="/tmp"
            )
            output_text = exec_result.output.decode('utf-8', errors='ignore')
            
            err_match = re.search(r"__ERROR_START__(.*?)__ERROR_END__", output_text, re.DOTALL)
            if err_match:
                 log_messages.append(f"Script Error (in Docker):\n{err_match.group(1)}")
                 return (*final_results, "\n".join(log_messages) + "\n" + output_text)

            match = re.search(r"__COMFY_RESULT_START__(.*?)__COMFY_RESULT_END__", output_text, re.DOTALL)
            if match:
                json_str = match.group(1)
                extracted_dict = json.loads(json_str)
                
                if 'error' in extracted_dict:
                    log_messages.append(f"Runtime Error:\n{extracted_dict['error']}")
                    return (*final_results, "\n".join(log_messages) + "\n" + output_text)

                for i in range(6):
                    key = f"r{i+1}"
                    val = extracted_dict.get(key)
                    
                    if isinstance(val, str) and val in object_references:
                        final_results[i] = object_references[val]
                    else:
                        final_results[i] = val
            
            log_messages.append("SUCCESS: Script executado com sucesso.")
            return (*final_results, "\n".join(log_messages) + "\n" + output_text)

        except Exception as e:
             log_messages.append(f"Execution Infrastructure Error (Docker exec failed): {str(e)}")
             return (*final_results, "\n".join(log_messages))