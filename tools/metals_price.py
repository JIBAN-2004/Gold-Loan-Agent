import os
import requests
from langchain_core.tools import tool

from dotenv import load_dotenv
load_dotenv()

from utils.logger import logger


GOLD_API_KEY = os.getenv("GOLD_API_KEY")


@tool("collect_metals_price")
def metals_price_tool(metal: str = "gold") -> str:
    """
    Fetch current gold or silver price using GoldAPI.
    Returns price per gram and per ounce in USD.
    """

    # LOG ADDED
    logger.info(f"TOOL_START collect_metals_price | metal='{metal}'")

    metal = metal.lower().strip()

    # LOG ADDED
    logger.debug(f"Normalized metal='{metal}'")

    symbol_map = {
        "gold": "XAU",
        "silver": "XAG"
    }

    if metal not in symbol_map:
        # LOG ADDED
        logger.warning(
            f"Unsupported metal requested: '{metal}'"
        )

        return {
            "status": "error",
            "message": "❌ Supported metals are gold and silver only."
        }

    try:
        url = f"https://www.goldapi.io/api/{symbol_map[metal]}/INR"
        headers = {
            "x-access-token": GOLD_API_KEY,
            "Content-Type": "application/json"
        }

        # LOG ADDED
        logger.debug(f"Calling GoldAPI | url={url}")

        response = requests.get(url, headers=headers, timeout=5)

        # LOG ADDED
        logger.debug(
            f"GoldAPI response status_code={response.status_code}"
        )

        data = response.json()

        # LOG ADDED
        logger.debug(
            f"GoldAPI response payload keys={list(data.keys())}"
        )

        if "price" not in data:
            # LOG ADDED
            logger.error(
                f"Price not found in GoldAPI response: {data}"
            )

            return {
                "status": "error",
                "message": "⚠️ Unable to fetch metal price right now."
            }

        price_per_ounce = data["price"]
        price_per_gram = round(price_per_ounce / 31.1035, 2)
        price_per_decagram = round(price_per_gram * 10, 2)

        # LOG ADDED
        logger.info(
            f"Metal price fetched successfully | metal={metal} | "
            f"per_gram={price_per_gram} INR"
        )

        return {
            "status": "success",
            "message": (
                f"📊 Current {metal.capitalize()} Price:\n"
                f"• INR {price_per_gram} per gram\n"
                f"• INR {price_per_decagram} per decagram"
            ),
            "next_action": "loan completion message"
        }

    except Exception as e:
        # LOG ADDED
        logger.error(
            "Exception while fetching metal prices",
            exc_info=True
        )

        return {
            "status": "error",
            "message": "⚠️ Error while fetching metal prices."
        }
