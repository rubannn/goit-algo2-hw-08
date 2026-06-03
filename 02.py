import random
import time
from collections import deque
from typing import Dict


class SlidingWindowRateLimiter:
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_requests = max_requests
        self.user_messages: Dict[str, deque[float]] = {}

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        user_window = self.user_messages.get(user_id)
        if user_window is None:
            return

        window_start = current_time - self.window_size
        while user_window and user_window[0] <= window_start:
            user_window.popleft()

        if not user_window:
            del self.user_messages[user_id]

    def can_send_message(self, user_id: str) -> bool:
        current_time = time.time()
        self._cleanup_window(user_id, current_time)
        user_window = self.user_messages.get(user_id, deque())
        return len(user_window) < self.max_requests

    def record_message(self, user_id: str) -> bool:
        current_time = time.time()
        self._cleanup_window(user_id, current_time)
        user_window = self.user_messages.setdefault(user_id, deque())

        if len(user_window) >= self.max_requests:
            return False

        user_window.append(current_time)
        return True

    def time_until_next_allowed(self, user_id: str) -> float:
        current_time = time.time()
        self._cleanup_window(user_id, current_time)
        user_window = self.user_messages.get(user_id)

        if not user_window or len(user_window) < self.max_requests:
            return 0.0

        oldest_message_time = user_window[0]
        wait_time = self.window_size - (current_time - oldest_message_time)
        return max(0.0, wait_time)

def view_messages(limiter, start, step, title):
    print(f"\n=== {title} ===")
    for message_id in range(start, start + step + 1):
        # Симулюємо різних користувачів (ID від 1 до 5)
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        status = "✓" if result else f"x (очікування {wait_time:.1f}s)"

        print(
            f"Повідомлення {message_id:2d} | Користувач {user_id} | {status}"
        )
        # Невелика затримка між повідомленнями для реалістичності
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))

# Демонстрація роботи
def test_rate_limiter() -> None:
    # Створюємо rate limiter: вікно 10 секунд, 1 повідомлення
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    view_messages(limiter, 1, 10, "Симуляція потоку повідомлень")

    # Чекаємо, поки вікно очиститься
    print("\nОчікуємо 4 секунди...")
    time.sleep(4)

    view_messages(limiter, 11, 10, "Нова серія повідомлень після очікування")


if __name__ == "__main__":
    test_rate_limiter()
