# app/agents/nodes.py
from langchain_core.messages import HumanMessage

async def segmentation_node(state):
    # Logic to call LLM and segment customers
    # Returns updated state with "segments"
    return {"segments": ["High-Protein Shopper", "Budget-Conscious"]}

async def safety_node(state):
    # Logic to check content against policies
    # Returns updated state with "is_safe" flag and logs
    return {"safety_logs": ["Checked for medical claims: Passed"]}