from config import get_model

from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from google.adk.code_executors import BuiltInCodeExecutor

def get_fee_for_payment_method(method: str) -> dict:
    """Looks up the transaction fee percentage for a given payment method.

    Args:
        method: The name of the payment method, e.g. 'platinum credit card' or 'bank transfer'.

    Returns:
        Success: {"status": "success", "fee_percentage": 0.02}
        Error: {"status": "error", "error_message": "Payment method not found"}
    """
    fee_database = {
        "platinum credit card": 0.02,
        "gold debit card": 0.035,
        "bank transfer": 0.01,
    }
    fee = fee_database.get(method.lower())
    if fee is not None:
        return {"status": "success", "fee_percentage": fee}
    else:
        return {"status": "error", "error_message": f"Payment method '{method}' not found"}


def get_exchange_rate(base_currency: str, target_currency: str) -> dict:
    """Looks up and returns the exchange rate between two currencies.

    Args:
        base_currency: ISO 4217 code you are converting from (e.g. 'USD').
        target_currency: ISO 4217 code you are converting to (e.g. 'EUR').

    Returns:
        Success: {"status": "success", "rate": 0.93}
        Error: {"status": "error", "error_message": "Unsupported currency pair"}
    """
    rate_database = {
        "usd": {"eur": 0.93, "jpy": 157.50, "inr": 83.58}
    }
    rate = rate_database.get(base_currency.lower(), {}).get(target_currency.lower())
    if rate is not None:
        return {"status": "success", "rate": rate}
    else:
        return {"status": "error", "error_message": f"Unsupported currency pair: {base_currency}/{target_currency}"}


calculation_agent = LlmAgent(
    name="CalculationAgent",
    model=get_model(),
    instruction="""You are a specialized calculator that ONLY responds with Python code.

RULES:
1. Your output MUST be ONLY a Python code block.
2. Do NOT write any text before or after the code block.
3. The Python code MUST calculate the result.
4. The Python code MUST print the final result to stdout.
5. You are PROHIBITED from performing the calculation yourself.
""",
    code_executor=BuiltInCodeExecutor(),
)


root_agent = LlmAgent(
    name="enhanced_currency_agent",
    model=get_model(),
    instruction="""You are a smart currency conversion assistant.

For any currency conversion request, follow these steps IN ORDER:

1. Call get_fee_for_payment_method() to get the transaction fee
2. Call get_exchange_rate() to get the conversion rate
3. Check "status" in each response — if "error", stop and explain the issue
4. YOU MUST call the CalculationAgent tool to do ALL math. 
   NEVER write arithmetic yourself. NEVER compute expressions like '500 * 0.02'.
   Instead, describe the calculation in plain English to CalculationAgent, e.g.:
   "Calculate: 500 USD with a 2% fee, then convert remaining amount at rate 0.93"
5. Use CalculationAgent's result to provide a breakdown showing:
   - Final converted amount
   - Fee percentage and its value in the original currency
   - Amount remaining after the fee
   - Exchange rate applied

CRITICAL: If you perform any arithmetic yourself instead of using CalculationAgent, you have failed.
""",
    tools=[
        get_fee_for_payment_method,
        get_exchange_rate,
        AgentTool(agent=calculation_agent),
    ],
)