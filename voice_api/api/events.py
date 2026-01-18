"""
Event emitter for broadcasting form state changes to WebSocket clients.

This module provides a singleton EventEmitter that the voice pipeline uses
to broadcast state changes without tight coupling to the API layer.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from ..config import LOGGER


@dataclass
class FormEvent:
    """
    Event structure for form state changes.
    
    Attributes:
        type: Event type (field_changed, validation_result, field_saved, etc.)
        data: Event payload
        session_id: Optional session ID for multi-session support
    """
    
    type: str
    data: Dict[str, Any]
    session_id: Optional[str] = "default"


class EventEmitter:
    """
    Singleton event emitter for broadcasting form events to WebSocket clients.
    
    The voice pipeline emits events, and WebSocket handlers subscribe to receive them.
    Thread-safe and async-compatible. Supports both Queue and callable subscribers.
    
    IMPORTANT: This emitter supports cross-thread event emission. When the voice
    pipeline (running in a separate thread) emits events, they are properly
    dispatched to callbacks subscribed from the server's event loop.
    """
    
    def __init__(self) -> None:
        """Initialize the event emitter with empty subscriber sets."""
        self._queue_subscribers: Set[asyncio.Queue] = set()
        # Store (callback, event_loop) tuples for cross-thread support
        self._callable_subscribers: Set[Tuple[Callable, Optional[asyncio.AbstractEventLoop]]] = set()
        self._lock = asyncio.Lock()
        self._sync_lock = asyncio.Lock()
    
    async def subscribe(self, subscriber: Union[asyncio.Queue, Callable]) -> None:
        """
        Subscribe a queue or callable to receive events.
        
        Args:
            subscriber: Async queue to receive FormEvent objects, or
                       async callable that accepts FormEvent
        """
        async with self._lock:
            if isinstance(subscriber, asyncio.Queue):
                self._queue_subscribers.add(subscriber)
            elif callable(subscriber):
                # Store the callback with its event loop for cross-thread support
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = None
                self._callable_subscribers.add((subscriber, loop))
                LOGGER.info(
                    "Subscribed callback %s with event loop %s",
                    subscriber.__name__ if hasattr(subscriber, '__name__') else str(subscriber),
                    loop,
                )
            else:
                LOGGER.error("Invalid subscriber type: %s", type(subscriber))
                return
            
            LOGGER.debug(
                "Added subscriber (queues: %s, callables: %s)",
                len(self._queue_subscribers),
                len(self._callable_subscribers),
            )
    
    async def unsubscribe(self, subscriber: Union[asyncio.Queue, Callable]) -> None:
        """
        Unsubscribe a queue or callable from receiving events.
        
        Args:
            subscriber: Queue or callable to remove from subscribers
        """
        async with self._lock:
            self._queue_subscribers.discard(subscriber)
            # Remove any tuple with this callback
            self._callable_subscribers = {
                (cb, loop) for (cb, loop) in self._callable_subscribers if cb != subscriber
            }
            LOGGER.debug(
                "Removed subscriber (queues: %s, callables: %s)",
                len(self._queue_subscribers),
                len(self._callable_subscribers),
            )
    
    async def emit(self, event: FormEvent) -> None:
        """
        Broadcast an event to all subscribers.
        
        Args:
            event: FormEvent to broadcast
        """
        async with self._lock:
            total_subscribers = len(self._queue_subscribers) + len(self._callable_subscribers)
            
            if total_subscribers == 0:
                LOGGER.debug("No subscribers for event: %s", event.type)
                return
            
            LOGGER.info(
                "Broadcasting event '%s' to %s subscriber(s) (queues: %s, callables: %s): %s",
                event.type,
                total_subscribers,
                len(self._queue_subscribers),
                len(self._callable_subscribers),
                event.data,
            )
            
            # Broadcast to queue subscribers
            for queue in self._queue_subscribers:
                try:
                    queue.put_nowait(event)
                except asyncio.QueueFull:
                    LOGGER.warning("Subscriber queue full, dropping event")
            
            # Broadcast to callable subscribers
            for callback, subscriber_loop in self._callable_subscribers:
                try:
                    self._invoke_callback(callback, event, subscriber_loop)
                except Exception as e:
                    LOGGER.error("Error in event callback: %s", e, exc_info=True)
    
    def _invoke_callback(
        self,
        callback: Callable,
        event: FormEvent,
        subscriber_loop: Optional[asyncio.AbstractEventLoop]
    ) -> None:
        """
        Invoke a callback, handling cross-thread scenarios.
        
        Args:
            callback: The callback function to invoke
            event: The event to pass to the callback
            subscriber_loop: The event loop the callback was subscribed from
        """
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            current_loop = None
        
        if asyncio.iscoroutinefunction(callback):
            if subscriber_loop and subscriber_loop != current_loop and subscriber_loop.is_running():
                # Cross-thread: use run_coroutine_threadsafe
                LOGGER.debug(
                    "Cross-thread callback invocation: %s",
                    callback.__name__ if hasattr(callback, '__name__') else str(callback),
                )
                future = asyncio.run_coroutine_threadsafe(callback(event), subscriber_loop)
                # Don't wait for result to avoid blocking
            elif current_loop:
                # Same loop or no subscriber loop: create task
                current_loop.create_task(callback(event))
            else:
                LOGGER.warning("Cannot invoke async callback: no event loop")
        else:
            # Synchronous callback
            callback(event)
    
    def emit_sync(self, event: FormEvent) -> None:
        """
        Synchronously emit an event (dispatches to all subscribers' event loops).
        
        Use this from synchronous code or from a different thread that needs to emit events.
        
        Args:
            event: FormEvent to broadcast
        """
        LOGGER.debug("Emitting event synchronously: %s", event.type)
        
        # Directly invoke callbacks without needing the current thread's event loop
        total_subscribers = len(self._queue_subscribers) + len(self._callable_subscribers)
        
        if total_subscribers == 0:
            LOGGER.debug("No subscribers for sync event: %s", event.type)
            return
        
        LOGGER.info(
            "Sync broadcasting event '%s' to %s subscriber(s): %s",
            event.type,
            total_subscribers,
            event.data,
        )
        
        # Broadcast to queue subscribers
        for queue in self._queue_subscribers:
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                LOGGER.warning("Subscriber queue full, dropping event")
        
        # Broadcast to callable subscribers using their subscribed event loops
        for callback, subscriber_loop in self._callable_subscribers:
            try:
                self._invoke_callback_sync(callback, event, subscriber_loop)
            except Exception as e:
                LOGGER.error("Error in sync event callback: %s", e, exc_info=True)
    
    def _invoke_callback_sync(
        self,
        callback: Callable,
        event: FormEvent,
        subscriber_loop: Optional[asyncio.AbstractEventLoop]
    ) -> None:
        """
        Synchronously invoke a callback, handling cross-thread scenarios.
        
        Args:
            callback: The callback function to invoke
            event: The event to pass to the callback
            subscriber_loop: The event loop the callback was subscribed from
        """
        if asyncio.iscoroutinefunction(callback):
            if subscriber_loop and subscriber_loop.is_running():
                # Use run_coroutine_threadsafe for cross-thread async callbacks
                LOGGER.debug(
                    "Cross-thread sync callback invocation to loop %s: %s",
                    subscriber_loop,
                    callback.__name__ if hasattr(callback, '__name__') else str(callback),
                )
                future = asyncio.run_coroutine_threadsafe(callback(event), subscriber_loop)
                # Don't wait for result to avoid blocking the voice pipeline
            else:
                LOGGER.warning(
                    "Cannot invoke async callback %s: subscriber loop not running",
                    callback.__name__ if hasattr(callback, '__name__') else str(callback),
                )
        else:
            # Synchronous callback - just call it
            callback(event)


# Global singleton instance
event_emitter = EventEmitter()

