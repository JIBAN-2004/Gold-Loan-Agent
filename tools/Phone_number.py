from langchain_core.tools import tool
from tools.retry_limit import check_and_increment_retry, reset_retry

# LOG ADDED
from utils.logger import logger


@tool("collect_phone_number")
def phone_number_tool(number: str, thread_id: str):
    """
    Collect the user's phone number.
    """

    # LOG ADDED
    logger.info(f"[thread_id={thread_id}] TOOL_START collect_phone_number")
    logger.debug(f"[thread_id={thread_id}] Raw input number='{number}'")

    retry_key = "phone_number"

    # LOG ADDED
    logger.debug(f"[thread_id={thread_id}] Checking retry for key='{retry_key}'")
    check_and_increment_retry(thread_id, retry_key)

    if not number.isdigit() or len(number) != 10:
        # LOG ADDED
        logger.warning(
            f"[thread_id={thread_id}] Invalid phone number received: '{number}'"
        )

        return {
            "status": "error",
            "message": "Phone number must be 10 digits."
        }
    
    reset_retry(thread_id, retry_key)

    # LOG ADDED
    logger.debug(
        f"[thread_id={thread_id}] Retry reset for key='{retry_key}'"
    )
    
    print("Phone number collected:", number)

    # LOG ADDED
    logger.info(
        f"[thread_id={thread_id}] TOOL_SUCCESS collect_phone_number → next_action=send_otp_tool"
    )

    return {
        "status": "success",
        "phone_number": number,
        "next_action": "send_otp_tool"
    }
