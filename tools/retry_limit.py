MAX_RETRIES = 2
RETRY_STORE = {}

from utils.logger import logger


def check_and_increment_retry(thread_id: str, field: str):
    # LOG ADDED
    logger.debug(
        f"[thread_id={thread_id}] Retry check START | field='{field}'"
    )

    if thread_id not in RETRY_STORE:
        # LOG ADDED
        logger.debug(
            f"[thread_id={thread_id}] Initializing retry store"
        )
        RETRY_STORE[thread_id] = {}

    count = RETRY_STORE[thread_id].get(field, 0)

    # LOG ADDED
    logger.debug(
        f"[thread_id={thread_id}] Current retry count | field='{field}' | count={count}"
    )

    if count >= MAX_RETRIES:
        # LOG ADDED
        logger.error(
            f"[thread_id={thread_id}] MAX_RETRIES exceeded | field='{field}' | limit={MAX_RETRIES}"
        )
        raise ValueError("Maximum retry limit exceeded. Please restart the application.")

    RETRY_STORE[thread_id][field] = count + 1

    # LOG ADDED
    logger.info(
        f"[thread_id={thread_id}] Retry incremented | field='{field}' | new_count={count + 1}"
    )


def reset_retry(thread_id: str, field: str):
    # LOG ADDED
    logger.debug(
        f"[thread_id={thread_id}] Retry reset requested | field='{field}'"
    )

    if thread_id in RETRY_STORE:
        RETRY_STORE[thread_id].pop(field, None)

        # LOG ADDED
        logger.info(
            f"[thread_id={thread_id}] Retry reset DONE | field='{field}'"
        )


def reset_all_retries(thread_id: str):
    # LOG ADDED
    logger.info(
        f"[thread_id={thread_id}] Resetting ALL retries"
    )

    RETRY_STORE.pop(thread_id, None)
