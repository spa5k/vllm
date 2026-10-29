# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright contributors to the vLLM project
# _LoRACountingQueue calls the concrete queue methods via super().
# mypy: disable-error-code="safe-super"

import heapq
from abc import ABC, abstractmethod
from collections import Counter, deque
from collections.abc import Iterable, Iterator
from enum import Enum

from vllm.v1.request import Request


class SchedulingPolicy(Enum):
    """Enum for scheduling policies."""

    FCFS = "fcfs"
    PRIORITY = "priority"


class RequestQueue(ABC):
    """Abstract base class for request queues."""

    @abstractmethod
    def add_request(self, request: Request) -> None:
        """Add a request to the queue according to the policy."""
        pass

    @abstractmethod
    def pop_request(self) -> Request:
        """Pop a request from the queue according to the policy."""
        pass

    @abstractmethod
    def peek_request(self) -> Request:
        """Peek at the request at the front of the queue without removing it."""
        pass

    @abstractmethod
    def prepend_request(self, request: Request) -> None:
        """Prepend a request to the front of the queue."""
        pass

    @abstractmethod
    def prepend_requests(self, requests: Iterable[Request]) -> None:
        """Prepend all requests from another queue to the front of this
        queue."""
        pass

    @abstractmethod
    def remove_request(self, request: Request) -> None:
        """Remove a specific request from the queue."""
        pass

    @abstractmethod
    def remove_requests(self, requests: Iterable[Request]) -> None:
        """Remove multiple specific requests from the queue."""
        pass

    @abstractmethod
    def __bool__(self) -> bool:
        """Check if queue has any requests."""
        pass

    @abstractmethod
    def __len__(self) -> int:
        """Get number of requests in queue."""
        pass

    @abstractmethod
    def __iter__(self) -> Iterator[Request]:
        """Iterate over the queue according to the policy."""
        pass

    def unordered(self) -> Iterable[Request]:
        """Iterate over the queue in no particular order."""
        return self

    def num_lora_admissible(self, lora_ids: Iterable[int]) -> int:
        """Upper bound on the queued requests that the max_loras check does
        not skip when the LoRA slots are full with `lora_ids`."""
        return len(self)


class FCFSRequestQueue(deque[Request], RequestQueue):
    """A first-come-first-served queue that supports deque operations."""

    def add_request(self, request: Request) -> None:
        """Add a request to the queue according to FCFS policy."""
        self.append(request)

    def pop_request(self) -> Request:
        """Pop a request from the queue according to FCFS policy."""
        return self.popleft()

    def peek_request(self) -> Request:
        """Peek at the next request in the queue without removing it."""
        if not self:
            raise IndexError("peek from an empty queue")
        return self[0]

    def prepend_request(self, request: Request) -> None:
        """Prepend a request to the front of the queue."""
        self.appendleft(request)

    def prepend_requests(self, requests: Iterable[Request]) -> None:
        """Prepend all requests from another queue to the front of this
        queue.

        Note: The requests will be prepended in reverse order of their
        appearance in the `requests` queue.
        """
        self.extendleft(requests)

    def remove_request(self, request: Request) -> None:
        """Remove a specific request from the queue."""
        self.remove(request)

    def remove_requests(self, requests: Iterable[Request]) -> None:
        """Remove multiple specific requests from the queue."""
        requests_to_remove = set(requests)
        filtered_requests = [req for req in self if req not in requests_to_remove]
        # deque does not support in-place filtering, so we need to clear
        # and extend
        self.clear()
        self.extend(filtered_requests)

    def __bool__(self) -> bool:
        """Check if queue has any requests."""
        return len(self) > 0

    def __len__(self) -> int:
        """Get number of requests in queue."""
        return super().__len__()

    def __iter__(self) -> Iterator[Request]:
        """Iterate over the queue according to FCFS policy."""
        return super().__iter__()


