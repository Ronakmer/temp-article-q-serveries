import requests
import os
import time
import json
import uuid
from app.workers.core.article_innovator_api_call.api_client.api_client import APIClient

# class CalculatePriority:
#     def __init__(self):
#         self.api_client = APIClient()

#     def calculate_priority(self, base_priority, data_type: str):
#         DATA_WEIGHTS = {
#             'content_message': 1,
#             'retry_content_message': 2,
#             'category': 3,
#             'tag': 3,
#             'author': 3,
#             'primary_keyword': 4
#         }

#         base_priority = base_priority or 0  # default to 0 if None

#         return base_priority + DATA_WEIGHTS.get(data_type, 0)

#         # calculate_priority(12,'category')









class CalculatePriority:
    DATA_WEIGHTS = {
        'content_message': 1,
        'retry_content_message': 2,
        'retry_category': 2,
        'retry_tag': 2,
        'retry_author': 2,
        'category': 3,
        'tag': 3,
        'author': 3,
        'primary_keyword': 4,
    }

    def calculate_priority(self, base_priority, data_type: str) -> int:
        """
        Forward calculation:
        final_priority = base_priority + weight(data_type).
        """
        try:
            base = int(base_priority) if base_priority is not None else 0
        except (TypeError, ValueError):
            base = 0

        return base + self.DATA_WEIGHTS.get(data_type, 0)

    def extract_base_priority(self, final_priority, data_type: str) -> int:
        """
        Reverse calculation:
        base_priority = final_priority - weight(data_type).
        Ensures result is non-negative.
        """
        try:
            final_val = int(final_priority)
        except (TypeError, ValueError):
            final_val = 0

        weight = self.DATA_WEIGHTS.get(data_type, 0)
        base = final_val - weight
        return base if base >= 0 else 0


# if __name__ == "__main__":
#     calc = CalculatePriority()
#     print(calc.calculate_priority(100, 'category'))       # → 103
#     print(calc.extract_base_priority(103, 'category'))    # → 98
