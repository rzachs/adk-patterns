from dotenv import load_dotenv
load_dotenv()

from config import get_model

from google.adk.agents import LlmAgent
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.tool_context import ToolContext

LARGE_ORDER_THRESHOLD = 5

def place_shipping_order(num_containers: int, destination: str, tool_context: ToolContext) -> dict:
    """Places a shipping order. Requires approval if ordering more than 5 containers.

    Args:
        num_containers: Number of containers to ship
        destination: Shipping destination

    Returns:
        Dictionary with order status
    """
    # Small orders: auto-approve
    if num_containers <= LARGE_ORDER_THRESHOLD:
        return {
            "status": "approved",
            "order_id": f"ORD-{num_containers}-AUTO",
            "num_containers": num_containers,
            "destination": destination,
            "message": f"Order auto-approved: {num_containers} containers to {destination}",
        }

    # Large order - first call: request human approval
    if not tool_context.tool_confirmation:
        tool_context.request_confirmation(
            hint=f"Large order: {num_containers} containers to {destination}. Approve?",
            payload={"num_containers": num_containers, "destination": destination},
        )
        return {
            "status": "pending",
            "message": f"Order for {num_containers} containers requires approval",
        }

    # Large order - resumed: handle decision
    if tool_context.tool_confirmation.confirmed:
        return {
            "status": "approved",
            "order_id": f"ORD-{num_containers}-HUMAN",
            "num_containers": num_containers,
            "destination": destination,
            "message": f"Order approved: {num_containers} containers to {destination}",
        }
    else:
        return {
            "status": "rejected",
            "message": f"Order rejected: {num_containers} containers to {destination}",
        }


shipping_agent = LlmAgent(
    name="shipping_agent",
    model=get_model(),
    instruction="""You are a shipping coordinator assistant.

When users request to ship containers:
1. Use the place_shipping_order tool with the number of containers and destination
2. If the order status is 'pending', inform the user that approval is required
3. After receiving the final result, provide a clear summary including:
   - Order status (approved/rejected)
   - Order ID (if available)
   - Number of containers and destination
4. Keep responses concise but informative
""",
    tools=[FunctionTool(func=place_shipping_order)],
)