class PriorityRequestQueue(RequestQueue):
    """A priority queue that supports heap operations.

    Respects the ordering defined in the Request class, where
    requests with a smaller value of `priority` are processed first.
    If multiple requests have the same priority, the one with the earlier
    `arrival_time` is processed first.
    """

    def __init__(self) -> None:
        self._heap: list[Request] = []

    def add_request(self, request: Request) -> None:
        """Add a request to the queue according to priority policy."""
        heapq.heappush(self._heap, request)

    def pop_request(self) -> Request:
        """Pop a request from the queue according to priority policy."""
        if not self._heap:
            raise IndexError("pop from empty heap")
        return heapq.heappop(self._heap)

    def peek_request(self) -> Request:
        """Peek at the next request in the queue without removing it."""
        if not self._heap:
            raise IndexError("peek from empty heap")
        return self._heap[0]

    def prepend_request(self, request: Request) -> None:
        """Add a request to the queue according to priority policy.

        Note: In a priority queue, there is no concept of prepending to the
        front. Requests are ordered by (priority, arrival_time)."""
        heapq.heappush(self._heap, request)

    def prepend_requests(self, requests: Iterable[Request]) -> None:
        """Add all requests from another queue according to priority policy.

        Note: In a priority queue, there is no concept of prepending to the
        front. Requests are ordered by (priority, arrival_time)."""
        for request in requests:
            heapq.heappush(self._heap, request)

    def remove_request(self, request: Request) -> None:
        """Remove a specific request from the queue."""
        self._heap.remove(request)
        heapq.heapify(self._heap)

    def remove_requests(self, requests: Iterable[Request]) -> None:
        """Remove multiple specific requests from the queue."""
        requests_to_remove = requests if isinstance(requests, set) else set(requests)
        self._heap = [r for r in self._heap if r not in requests_to_remove]
        heapq.heapify(self._heap)

    def __bool__(self) -> bool:
        """Check if queue has any requests."""
        return bool(self._heap)

    def __len__(self) -> int:
        """Get number of requests in queue."""
        return len(self._heap)

    def __iter__(self) -> Iterator[Request]:
        """Iterate over the queue according to priority policy."""
        heap_copy = self._heap[:]
        while heap_copy:
            yield heapq.heappop(heap_copy)

    def unordered(self) -> Iterable[Request]:
        return self._heap


def _lora_key(request: Request) -> int:
    """The LoRA ID if the max_loras check alone can skip the request, else 0.
    Structured output requests get 0: a visit reports their grammar errors."""
    lora = request.lora_request
    if lora is None or request.structured_output_request is not None:
        return 0
    return lora.lora_int_id


class _LoRACountingQueue(RequestQueue):
    """Counts the queued requests per `_lora_key`. Used only with LoRA."""

    def __init__(self) -> None:
        super().__init__()
        self.lora_counts: Counter[int] = Counter()

    def num_lora_admissible(self, lora_ids: Iterable[int]) -> int:
        return self.lora_counts[0] + sum(self.lora_counts[i] for i in lora_ids)

    def add_request(self, request: Request) -> None:
        super().add_request(request)
        self.lora_counts[_lora_key(request)] += 1

    def pop_request(self) -> Request:
        request = super().pop_request()
        self.lora_counts[_lora_key(request)] -= 1
        return request

    def prepend_request(self, request: Request) -> None:
        super().prepend_request(request)
        self.lora_counts[_lora_key(request)] += 1

    def prepend_requests(self, requests: Iterable[Request]) -> None:
        requests = list(requests)
        super().prepend_requests(requests)
        self.lora_counts.update(map(_lora_key, requests))

    def remove_request(self, request: Request) -> None:
        super().remove_request(request)
        self.lora_counts[_lora_key(request)] -= 1

    def remove_requests(self, requests: Iterable[Request]) -> None:
        removed = set(requests).intersection(self.unordered())
        super().remove_requests(removed)
        self.lora_counts.subtract(map(_lora_key, removed))


class _LoRAFCFSRequestQueue(_LoRACountingQueue, FCFSRequestQueue):
    pass


class _LoRAPriorityRequestQueue(_LoRACountingQueue, PriorityRequestQueue):
    pass


def create_request_queue(
    policy: SchedulingPolicy, count_loras: bool = False
) -> RequestQueue:
    """Create request queue based on scheduling policy."""
    if policy == SchedulingPolicy.PRIORITY:
        return _LoRAPriorityRequestQueue() if count_loras else PriorityRequestQueue()
    elif policy == SchedulingPolicy.FCFS:
        return _LoRAFCFSRequestQueue() if count_loras else FCFSRequestQueue()
    else:
        raise ValueError(f"Unknown scheduling policy: {policy}")
