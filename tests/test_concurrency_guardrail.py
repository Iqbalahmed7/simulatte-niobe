from __future__ import annotations

import asyncio

from niobe import runner


def test_shared_semaphore_caps_parallel_calls():
    runner._llm_semaphore = asyncio.Semaphore(20)

    state = {"current": 0, "max_seen": 0}
    lock = asyncio.Lock()

    @runner.with_llm_semaphore
    async def mock_llm_call(_: int) -> int:
        async with lock:
            state["current"] += 1
            state["max_seen"] = max(state["max_seen"], state["current"])
        await asyncio.sleep(0.01)
        async with lock:
            state["current"] -= 1
        return 1

    async def _exercise() -> int:
        results = await asyncio.gather(*[mock_llm_call(i) for i in range(100)])
        return sum(results)

    total = asyncio.run(_exercise())

    assert total == 100
    assert state["max_seen"] <= 20
