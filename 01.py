import random
import time
from functools import lru_cache


def get_time(function):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = function(*args, **kwargs)
        elapsed_time = time.perf_counter() - start_time
        return result, elapsed_time

    return wrapper


def range_sum_no_cache(array: list[int], left: int, right: int) -> int:
    return sum(array[left : right + 1])


def update_no_cache(array: list[int], index: int, value: int) -> None:
    array[index] = value


def build_cached_range_sum(
    array: list[int],
    maxsize: int = 1000,
):
    @lru_cache(maxsize=maxsize)
    def cached_range_sum(left: int, right: int) -> int:
        return sum(array[left : right + 1])

    return cached_range_sum


def range_sum_with_cache(
    array: list[int],
    left: int,
    right: int,
    cached_range_sum,
) -> int:
    return cached_range_sum(left, right)


def update_with_cache(
    array: list[int],
    index: int,
    value: int,
    cached_range_sum,
) -> None:
    array[index] = value
    cached_range_sum.cache_clear()


def make_queries(
    n: int,
    q: int,
    hot_pool: int = 30,
    p_hot: float = 0.95,
    p_update: float = 0.03,
) -> list[tuple[str, int, int]]:
    hot = [
        (random.randint(0, n // 2), random.randint(n // 2, n - 1))
        for _ in range(hot_pool)
    ]
    queries = []
    for _ in range(q):
        if random.random() < p_update:
            idx = random.randint(0, n - 1)
            val = random.randint(1, 100)
            queries.append(("Update", idx, val))
        else:
            if random.random() < p_hot:
                left, right = random.choice(hot)
            else:
                left = random.randint(0, n - 1)
                right = random.randint(left, n - 1)
            queries.append(("Range", left, right))
    return queries


@get_time
def run_queries_without_cache(
    array: list[int],
    queries: list[tuple[str, int, int]],
) -> None:
    for query_type, first, second in queries:
        if query_type == "Range":
            range_sum_no_cache(array, first, second)
        else:
            update_no_cache(array, first, second)


@get_time
def run_queries_with_cache(
    array: list[int],
    queries: list[tuple[str, int, int]],
    cached_range_sum,
) -> None:
    for query_type, first, second in queries:
        if query_type == "Range":
            range_sum_with_cache(array, first, second, cached_range_sum)
        else:
            update_with_cache(array, first, second, cached_range_sum)


def benchmark() -> None:
    random.seed(42)

    n = 100_000
    q = 50_000

    base_array = [random.randint(1, 100) for _ in range(n)]
    queries = make_queries(n, q)

    array_no_cache = base_array.copy()
    _, no_cache_time = run_queries_without_cache(array_no_cache, queries)

    array_with_cache = base_array.copy()
    cached_range_sum = build_cached_range_sum(array_with_cache, maxsize=1000)
    _, with_cache_time = run_queries_with_cache(
        array_with_cache,
        queries,
        cached_range_sum,
    )

    speedup = no_cache_time / with_cache_time if with_cache_time else float("inf")

    print("Результати виконання:")
    print(f"Без кешу: {no_cache_time:.4f} с")
    print(f"З LRU-кешем: {with_cache_time:.4f} с")
    print(f"Прискорення: {speedup:.2f}x")


if __name__ == "__main__":
    benchmark()
