from loguru import logger

from mobile_world.runtime.controller import AndroidController
from mobile_world.tasks.base import BaseTask


class CheckConferenceDurationTask(BaseTask):
    """Check how many days of conference meetings were scheduled in October."""

    goal = "How many days of conference meetings did I schedule in October?"
    correct_answer = "12"

    task_tags = {"lang-en"}

    app_names = {
        "Calendar",
    }

    def initialize_task_hook(self, controller: AndroidController) -> bool:
        self.relevant_information = "I always schedule conference meetings in the Calendar app."
        return True

    def is_successful(self, controller: AndroidController) -> float | tuple[float, str]:
        self._check_is_initialized()

        answer = controller.interaction_cache

        if self.correct_answer in str(answer):
            logger.info(f"Correct answer found: {answer}")
            return 1.0, "Success"
        else:
            logger.info(f"Incorrect answer: {answer}")
            return 0.0, f"Incorrect answer {answer}, expected {self.correct_answer}"
