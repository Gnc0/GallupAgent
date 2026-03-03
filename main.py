"""Gallup Agent - 交互式对话入口（协作版）。"""
from data.themes import GALLUP_THEMES, get_theme_names, get_themes_by_domain, GallupDomain
from agent.supervisor import SupervisorAgent
from agent.worker import WorkerAgent, DEEP_DIALOGUE_PROTOCOL
from config import Config
from logger import save_conversation


class GallupAgent:
    """Gallup Agent - 支持多Agent协作。"""

    def __init__(self):
        self.supervisor = SupervisorAgent()
        self.worker = WorkerAgent()
        print(f"Gallup Agent 初始化完成，共 {len(GALLUP_THEMES)} 个主题\n")

    def chat(self, user_input: str) -> str:
        """处理对话，多Agent协作并返回统一答案。"""
        # Step 1: Supervisor分析
        result = self.supervisor.analyze(user_input)
        dsl = result.get("dsl", {})
        command = dsl.get("command")
        targets = dsl.get("target_agents", [])
        
        # 获取主题选择理由
        reasoning = result.get("user_visible_reasoning", "")

        # 处理REJECT命令 - 非问题分析类请求
        if command == "REJECT":
            reject_message = dsl.get("input_context", "抱歉，我是一个专注于问题分析的AI助手。请提出您需要分析的问题、困惑或需要建议的情况。")
            
            # 保存REJECT类型的对话记录（使用全局导入的save_conversation）
            save_conversation(
                user_input=user_input,
                response=reject_message,
                themes=[],
                reasoning=result.get("reasoning", "非问题分析类请求"),
                theme_results={},
                metadata={
                    "task": result.get("task", ""),
                    "command": "REJECT",
                    "num_themes": 0
                }
            )
            
            return reject_message

        if command == "FINISH" or not targets:
            return result.get("reasoning", "感谢您的咨询")

        # Step 2: 多Agent协作
        print(f"[协作模式] 调用 {len(targets)} 个主题: {', '.join(targets)}")
        
        # 立即显示主题选择理由
        if reasoning:
            print(f"\n【分析视角】\n{reasoning}\n")
        
        all_results = {}
        
        # 顺序执行，让后面的Agent能看到前面的结果
        for i, theme in enumerate(targets):
            context = {
                "conversation_history": "",
                "task_description": result.get("task", "")
            }
            
            # 汇总前面的结果
            if all_results:
                prev = "\n\n".join([f"【{t}】的观点:\n{r[:300]}..." for t, r in all_results.items()])
                context["conversation_history"] = f"已有观点汇总:\n{prev}\n\n请基于你的视角提供补充或不同观点。"
            
            all_results[theme] = self.worker.execute(theme, user_input, context)
            print(f"  ✓ {theme} 完成")

        # Step 3: 汇总所有观点，包含reasoning
        synthesis = self._synthesize(user_input, all_results, reasoning)
        
        # 保存对话记录
        filepath = save_conversation(
            user_input=user_input,
            response=synthesis,
            themes=targets,
            reasoning=reasoning,
            theme_results=all_results,
            metadata={
                "task": result.get("task", ""),
                "num_themes": len(targets)
            }
        )
        print(f"\n[记录已保存] {filepath}")
        
        return synthesis

    def _synthesize(self, question: str, results: dict, reasoning: str = "") -> str:
        """整合多个Agent的观点，给出统一答案。"""
        # 构建汇总prompt，包含主题名称
        summaries = []
        for theme, content in results.items():
            # 保留完整内容，不截断
            summary = f"【{theme}】{content}"
            summaries.append(summary)
        
        combined = "\n\n---\n\n".join(summaries)
        
        # 总结Agent的额外规则
        summarize_rules = """
【额外约束】
- 不要暴露你知道之前几个主题分别思考了什么（禁止如"从X视角来看"、"基于前面的分析"等表述）
- 你应该像直接给出完整答案一样，不要提及答案的来源或构建过程
- 把所有观点融合成统一连贯的答案，不要列举式地逐个介绍每个视角"""
        
        synthesis_prompt = f"""基于用户的提问「{question}」，以下是多个Gallup天赋视角的详细分析：

{combined}

请整合以上所有观点，给出一个统一、连贯、有价值的最终答案。
答案应该：
1. 综合各视角的核心观点
2. 结构清晰，重点突出
3. 对用户有实际指导意义

{DEEP_DIALOGUE_PROTOCOL}

{summarize_rules}

最终答案："""

        # 调用LLM进行整合
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.messages import HumanMessage
        
        llm = Config.get_supervisor_llm()
        prompt = ChatPromptTemplate.from_messages([
            HumanMessage(content=synthesis_prompt)
        ])
        chain = prompt | llm
        response = chain.invoke({})
        
        return response.content

    def show_help(self):
        """显示帮助。"""
        print("""
命令:
  help    - 显示帮助
  themes  - 列出所有主题
  domains - 按领域显示主题
  exit    - 退出
""")

    def show_themes(self):
        """显示所有主题。"""
        print(f"\n所有 {len(GALLUP_THEMES)} 个Gallup主题:\n")
        for i, (name, info) in enumerate(GALLUP_THEMES.items(), 1):
            print(f"  {i:2}. {name:20} - {info['name']}")

    def show_domains(self):
        """按领域显示主题。"""
        print("\n按领域分类:\n")
        for domain in GallupDomain:
            print(f"【{domain.value}】")
            themes = get_themes_by_domain(domain)
            for t in themes:
                print(f"  • {t}")
            print()


def main():
    """主函数。"""
    print("=" * 50)
    print("  Gallup Agent - 盖洛普智能体助手")
    print("=" * 50)
    print("输入 'help' 查看帮助，输入 'exit' 退出\n")

    agent = GallupAgent()

    while True:
        try:
            user_input = input("> ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() == "exit":
                print("\n再见！")
                break
            elif user_input.lower() == "help":
                agent.show_help()
            elif user_input.lower() == "themes":
                agent.show_themes()
            elif user_input.lower() == "domains":
                agent.show_domains()
            else:
                print("\n")
                response = agent.chat(user_input)
                print(response)
                print()

        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"\n错误: {e}\n")


if __name__ == "__main__":
    main()
