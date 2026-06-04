from config import get_model

from google.adk.agents import LlmAgent

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


root_agent = LlmAgent(
    name="currency_agent",
    model=get_model(),
    instruction="""You are a smart currency conversion assistant.

For currency conversion requests:
1. Use get_fee_for_payment_method() to find transaction fees
2. Use get_exchange_rate() to get currency conversion rates
3. Check the "status" field in each tool's response for errors
4. Calculate the final amount after fees and provide a clear breakdown:
   - Final converted amount
   - Fee percentage and its value in the original currency
   - Amount remaining after the fee
   - Exchange rate used

If any tool returns status "error", explain the issue clearly.
""",
    tools=[get_fee_for_payment_method, get_exchange_rate],
)