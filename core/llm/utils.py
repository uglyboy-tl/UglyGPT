from typing import Any, Callable, TypeVar

from loguru import logger
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_random_exponential,
    before_sleep_log,
)

from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

def retry_decorator(not_notry_exception:Callable[[BaseException],bool] = lambda x:False, max_retries:int = 6) -> Callable[[Any], Any]:
    min_seconds = 5
    max_seconds = 60
    return retry(
        reraise=True,
        stop=stop_after_attempt(max_retries),
        retry=retry_if_exception(not_notry_exception),
        wait=wait_random_exponential(min=min_seconds, max=max_seconds),
        before_sleep=before_sleep_log(logger, "WARNING"), # type: ignore
    )