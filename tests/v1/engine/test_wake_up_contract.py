# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright contributors to the vLLM project

import asyncio
import contextlib
from concurrent.futures import Future
from threading import Event, Lock
from threading import Thread as CallerThread
from types import SimpleNamespace
from unittest.mock import AsyncMock, call

import pytest

from vllm.v1.engine import EngineCoreOutputs, UtilityOutput, UtilityResult
from vllm.v1.engine import core_client as clients
from vllm.v1.engine.core_client import DPLBAsyncMPClient
from vllm.v1.engine.exceptions import EngineDeadError
from vllm.v1.engine.utils import CoreEngineActorManager

pytestmark = pytest.mark.cpu_test


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "results, expected",
    [
        ([True, True], True),
        ([True, False], False),
        ([False, True], False),
        ([False, False], False),
    ],
)
async def test_dp_wake_up_requires_all_engines_awake(results, expected):
    client = object.__new__(DPLBAsyncMPClient)
    client.core_engines = [b"engine-0", b"engine-1"]
    client._call_utility_async = AsyncMock(side_effect=results)

    assert await client.wake_up_async(["weights"]) is expected
    assert client._call_utility_async.await_args_list == [
        call("wake_up", ["weights"], engine=b"engine-0"),
        call("wake_up", ["weights"], engine=b"engine-1"),
    ]


