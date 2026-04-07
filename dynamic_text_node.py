"""
AFOLIE 动态文本接口节点 - 支持动态增减文本输入接口的节点
"""


class AFOLIE动态文本接口:
    """
    动态文本接口节点
    支持动态增减文本输入接口，合并输出
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "合并方式": ([
                    "直接拼接",
                    "换行符分隔",
                    "空格分隔",
                    "逗号分隔",
                    "自定义分隔符"
                ],),
                "自定义分隔符": ("STRING", {
                    "default": "|",
                    "multiline": False,
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("合并文本",)
    FUNCTION = "merge_text"
    CATEGORY = "AFOLIE/文本"
    
    DESCRIPTION = """
    动态文本接口节点
    
    功能：
    • 支持动态增减文本输入接口
    • 多种合并方式可选
    • 支持自定义分隔符
    • 自动过滤空文本
    
    使用场景：
    • 合并多个提示词
    • 组合多段描述文本
    • 批量文本处理
    """

    def merge_text(self, 合并方式, 自定义分隔符="|", **kwargs):
        """
        合并多个文本输入
        
        Args:
            合并方式: 文本合并的方式
            自定义分隔符: 当选择自定义分隔符时使用的分隔符
            **kwargs: 动态添加的文本输入
        
        Returns:
            合并后的文本
        """
        # 收集所有非空文本（按名称排序以保持顺序）
        texts = []
        
        # 从kwargs中获取所有文本输入
        text_inputs = []
        for key, value in kwargs.items():
            if key.startswith("文本"):
                try:
                    # 提取数字部分用于排序
                    num = int(key.replace("文本", ""))
                    text_inputs.append((num, value))
                except ValueError:
                    continue
        
        # 按数字排序
        text_inputs.sort(key=lambda x: x[0])
        
        # 收集非空文本
        for _, text in text_inputs:
            if text is not None and str(text).strip():
                texts.append(str(text).strip())
        
        # 如果没有任何文本，返回空字符串
        if not texts:
            return ("",)
        
        # 根据合并方式选择分隔符
        separator_map = {
            "直接拼接": "",
            "换行符分隔": "\n",
            "空格分隔": " ",
            "逗号分隔": ", ",
            "自定义分隔符": 自定义分隔符
        }
        
        separator = separator_map.get(合并方式, "")
        
        # 合并文本
        result = separator.join(texts)
        
        return (result,)


# Node registration
NODE_CLASS_MAPPINGS = {
    "AFOLIE动态文本接口": AFOLIE动态文本接口
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AFOLIE动态文本接口": "动态文本接口 📝"
}
