from langchain_core.tools import tool
from tools.retry_limit import check_and_increment_retry, reset_retry
from utils.logger import logger

@tool("collect_full_name")
def full_name_tool(name: str, thread_id: str):
    """
    Collect the user's full name (first name + last name required).
    """

    # LOG ADDED
    logger.info(f"[thread_id={thread_id}] TOOL_START collect_full_name")
    logger.debug(f"[thread_id={thread_id}] Raw input name='{name}'")

    retry_key = "full_name"

    # LOG ADDED
    logger.debug(f"[thread_id={thread_id}] Checking retry for key='{retry_key}'")

    check_and_increment_retry(thread_id, retry_key)

    name = name.strip()
    parts = [p for p in name.split(" ") if p]

    # LOG ADDED
    logger.debug(
        f"[thread_id={thread_id}] Parsed name parts={parts} (count={len(parts)})"
    )

    if len(parts) < 2:
        return {
            "status": "error",
            "message": "Please enter both first name and last name."
        }

    full_name = " ".join(parts)

    # LOG ADDED
    logger.info(
        f"[thread_id={thread_id}] Full name validated successfully: '{full_name}'"
    )

    reset_retry(thread_id, retry_key)

    # LOG ADDED
    logger.debug(
        f"[thread_id={thread_id}] Retry reset for key='{retry_key}'"
    )

    print("Full name collected:", full_name)
    return {
        "status": "success",
        "full_name": full_name,
        "first_name": parts[0],
        "next_action":"phone_number_tool"
    }

    