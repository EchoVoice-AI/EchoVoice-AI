from typing import List, Literal
from PersonalizeAI.state import GraphState


def deployment_router(state: GraphState) -> List[Literal["FEEDBACK_LOOP", "DEPLOYMENT_QUEUE"]]:
    print("Routing to Dual Exit: Deployment Queue and Feedback Loop.")
    return ["FEEDBACK_LOOP", "DEPLOYMENT_QUEUE"]
