"""
Event emitter for broadcasting form state changes to WebSocket clients.

This module provides a singleton EventEmitter that the voice pipeline uses
to broadcast state changes without tight coupling to the API layer.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Set, Union

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
    """
    
    def __init__(self) -> None:
        """Initialize the event emitter with empty subscriber sets."""
        self._queue_subscribers: Set[asyncio.Queue] = set()
        self._callable_subscribers: Set[Callable] = set()
        self._lock = asyncio.Lock()
    
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
                self._callable_subscribers.add(subscriber)
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
            self._callable_subscribers.discard(subscriber)
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
            for callback in self._callable_subscribers:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event)
                    else:
                        callback(event)
                except Exception as e:
                    LOGGER.error("Error in event callback: %s", e, exc_info=True)
    
    def emit_sync(self, event: FormEvent) -> None:
        """
        Synchronously emit an event (creates task for async emit).
        
        Use this from synchronous code that needs to emit events.
        
        Args:
            event: FormEvent to broadcast
        """
        LOGGER.debug("Emitting event synchronously: %s", event.type)
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.emit(event))
        except RuntimeError:
            LOGGER.warning("No event loop running, cannot emit event")


# Global singleton instance
event_emitter = EventEmitter()
