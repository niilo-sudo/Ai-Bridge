from openai import OpenAI

[Basics]

class Agent:
    def __init__(self, name, system_prompt, model="gpt-4.1-mini"):
        self.name = name
        self.system_prompt = system_prompt
        self.model = model
        self.client = OpenAI()

    def run(self, input_message):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": input_message}
            ]
        )
        return response.choices[0].message.content

;Roles

agent_a = Agent(
    name="Agent A",
    system_prompt="""
You are Agent A, an interpreter and router.
Analyze the input and output a structured task description.
Use JSON only.
"""
)
agent_b = Agent(
    name="Agent B",
    system_prompt="""
You are Agent B, a specialist executor.
Follow the structured task exactly.
Produce the final output only.
"""
)
agent_c = Agent(
    name="Agent C",
    system_prompt="""
You are Agent C, a critic.
Evaluate the result and say PASS or FAIL with a reason.
"""
)

;Orchestrator

class AgentStack:
    def __init__(self, agents):
        self.agents = agents

    def run(self, user_input):
        state = {}

        # Step 1: Interpretation
        instruction = self.agents["A"].run(user_input)
        state["instruction"] = instruction

        # Step 2: Execution
        result = self.agents["B"].run(instruction)
        state["result"] = result

        # Step 3: Critique
        critique = self.agents["C"].run(result)
        state["critique"] = critique

        # Optional loop
        if "FAIL" in critique:
            improved = self.agents["B"].run(
                instruction + "\nImprove based on critique:\n" + critique
            )
            state["result"] = improved

        return state

;Complete Stack

stack = AgentStack(
    agents={
        "A": agent_a,  # API connection 1
        "B": agent_b,  # API connection 2
        "C": agent_c   # API connection 3
    }
)

output = stack.run(
    "Generate a surreal image prompt of a floating city made of glass."
)

print(output)
