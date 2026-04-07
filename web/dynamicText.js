import { app } from "../../scripts/app.js";

/**
 * AFOLIE 动态文本接口节点 - 动态输入接口控制
 * 提供添加/删除文本输入接口的功能
 */
app.registerExtension({
    name: "AFOLIE.DynamicTextInterface",
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeType.comfyClass === "AFOLIE动态文本接口") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            
            nodeType.prototype.onNodeCreated = function() {
                const result = onNodeCreated?.apply(this, arguments);
                
                // 初始化输入计数器
                this.textInputCounter = 0;
                
                // 创建控制按钮容器
                const buttonContainer = document.createElement("div");
                buttonContainer.style.display = "flex";
                buttonContainer.style.alignItems = "center";
                buttonContainer.style.justifyContent = "center";
                buttonContainer.style.padding = "8px";
                buttonContainer.style.gap = "10px";
                
                // 创建添加按钮
                const addBtn = document.createElement("button");
                addBtn.innerHTML = "➕ 添加接口";
                addBtn.title = "添加一个新的文本输入接口";
                addBtn.style.padding = "6px 12px";
                addBtn.style.border = "1px solid #4a9eff";
                addBtn.style.borderRadius = "4px";
                addBtn.style.backgroundColor = "#2a5a8a";
                addBtn.style.color = "#fff";
                addBtn.style.cursor = "pointer";
                addBtn.style.fontSize = "12px";
                addBtn.style.fontWeight = "bold";
                addBtn.style.transition = "all 0.2s";
                
                // 创建删除按钮
                const removeBtn = document.createElement("button");
                removeBtn.innerHTML = "➖ 删除接口";
                removeBtn.title = "删除最后一个文本输入接口";
                removeBtn.style.padding = "6px 12px";
                removeBtn.style.border = "1px solid #ff6b6b";
                removeBtn.style.borderRadius = "4px";
                removeBtn.style.backgroundColor = "#8a2a2a";
                removeBtn.style.color = "#fff";
                removeBtn.style.cursor = "pointer";
                removeBtn.style.fontSize = "12px";
                removeBtn.style.fontWeight = "bold";
                removeBtn.style.transition = "all 0.2s";
                
                // 创建计数显示
                const countDisplay = document.createElement("span");
                countDisplay.style.fontSize = "12px";
                countDisplay.style.color = "#aaa";
                countDisplay.style.minWidth = "40px";
                countDisplay.style.textAlign = "center";
                countDisplay.textContent = "0";
                
                // 鼠标悬停效果 - 添加按钮
                addBtn.addEventListener("mouseenter", () => {
                    addBtn.style.backgroundColor = "#3a7aba";
                    addBtn.style.transform = "scale(1.02)";
                });
                addBtn.addEventListener("mouseleave", () => {
                    addBtn.style.backgroundColor = "#2a5a8a";
                    addBtn.style.transform = "scale(1)";
                });
                
                // 鼠标悬停效果 - 删除按钮
                removeBtn.addEventListener("mouseenter", () => {
                    removeBtn.style.backgroundColor = "#aa3a3a";
                    removeBtn.style.transform = "scale(1.02)";
                });
                removeBtn.addEventListener("mouseleave", () => {
                    removeBtn.style.backgroundColor = "#8a2a2a";
                    removeBtn.style.transform = "scale(1)";
                });
                
                // 更新按钮状态
                const updateButtonStates = () => {
                    // 更新计数显示
                    countDisplay.textContent = `${this.textInputCounter}`;
                    
                    // 删除按钮状态
                    if (this.textInputCounter <= 0) {
                        removeBtn.style.opacity = "0.5";
                        removeBtn.style.cursor = "not-allowed";
                        removeBtn.disabled = true;
                    } else {
                        removeBtn.style.opacity = "1";
                        removeBtn.style.cursor = "pointer";
                        removeBtn.disabled = false;
                    }
                };
                
                // 添加输入接口
                const addTextInput = () => {
                    this.textInputCounter++;
                    const inputName = `文本${this.textInputCounter}`;
                    this.addInput(inputName, "STRING");
                    updateButtonStates();
                    this.setSize([this.size[0], this.computeSize()[1]]);
                    this.setDirtyCanvas(true);
                    app.graph.setDirtyCanvas(true, true);
                };
                
                // 删除输入接口
                const removeTextInput = () => {
                    if (this.textInputCounter > 0) {
                        const inputName = `文本${this.textInputCounter}`;
                        const inputIndex = this.findInputSlot(inputName);
                        if (inputIndex !== -1) {
                            this.removeInput(inputIndex);
                        }
                        this.textInputCounter--;
                        updateButtonStates();
                        this.setSize([this.size[0], this.computeSize()[1]]);
                        this.setDirtyCanvas(true);
                        app.graph.setDirtyCanvas(true, true);
                    }
                };
                
                // 添加按钮点击事件
                addBtn.addEventListener("click", addTextInput);
                
                // 删除按钮点击事件
                removeBtn.addEventListener("click", removeTextInput);
                
                // 组装按钮容器
                buttonContainer.appendChild(removeBtn);
                buttonContainer.appendChild(countDisplay);
                buttonContainer.appendChild(addBtn);
                
                // 添加DOM组件到节点
                this.addDOMWidget("dynamic_text_controls", "controls", buttonContainer, {
                    serialize: false,
                    hideOnZoom: false,
                });
                
                // 初始化按钮状态
                updateButtonStates();
                
                // 保存函数引用以便后续使用
                this._updateButtonStates = updateButtonStates;
                this._addTextInput = addTextInput;
                
                // 默认添加一个输入接口
                addTextInput();
                
                // 调整节点大小
                setTimeout(() => {
                    this.setSize([this.size[0], this.computeSize()[1]]);
                }, 10);
                
                return result;
            };
            
            // 序列化时保存输入数量
            const onSerialize = nodeType.prototype.onSerialize;
            nodeType.prototype.onSerialize = function(o) {
                if (onSerialize) {
                    onSerialize.apply(this, arguments);
                }
                o.textInputCounter = this.textInputCounter || 1;
            };
            
            // 反序列化时恢复输入接口
            const onConfigure = nodeType.prototype.onConfigure;
            nodeType.prototype.onConfigure = function(o) {
                if (onConfigure) {
                    onConfigure.apply(this, arguments);
                }
                
                // 恢复输入计数器
                if (o.textInputCounter !== undefined) {
                    // 计算当前已有的文本输入数量
                    let currentCount = 0;
                    if (this.inputs) {
                        for (const input of this.inputs) {
                            if (input.name && input.name.startsWith("文本")) {
                                currentCount++;
                            }
                        }
                    }
                    this.textInputCounter = currentCount;
                    
                    // 延迟更新按钮状态
                    setTimeout(() => {
                        if (this._updateButtonStates) {
                            this._updateButtonStates();
                        }
                    }, 100);
                }
            };
        }
    },
});
