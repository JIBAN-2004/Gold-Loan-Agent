from langchain_core.tools import tool
from utils.logger import logger

HARD_CODED_OTP = "654321"
MAX_RETRIES = 2

OTP_RETRY_STORE = {}

@tool("send_otp")
def send_otp_tool(phone_number: str) -> str:
    """
    Fake OTP sender (DEV MODE).
    OTP is always 654321.
    Resets retry count.
    """

    # LOG ADDED
    logger.info(f"TOOL_START send_otp | phone_number={phone_number}")

    OTP_RETRY_STORE[phone_number] = 0

    # LOG ADDED
    logger.debug(
        f"OTP retry counter reset for phone_number={phone_number}"
    )

    print(f"OTP sent to {phone_number}: {HARD_CODED_OTP}")

    # LOG ADDED
    logger.info(
        f"TOOL_SUCCESS send_otp | next_action=verify_otp_tool"
    )

    return {
        "status": "success",
        "message": "OTP has been sent to your registered mobile number.",
        "next_action": "verify_otp_tool"
    }


@tool("verify_otp")
def verify_otp_tool(phone_number: str, otp: str) -> str:
    """
    OTP verification with max 3 retries.
    """

    # LOG ADDED
    logger.info(f"TOOL_START verify_otp | phone_number={phone_number}")
    logger.debug(f"Received OTP='{otp}'")

    # Initialize retry counter if missing
    if phone_number not in OTP_RETRY_STORE:

        # LOG ADDED
        logger.warning(f"Retry store missing for phone_number={phone_number}, initializing")

        OTP_RETRY_STORE[phone_number] = 0

    # Too many attempts
    if OTP_RETRY_STORE[phone_number] >= MAX_RETRIES:

        # LOG ADDED
        logger.error(f"OTP blocked | phone_number={phone_number} | retries={OTP_RETRY_STORE[phone_number]}")

        return {
            "status": "error", 
            "message": "OTP failed 3 times. Please request a new OTP."
        }

    # Wrong OTP
    if otp != HARD_CODED_OTP:
        OTP_RETRY_STORE[phone_number] += 1
        remaining = MAX_RETRIES - OTP_RETRY_STORE[phone_number]

        #LOG ADDED
        logger.warning(
            f"Incorrect OTP | phone_number={phone_number} | "
            f"attempts_used={OTP_RETRY_STORE[phone_number]} | "
            f"remaining={remaining}"
        )

        return {
            "status": "error",
            "message": f"Incorrect OTP. You have {remaining} attempts left."
        }

    # Correct OTP → clear retries
    del OTP_RETRY_STORE[phone_number]

    # 🔹 LOG ADDED
    logger.info(f"OTP verified successfully | phone_number={phone_number} | next_action=father_name_tool")

    return {
        "status": "success", 
        "message": "OTP verified successfully.",
        "next_action": "father_name_tool"
    }