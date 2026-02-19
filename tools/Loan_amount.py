from langchain_core.tools import tool
from tools.retry_limit import check_and_increment_retry, reset_retry
from utils.logger import logger


@tool("collect_loan_amount")
def loan_amount_tool(amount: str, thread_id: str):
    """
    Collect the loan amount requested by the user.
    """

    # LOG ADDED
    logger.info(f"[thread_id={thread_id}] TOOL_START collect_loan_amount")
    logger.debug(f"[thread_id={thread_id}] Raw input amount='{amount}'")

    retry_key = "loan_amount"

    # LOG ADDED
    logger.debug(f"[thread_id={thread_id}] Checking retry for key='{retry_key}'")
    check_and_increment_retry(thread_id, retry_key)

    if not amount.isdigit():
        # LOG ADDED
        logger.warning(
            f"[thread_id={thread_id}] Non-numeric loan amount received: '{amount}'"
        )

        return {
            "status": "error",
            "message": "Loan amount must be numeric."
        }
    
    amt = int(amount)

    # LOG ADDED
    logger.debug(
        f"[thread_id={thread_id}] Parsed loan amount={amt}"
    )

    if amt < 10000 or amt > 10000000:
        # LOG ADDED
        logger.warning(
            f"[thread_id={thread_id}] Loan amount out of range: {amt}"
        )

        return {
            "status": "error",
            "message": "Loan amount must be between 10,000 and 1,00,00,000."
        }
    
    reset_retry(thread_id, retry_key)

    # LOG ADDED
    logger.debug(
        f"[thread_id={thread_id}] Retry reset for key='{retry_key}'"
    )

    print("Loan amount collected:", amt)

    # LOG ADDED
    logger.info(
        f"[thread_id={thread_id}] TOOL_SUCCESS collect_loan_amount → next_action=loan_type_tool"
    )

    return {
        "status": "success",
        "loan_amount": amt,
        "next_action": "loan_type_tool"
    }
