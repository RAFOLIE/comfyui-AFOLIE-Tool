"""
AFOLIE 动态文本接口节点（V3 API）
支持动态增减文本输入接口的节点
"""

from comfy_api.latest import io


class AFOLIEDynamicText(io.ComfyNode):
    """动态文本接口节点 - 支持动态增减文本输入接口，合并输出"""

    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="AFOLIE动态文本接口",
            display_name="动态文本接口 📝",
            category="AFOLIE/文本",
            description="支持动态增减文本输入接口，合并输出。支持多种合并方式：直接拼接、换行符分隔、空格分隔、逗号分隔、自定义分隔符",
            inputs=[
                io.Combo.Input("合并方式", options=[
                    "直接拼接",
                    "换行符分隔",
                    "空格分隔",
                    "逗号分隔",
                    "自定义分隔符"
                ]),
                io.String.Input("自定义分隔符", default="|", multiline=False),
            ],
            outputs=[
                io.String.Output("合并文本"),
            ],
        )

    @classmethod
    def execute(cls, 合并方式, 自定义分隔符="|", **kwargs):
        # 收集所有非空文本
        text_inputs = []
        for key, value in kwargs.items():
            if key.startswith("文本"):
                try:
                    num = int(key.replace("文本", ""))
                    text_inputs.append((num, value))
                except ValueError:
                    continue

        # 按数字排序
        text_inputs.sort(key=lambda x: x[0])

        # 收集非空文本
        texts = []
        for _, text in text_inputs:
            if text is not None and str(text).strip():
                texts.append(str(text).strip())

        if not texts:
            return io.NodeOutput("")

        # 根据合并方式选择分隔符
        separator_map = {
            "直接拼接": "",
            "换行符分隔": "\n",
            "空格分隔": " ",
            "逗号分隔": ", ",
            "自定义分隔符": 自定义分隔符
        }

        separator = separator_map.get(合并方式, "")
        result = separator.join(texts)

        return io.NodeOutput(result)
