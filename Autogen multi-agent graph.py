
"""
Multi-Agent Stack (AutoGen)
---------------------------

Architecture:
- Agent A: Interpreter / Planner (API connection 1)
- Agent B: Executor / Specialist (API connection 2)
- Agent C: Critic / Validator (API connection 3)
- GroupChatManager: Orchestrates the multi-agent graph

This file is intentionally monolithic for easy modification.
"""

import autogen

# ============================================================
# 1. LLM CONFIGS (SEPARATE API CONNECTIONS)
# ============================================================

llm_config_a = {
    "model": "gpt-4.1-mini",
    "temperature": 0,
}

llm_config_b = {
    "model": "gpt-4.1-mini",
    "temperature": 0.7,
}

llm_config_c = {
    "model": "gpt-4.1-mini",
    "temperature": 0,
}

# ============================================================
# 2. AGENT DEFINITIONS
# ============================================================

# -------- Agent A: Interpreter / Planner --------
agent_a = autogen.AssistantAgent(
    name="Agent_A_Interpreter",
    system_message="""
You are Agent A, an interpreter and planner.

Responsibilities:
- Analyze the user's request
- Determine task type and intent
- Produce a structured instruction for a specialist agent

Output STRICT JSON with:
{
  "task_type": "...",
  "description": "...",
  "constraints": "...",
  "input_data": "..."
}

Do not add commentary outside the JSON.
""",
    llm_config=llm_config_a,
)

# -------- Agent B: Executor / Specialist --------
agent_b = autogen.AssistantAgent(
    name="Agent_B_Executor",
    system_message="""
You are Agent B, a specialist executor.

You receive structured instructions from Agent A.
Rules:
- Do NOT reinterpret the task
- Follow the instruction exactly
- Produce the final output only
""",
    llm_config=llm_config_b,
)

# -------- Agent C: Critic / Validator --------
agent_c = autogen.AssistantAgent(
    name="Agent_C_Critic",
    system_message="""
You are Agent C, a critic and validator.

Evaluate the executor's output.
Reply with exactly one of the following:

PASS

or

FAIL: <short reason>
""",
    llm_config=llm_config_c,
)

# ============================================================
# 3. TERMINATION LOGIC (GRAPH CONTROL)
# ============================================================

def critic_termination(message):
    """
    Stop the graph if the critic approves the result.
    """
    content = message.get("content", "")
    return content.strip().startswith("PASS")

agent_c.is_termination_msg = critic_termination

# ============================================================
# 4. GROUP CHAT (MULTI-AGENT GRAPH)
# ============================================================

groupchat = autogen.GroupChat(
    agents=[agent_a, agent_b, agent_c],
    messages=[],
    max_round=8,
)

manager = autogen.GroupChatManager(
    groupchat=groupchat,
    llm_config=llm_config_a,  # lightweight manager
)

# ============================================================
# 5. USER PROXY (ENTRY POINT)
# ============================================================

user_proxy = autogen.UserProxyAgent(
    name="User",
    human_input_mode="NEVER",
    code_execution_config=False,
)

# ============================================================
# 6. MAIN EXECUTION
# ============================================================

def run_stack(user_prompt: str):
    """
    Entry point for the multi-agent stack.
    """
    user_proxy.initiate_chat(
        manager,
        message=user_prompt,
    )

if __name__ == "__main__":
    run_stack(
        "Create a surreal image concept of a floating glass city at sunset."
    )
