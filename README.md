# UglyGPT

这是一个个人项目，主要解决如何更好的使用大模型的问题。

主要议题：
1. 可以便捷的使用不同的大模型；
2. 针对大模型，增加 Index 功能，提升长期记忆的能力；
3. 针对 Index 功能，提供文本向量压缩的不同版本；
4. 提供类 LangChain 的私有知识检索能力（导入知识，形成 Index）；
5. 提供 LangChain 的 Chain 功能，是模型基础的输入输出模块模板；
    1. 提供自然预言生成适合的 API 调用能力；
    2. 提供自然语言生成适合的 bash 调用能力；
    4. 提供自然语言生成适合的基于 Python 的数学计算能力；
6. 提供类 BaByAGI 的自动新任务生成能力；
7. 提供 Agent 来调用 Tool 自动选择工具并完成任务的能力（ReAct），工具包括不限于：
    1. Bing 搜索；
    2. 高德地图检索；
    3. Arxiv 论文检索；
    4. Shell 的执行能力；
    5. SQL 的执行能力；
    6. 询问 Human 的能力；
    7. 调用其他 Chain 作为工具；
8. 提供类似于 MapReduce 的对长文本分段分析的能力，解决 token 限制；