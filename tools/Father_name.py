from langchain_core.tools import tool
from tools.retry_limit import check_and_increment_retry, reset_retry
from utils.logger import logger


@tool("collect_father_name")
def father_name_tool(name: str, thread_id: str):
    """
    Collect the user's father's name.
    """

    # LOG ADDED
    logger.info(f"[thread_id={thread_id}] TOOL_START collect_father_name")
    logger.debug(f"[thread_id={thread_id}] Raw input name='{name}'")

    retry_key = "father_name"

    # LOG ADDED
    logger.debug(f"[thread_id={thread_id}] Checking retry for key='{retry_key}'")
    check_and_increment_retry(thread_id, retry_key)

    name = name.strip()
    parts = [p for p in name.split(" ") if p]

    # LOG ADDED
    logger.debug(
        f"[thread_id={thread_id}] Parsed father name parts={parts} (count={len(parts)})"
    )

    if len(parts) < 2:
        # LOG ADDED
        logger.warning(
            f"[thread_id={thread_id}] Invalid father name provided: '{name}'"
        )

        return {
            "status": "error",
            "message": "Please enter your first name and last name."
        }
    
    full_name = " ".join(parts)

    # LOG ADDED
    logger.info(
        f"[thread_id={thread_id}] Father name validated successfully: '{full_name}'"
    )
    
    reset_retry(thread_id, retry_key)

    # LOG ADDED
    logger.debug(
        f"[thread_id={thread_id}] Retry reset for key='{retry_key}'"
    )

    print("Father name collected:", name)

    # LOG ADDED
    logger.info(
        f"[thread_id={thread_id}] TOOL_SUCCESS collect_father_name → next_action=loan_amount_tool"
    )

    return {
        "status": "success",
        "father_name": full_name,
        "next_action": "loan_amount_tool"
    }
