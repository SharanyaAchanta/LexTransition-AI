import time
import requests


class AITimeoutError(Exception):
    pass


def execute_with_timeout_retry(request_func, retries=2, timeout=15):
    attempt = 0

    while attempt <= retries:
        try:
            return request_func(timeout)

        except requests.exceptions.Timeout:
            attempt += 1
            if attempt > retries:
                raise AITimeoutError(
                    "AI service timed out after multiple attempts."
                )
            time.sleep(2)
