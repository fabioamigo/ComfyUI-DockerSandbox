import { app } from "/scripts/app.js";

app.registerExtension({
    name: "DockerSandbox.Extensions",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        // CORRIGIDO: Checa pelo nome da classe Python (sem espaços)
        if (nodeData.name === "DockerSandboxRunner") { 

            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
                this.setSize([350, 150]); 
                return r;
            };

            // --- FUNÇÃO PARA INJETAR OPÇÕES DE MENU ---
            const getExtraMenuOptions = nodeType.prototype.getExtraMenuOptions;
            nodeType.prototype.getExtraMenuOptions = function (_, options) {
                const me = this;
                
                // 1. ADD INPUT
                options.push({
                    content: "+ Add Input (Dynamic)",
                    callback: () => {
                        const name = prompt("Enter variable name (e.g., width, my_text):");
                        if (!name) return;

                        const validTypes = ["STRING", "INT", "FLOAT", "BOOLEAN", "*"];
                        let type = prompt(
                            `Enter type exactly as shown:\n\n${validTypes.join("\n")}\n\n(* = Any/Wildcard)`,
                            "*"
                        );

                        if (!type) return;
                        type = type.toUpperCase();

                        if (!validTypes.includes(type)) {
                            alert(`Invalid type! Please use one of: ${validTypes.join(", ")}`);
                            return;
                        }

                        const finalName = `${name} (${type})`;
                        const exists = me.findInputSlot(finalName);
                        
                        if (exists !== -1) {
                            alert("An input with this name already exists.");
                            return;
                        }

                        me.addInput(finalName, type);
                        app.graph.setDirtyCanvas(true, true);
                    }
                });

                // 2. REMOVE UNUSED INPUTS
                options.push({
                    content: "- Remove Unused Inputs",
                    callback: () => {
                        for (let i = me.inputs.length - 1; i >= 0; i--) {
                            const input = me.inputs[i];
                            // Ignora os inputs fixos (code, timeout, memory_limit)
                            if (["code", "timeout", "memory_limit"].includes(input.name)) continue;
                            
                            // Remove se não estiver conectado
                            if (!input.link) {
                                me.removeInput(i);
                            }
                        }
                        app.graph.setDirtyCanvas(true, true);
                    }
                });

                if (getExtraMenuOptions) {
                    return getExtraMenuOptions.apply(this, arguments);
                }
            };
        }
    }
});