def _sync_client(monkeypatch, *, shutdown=False):
    class Socket:
        def bind(self, _address):
            pass

        def close(self, **_kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            pass

        def connect(self, _address):
            pass

        def send(self, _message):
            pass

        def recv_multipart(self, **_kwargs):
            return [SimpleNamespace(buffer=clients.EngineCoreProc.ENGINE_CORE_DEAD)]

    output = Socket()
    stop = Socket()

    class Poller:
        def register(self, *_args):
            pass

        def poll(self):
            return [(stop if shutdown else output, clients.zmq.POLLIN)]

    class ReceiverThread:
        def __init__(self, *, target, **_kwargs):
            self.target = target

        def start(self):
            pass

    def init(client, **_kwargs):
        client.utility_results = {}
        client.utility_results_lock = Lock()
        client.ctx = SimpleNamespace(socket=lambda *_args: stop)
        client.resources = clients.BackgroundResources(
            ctx=client.ctx, output_socket=output
        )
        client.decoder = SimpleNamespace(decode=lambda frames: frames[0])
        client.vllm_config = SimpleNamespace(
            parallel_config=SimpleNamespace(data_parallel_size=1)
        )

    monkeypatch.setattr(clients.MPClient, "__init__", init)
    monkeypatch.setattr(clients, "Thread", ReceiverThread)
    monkeypatch.setattr(clients.zmq, "Socket", Socket)
    monkeypatch.setattr(clients.zmq, "Poller", Poller)
    monkeypatch.setattr(clients, "close_sockets", lambda _sockets: None)
    monkeypatch.setattr(clients, "get_open_zmq_inproc_path", lambda: "unused")
    client = clients.SyncMPClient(None, None, False)
    client._send_input = lambda *_args: client.output_queue_thread.target()
    return client


class _AsyncSocket:
    def __init__(self):
        self.messages: asyncio.Queue[EngineCoreOutputs | BaseException] = (
            asyncio.Queue()
        )
        self.receive_count = 0
        self.started = asyncio.Event()

    async def recv_multipart(self, **_kwargs):
        self.receive_count += 1
        self.started.set()
        message = await self.messages.get()
        if isinstance(message, EngineDeadError):
            return [SimpleNamespace(buffer=clients.EngineCoreProc.ENGINE_CORE_DEAD)]
        if isinstance(message, BaseException):
            raise message
        return [message, b""]


def _async_client(monkeypatch):
    socket = _AsyncSocket()
    monkeypatch.setattr(clients.zmq.asyncio, "Socket", _AsyncSocket)
    monkeypatch.setattr(clients, "close_sockets", lambda _sockets: None)
    client = object.__new__(clients.AsyncMPClient)
    client.utility_results = {}
    client.utility_results_lock = Lock()
    client.resources = clients.BackgroundResources(ctx=None, output_socket=socket)
    client.decoder = SimpleNamespace(decode=lambda frames: frames[0])
    client.outputs_queue = asyncio.Queue()
    client.core_engine = b"engine-0"
    client.core_engines = [b"engine-0", b"engine-1"]
    client.client_index = 0
    client.encoder = SimpleNamespace(encode=lambda request: (request,))
    client.sent = asyncio.Queue()

    async def send(message, engine):
        call_id = message[1][1]
        client.sent.put_nowait((engine, call_id, client.utility_results[call_id]))

    client._send_input_message = send
    return client, socket


async def _sent(client):
    return await asyncio.wait_for(client.sent.get(), timeout=1)


async def _receiver_done(client):
    receiver = client.resources.output_queue_task
    observed = asyncio.Event()
    receiver.add_done_callback(lambda _task: observed.set())
    await asyncio.wait_for(observed.wait(), timeout=1)
    with contextlib.suppress(asyncio.CancelledError):
        await asyncio.wait_for(asyncio.shield(receiver), timeout=1)


async def _finish(client, *calls):
    receiver = client.resources.output_queue_task
    for task in (*calls, receiver):
        if task is not None:
            if not task.done():
                task.cancel()
            with contextlib.suppress(asyncio.CancelledError, EngineDeadError):
                await task
    with client.utility_results_lock:
        futures = tuple(client.utility_results.values())
        client.utility_results.clear()
    for future in futures:
        if not future.done():
            future.cancel()
        elif not future.cancelled():
            future.exception()


def _drain_sync(client):
    with client.utility_results_lock:
        futures = tuple(client.utility_results.values())
        client.utility_results.clear()
    for future in futures:
        if not future.done():
            future.set_exception(EngineDeadError())


@pytest.mark.parametrize(
    "stop_kind", ["death", "receiver_shutdown", "cleanup", "manager_error"]
)
def test_sync_utility_settles_when_receiver_stops(monkeypatch, stop_kind):
    client = _sync_client(monkeypatch, shutdown=stop_kind != "death")
    sent = Event()
    cleanup_started = Event()
    outcome: Future[object] = Future()

    def send(*_args):
        if cleanup_started.is_set():
            raise RuntimeError("test cleanup already started")
        sent.set()

    client._send_input = send

    def call():
        try:
            outcome.set_result(client.call_utility("is_sleeping"))
        except BaseException as error:
            outcome.set_exception(error)

    caller = CallerThread(target=call, name="utility-test-caller", daemon=True)
    receiver_driven = False
    caller.start()
    try:
        assert sent.wait(timeout=1)
        if stop_kind == "cleanup":
            client.resources()
        elif stop_kind == "manager_error":
            error = RuntimeError("manager shutdown failed")
            timeouts = []

            def stop_manager(*, timeout):
                timeouts.append(timeout)
                raise error

            manager = SimpleNamespace(shutdown=stop_manager)
            client.resources.engine_manager = manager
            client._finalizer = SimpleNamespace(detach=lambda: object())
            with pytest.raises(RuntimeError) as caught:
                client.shutdown(timeout=2)
            assert caught.value is error
            assert timeouts == [2]
            assert client.resources.engine_manager is manager
        if stop_kind in ("death", "receiver_shutdown"):
            receiver_driven = True
            client.output_queue_thread.target()
        caller.join(timeout=1)
        assert not caller.is_alive(), "terminal receiver stranded its utility caller"
        with pytest.raises(EngineDeadError):
            outcome.result()
        assert client.utility_results == {}
        assert client.resources.utility_terminal.is_set()
    finally:
        cleanup_started.set()
        _drain_sync(client)
        try:
            if not receiver_driven:
                client.output_queue_thread.target()
        finally:
            caller.join(timeout=1)
            _drain_sync(client)
            assert not caller.is_alive(), (
                "test cleanup failed to release its own caller"
            )


def test_sync_send_failure_removes_only_its_utility(monkeypatch):
    client = _sync_client(monkeypatch)
    sibling: Future[object] = Future()
    client.utility_results[123] = sibling
    error = RuntimeError("send failed")

    def send(*_args):
        raise error

    client._send_input = send
    try:
        with pytest.raises(RuntimeError) as caught:
            client.call_utility("is_sleeping")
        assert caught.value is error
        assert client.utility_results == {123: sibling}
        assert not sibling.done()
    finally:
        _drain_sync(client)


@pytest.mark.asyncio
@pytest.mark.parametrize("stop_kind", ["death", "receiver_error", "shutdown"])
async def test_async_utility_settles_when_receiver_stops(monkeypatch, stop_kind):
    client, socket = _async_client(monkeypatch)
    call = asyncio.create_task(client.call_utility_async("is_sleeping"))
    try:
        _engine, call_id, future = await _sent(client)
        assert future.get_loop() is asyncio.get_running_loop()
        await asyncio.wait_for(socket.started.wait(), timeout=1)
        error = (
            RuntimeError("receiver stopped")
            if stop_kind == "receiver_error"
            else EngineDeadError()
        )
        if stop_kind == "shutdown":
            client.resources()
        else:
            socket.messages.put_nowait(error)
        await _receiver_done(client)
        assert future.done(), "terminal receiver left its utility caller pending"
        with pytest.raises(EngineDeadError):
            await call
        assert client.utility_results == {}
        if stop_kind == "receiver_error":
            assert client.outputs_queue.get_nowait() is error
            assert client.resources.engine_dead is False
        clients._process_utility_output(
            UtilityOutput(call_id, result=UtilityResult(True)),
            client.utility_results,
            client.utility_results_lock,
        )
        with pytest.raises(EngineDeadError):
            await client.call_utility_async("is_sleeping")
        assert client.utility_results == {}
    finally:
        await _finish(client, call)


@pytest.mark.asyncio
async def test_receiver_cancelled_before_start_settles_utility(monkeypatch):
    client, socket = _async_client(monkeypatch)
    ensure = client._ensure_output_queue_task

    def cancel_before_start():
        ensure()
        client.resources.output_queue_task.cancel()

    client._ensure_output_queue_task = cancel_before_start
    call = asyncio.create_task(client.call_utility_async("is_sleeping"))
    try:
        _engine, _call_id, future = await _sent(client)
        await _receiver_done(client)
        assert socket.receive_count == 0
        assert future.done(), "pre-start cancellation bypassed terminal settlement"
        with pytest.raises(EngineDeadError):
            await call
        assert client.utility_results == {}
    finally:
        await _finish(client, call)


@pytest.mark.asyncio
@pytest.mark.parametrize("send_state", ["plain", "terminal_error", "terminal_cancel"])
async def test_async_send_failure_keeps_its_original_error(monkeypatch, send_state):
    client, _socket = _async_client(monkeypatch)
    sibling = asyncio.get_running_loop().create_future()
    client.utility_results[123] = sibling
    error = (
        asyncio.CancelledError()
        if send_state == "terminal_cancel"
        else RuntimeError("send failed")
    )

    async def send(*_args):
        if send_state != "plain":
            client.resources()
        raise error

    client._send_input_message = send
    try:
        with pytest.raises(type(error)) as caught:
            await client.call_utility_async("is_sleeping")
        assert caught.value is error
        if send_state == "plain":
            assert client.utility_results == {123: sibling}
            assert not sibling.done()
        else:
            assert client.utility_results == {}
            with pytest.raises(EngineDeadError):
                await sibling
    finally:
        await _finish(client)


@pytest.mark.asyncio
async def test_cancelled_utility_late_reply_preserves_sibling(monkeypatch):
    client, socket = _async_client(monkeypatch)
    cancelled = asyncio.create_task(client.call_utility_async("is_sleeping"))
    sibling = None
    try:
        _engine, cancelled_id, _future = await _sent(client)
        cancelled.cancel()
        with pytest.raises(asyncio.CancelledError):
            await cancelled
        sibling = asyncio.create_task(client.call_utility_async("is_sleeping"))
        _engine, sibling_id, _future = await _sent(client)
        for call_id, value in ((cancelled_id, False), (sibling_id, True)):
            socket.messages.put_nowait(
                EngineCoreOutputs(
                    utility_output=UtilityOutput(call_id, result=UtilityResult(value))
                )
            )
        assert await asyncio.wait_for(asyncio.shield(sibling), timeout=1) is True
        assert client.utility_results == {}
        assert not client.resources.output_queue_task.done()
    finally:
        await _finish(client, cancelled, sibling)


@pytest.mark.asyncio
async def test_terminal_receiver_settles_gather_and_eep_waiter(monkeypatch):
    client, socket = _async_client(monkeypatch)
    call = asyncio.create_task(client.call_utility_all_async("is_sleeping"))
    eep = None
    try:
        await _sent(client)
        await _sent(client)
        eep = clients.DPLBAsyncMPClient._eep_wait_for_setup_switch_complete(client)
        futures = list(client.utility_results.values())
        socket.messages.put_nowait(EngineDeadError())
        await _receiver_done(client)
        assert all(future.done() for future in futures)
        with pytest.raises(EngineDeadError):
            await call
        with pytest.raises(EngineDeadError):
            await eep
        assert client.utility_results == {}
    finally:
        if eep is not None and not eep.done():
            eep.cancel()
        elif eep is not None and not eep.cancelled():
            eep.exception()
        await _finish(client, call)


def test_terminal_transition_during_registration_leaves_no_row(monkeypatch):
    client = _sync_client(monkeypatch)

    class TerminalOnEntry:
        def __enter__(self):
            client.resources.utility_terminal.set()

        def __exit__(self, *_args):
            pass

    client.utility_results_lock = TerminalOnEntry()
    with pytest.raises(EngineDeadError):
        clients._register_utility_result(
            7,
            Future(),
            client.utility_results,
            client.utility_results_lock,
            client.resources.utility_terminal,
        )
    assert client.utility_results == {}


class _ObservedFailedFuture(asyncio.Future):
    def __init__(self):
        super().__init__()
        self.exception_calls = 0
        self.cancel_calls = 0

    def exception(self):
        self.exception_calls += 1
        return super().exception()

    def cancel(self, *args, **kwargs):
        self.cancel_calls += 1
        return super().cancel(*args, **kwargs)


def _scale_down_manager():
    actor = object()
    run_ref = object()
    manager = object.__new__(CoreEngineActorManager)
    manager.placement_group_is_local = [True]
    manager.local_engine_actors = [actor]
    manager.remote_engine_actors = []
    manager.actor_run_ref_dict = {actor: run_ref}
    manager.run_refs = [run_ref]
    return manager


@pytest.mark.asyncio
@pytest.mark.parametrize("direction", ["up", "down"])
@pytest.mark.parametrize("error_type", [RuntimeError, asyncio.CancelledError])
async def test_elastic_ep_commit_retrieves_failed_notification(direction, error_type):
    client = object.__new__(DPLBAsyncMPClient)
    terminal_error = EngineDeadError()
    wait_future = _ObservedFailedFuture()
    wait_future.set_exception(terminal_error)
    sibling_error = error_type("sibling commit failed")
    client._eep_wait_for_setup_switch_complete = lambda: wait_future
    client._eep_commit_pause_mode = lambda: "keep"

    async def utility(method, *_args, **_kwargs):
        if method == "pause_scheduler":
            return None
        raise sibling_error

    client._call_utility_async = utility
    if direction == "up":
        client.core_engines = [b"engine-0"]
        client.pause_scheduler_async = AsyncMock()
        commit = client._commit_scale_up_elastic_ep(2)
    else:
        client.core_engines = [b"engine-0", b"engine-1"]
        client.lb_engines = client.core_engines.copy()
        client.engine_ranks_managed = [0, 1]
        client._kv_event_sources = {}
        client.resources = SimpleNamespace(engine_manager=_scale_down_manager())
        client._make_reconfig_request = lambda *_args: object()
        commit = client._commit_scale_down_elastic_ep(1)

    try:
        with pytest.raises(error_type) as caught:
            await commit

        if error_type is RuntimeError:
            assert caught.value is sibling_error
        else:
            assert str(caught.value) == str(sibling_error)
        assert wait_future.exception_calls == 1
        assert wait_future.cancel_calls == 0
    finally:
        if wait_future.done() and not wait_future.cancelled():
            asyncio.Future.exception(wait_future)
