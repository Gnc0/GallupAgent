"""LangGraph Workflow - 工作流定义，包含节点和边。"""
from typing import TypedDict, List, Annotated, Optional, Dict
from operator import add

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from agent.supervisor import SupervisorAgent, create_supervisor
from agent.worker import WorkerAgent, create_worker
from data.themes import GALLUP_THEMES


# ==================== State Definition ====================

class AgentState(TypedDict):
    """Agent状态定义，用于在节点间传递信息。"""
    messages: List[str]                    # 对话消息历史
    user_input: str                        # 用户当前输入
    current_task: str                      # 当前任务描述
    iteration_count: int                    # 迭代计数
    active_theme: str                      # 当前激活的主题
    worker_result: str                      # Worker执行结果
    final_solution: str                     # 最终解决方案
    control_json: Dict                     # Supervisor生成的JSON控制指令
    should_continue: bool                   # 是否继续循环
    reasoning: str                          # 对用户可见的主题选择理由


# ==================== Node Functions ====================

def supervisor_node(state: AgentState) -> AgentState:
    """Supervisor节点：分析用户意图，生成控制JSON。

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    # 创建Supervisor实例
    supervisor = create_supervisor()

    # 构建上下文
    context = {}
    if state.get("messages"):
        context["conversation_history"] = "\n".join(state["messages"])
    if state.get("worker_result"):
        context["previous_results"] = state["worker_result"]

    # 分析并生成JSON
    result = supervisor.analyze(state["user_input"], context)

    # 更新状态
    state["control_json"] = result
    state["current_task"] = result.get("task", "")
    state["iteration_count"] = state.get("iteration_count", 0) + 1
    # 保存用户可见的reasoning
    state["reasoning"] = result.get("user_visible_reasoning", "")

    return state


def worker_node(state: AgentState) -> AgentState:
    """Worker节点：执行具体的Gallup主题任务。

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    control_json = state.get("control_json", {})
    dsl = control_json.get("dsl", {})

    target_agent = dsl.get("target_agent")
    input_context = dsl.get("input_context", "")

    if not target_agent:
        state["worker_result"] = "未指定目标Agent"
        return state

    # 验证主题是否有效
    if target_agent not in GALLUP_THEMES:
        state["worker_result"] = f"未知主题: {target_agent}"
        return state

    # 创建Worker实例
    worker = create_worker()

    # 构建上下文
    context = {
        "task_description": state.get("current_task", ""),
    }
    if state.get("messages"):
        context["conversation_history"] = "\n".join(state["messages"])

    # 执行任务
    result = worker.execute(target_agent, state["user_input"], context)

    # 更新状态
    state["worker_result"] = result
    state["active_theme"] = target_agent

    return state


def router_node(state: AgentState) -> str:
    """路由节点：根据control_json决定下一步走向。

    Args:
        state: 当前状态

    Returns:
        下一个节点的名称
    """
    control_json = state.get("control_json", {})
    dsl = control_json.get("dsl", {})

    command = dsl.get("command", "FINISH")

    if command == "CALL_AGENT":
        return "worker_node"
    elif command == "REJECT":
        return "reject_node"
    elif command == "FINISH":
        return "finish_node"
    else:
        return "finish_node"


def finish_node(state: AgentState) -> AgentState:
    """结束节点：生成最终答案。

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    # 收集所有Worker的结果
    messages = state.get("messages", [])
    worker_result = state.get("worker_result", "")
    reasoning = state.get("reasoning", "")

    # 构建最终输出 - 直接给用户完整回答
    # 主题选择理由直接整合到回答开头，不加标签
    if worker_result:
        # 如果有reasoning，放在开头
        if reasoning:
            final = f"{reasoning}\n\n{worker_result}"
        else:
            final = worker_result
    else:
        final = "感谢您的咨询。"

    state["final_solution"] = final
    state["should_continue"] = False

    return state


def reject_node(state: AgentState) -> AgentState:
    """拒绝节点：处理非问题分析类请求。

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    control_json = state.get("control_json", {})
    dsl = control_json.get("dsl", {})
    
    # 获取拒绝消息
    reject_message = dsl.get("input_context", "抱歉，我是一个专注于问题分析的AI助手。请提出您需要分析的问题、困惑或需要建议的情况。")
    
    state["final_solution"] = reject_message
    state["should_continue"] = False

    return state


# ==================== Graph Construction ====================

def create_graph() -> StateGraph:
    """创建LangGraph工作流。

    Returns:
        编译后的StateGraph
    """
    # 创建图
    graph = StateGraph(AgentState)

    # 添加节点
    graph.add_node("supervisor_node", supervisor_node)
    graph.add_node("worker_node", worker_node)
    graph.add_node("finish_node", finish_node)
    graph.add_node("reject_node", reject_node)

    # 设置入口点
    graph.set_entry_point("supervisor_node")

    # 添加条件边
    graph.add_conditional_edges(
        "supervisor_node",
        router_node,
        {
            "worker_node": "worker_node",
            "finish_node": "finish_node",
            "reject_node": "reject_node"
        }
    )

    # 添加循环边（worker完成后回到supervisor）
    graph.add_edge("worker_node", "supervisor_node")
    graph.add_edge("finish_node", END)
    graph.add_edge("reject_node", END)

    return graph


# 编译图
def get_compiled_graph() -> StateGraph:
    """获取编译后的图。"""
    graph = create_graph()
    return graph.compile()


# ==================== Helper Functions ====================

def run_workflow(user_input: str) -> str:
    """运行完整的工作流。

    Args:
        user_input: 用户输入

    Returns:
        最终答案
    """
    # 初始化状态
    initial_state: AgentState = {
        "messages": [],
        "user_input": user_input,
        "current_task": "",
        "iteration_count": 0,
        "active_theme": "",
        "worker_result": "",
        "final_solution": "",
        "control_json": {},
        "should_continue": True,
        "reasoning": ""
    }

    # 获取编译后的图
    compiled_graph = get_compiled_graph()

    # 运行图
    result = compiled_graph.invoke(initial_state)

    return result.get("final_solution", "")
