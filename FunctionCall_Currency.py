import requests
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
EXCHANGERATE_API_KEY = os.getenv("EXCHANGERATE_API_KEY_Y")


def get_exchange_rate(base_currency: str, target_currency: str) -> float:
    """Fetches the exchange rate from the API."""
    url = f"https://api.exchangeratesapi.io/v1/latest?access_key={EXCHANGERATE_API_KEY}&symbols={base_currency},{target_currency}"

    try:
        response = requests.get(url)
        #response.raise_for_status()
        if response.status_code == 200:
            data = response.json()
            # Check if both base_currency and target_currency exist in the response data
            if "rates" in data:
                if base_currency in data["rates"] and target_currency in data["rates"]:
                    return data["rates"][target_currency] / data["rates"][base_currency]
            else:
                print("Failed to get exchange rates. Status code:", response.status_code)

    except Exception as e:
        # Handle network issues or other API call errors
        print(f"Error fetching exchange rate: {e}")



def convert_currency(amount: float, base_currency: str, target_currency: str) -> str:
    """Converts the amount from base_currency to target_currency."""
    rate = get_exchange_rate(base_currency, target_currency)
    if rate is not None:
        converted_amount = amount * rate
        return f"The converted amount is: {converted_amount:.2f} {target_currency}"
    else:
        return f"Invalid currency codes: {base_currency} or {target_currency}. Please check your input."


# Define the tool functions
house_fns = [convert_currency]

# Initialize the Generative Model
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash", tools=house_fns)

# Start a chat session
chat = model.start_chat()


user_input = input("Please enter your query for currency exchange: ")

# Provide context about the available tool
prompt = f"""
I can help you convert amounts between different currencies using the 'convert_currency' tool.

To use this tool, please follow one of these formats:
- '<amount> <base_currency> to <target_currency>' (e.g., '100 USD to INR' to convert 100 USD to INR).
- '<base_currency> to <target_currency>' (e.g., 'USD to INR' to convert 1 USD to INR by default).

Make sure to use valid three-letter currency codes (e.g., USD for US Dollar, EUR for Euro, INR for Indian Rupee).

{user_input}
"""

# Send the prompt to the Generative AI model
response = chat.send_message(prompt)

# Process the response
for part in response.parts:
    if part.text:
        print(part.text)
    if fn := part.function_call:
        # Extract arguments (target_currency, base_currency, and amount)
        target_currency = fn.args.get("target_currency")
        amount = float(fn.args.get("amount"))
        base_currency = fn.args.get("base_currency")

        # Automatically call the function and integrate the result
        result = convert_currency(amount, base_currency, target_currency)
        print(result)
