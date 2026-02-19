from langchain_core.tools import tool
from tools.retry_limit import check_and_increment_retry, reset_retry

# LOG ADDED
from utils.logger import logger


@tool("collect_loan_type")
def loan_type_tool(loan_type: str, thread_id: str):
    """
    Collect the type of loan selected by the user.
    """

    # LOG ADDED
    logger.info(f"[thread_id={thread_id}] TOOL_START collect_loan_type")
    logger.debug(f"[thread_id={thread_id}] Raw input loan_type='{loan_type}'")

    retry_key = "loan_type"

    # LOG ADDED
    logger.debug(f"[thread_id={thread_id}] Checking retry for key='{retry_key}'")
    check_and_increment_retry(thread_id, retry_key)

    allowed = ["gold", "personal", "home"]
    lt = loan_type.lower()

    # LOG ADDED
    logger.debug(
        f"[thread_id={thread_id}] Normalized loan_type='{lt}', allowed={allowed}"
    )

    if lt not in allowed:
        # LOG ADDED
        logger.error(
            f"[thread_id={thread_id}] Invalid loan type received: '{lt}'"
        )
        raise ValueError(f"Loan type must be one of {allowed}")
    
    reset_retry(thread_id, retry_key)

    # LOG ADDED
    logger.debug(
        f"[thread_id={thread_id}] Retry reset for key='{retry_key}'"
    )

    print("Loan type collected:", lt)

    # LOG ADDED
    logger.info(
        f"[thread_id={thread_id}] TOOL_SUCCESS collect_loan_type → next_action=metals_price_tool"
    )

    if lt == "gold":
        return (
            "Thank you for providing all the details. "
            "Your Gold loan application has been submitted successfully. "
            "Would you like to know the current price of gold or silver?"
        )

    return (
        f"Thank you for providing all the details. "
        f"Your {lt.capitalize()} loan application has been submitted successfully."
    )
