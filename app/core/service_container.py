# app/core/service_container.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, TypeVar, Type

T = TypeVar("T")


@dataclass
class _ServiceRegistration:
    factory: Callable[[], Any]
    singleton: bool
    instance: Any | None = None


class ServiceContainer:
    """
    Very lightweight DI container.
    - Register by interface (Protocol or ABC)
    - Choose singleton or transient
    """

    def __init__(self) -> None:
        self._registrations: Dict[type[Any], _ServiceRegistration] = {}

    def register(
        self,
        interface: type[T],
        factory: Callable[[], T],
        *,
        singleton: bool = True,
    ) -> None:
        self._registrations[interface] = _ServiceRegistration(
            factory=factory,
            singleton=singleton,
        )

    def resolve(self, interface: type[T]) -> T:
        try:
            reg = self._registrations[interface]
        except KeyError as exc:
            raise KeyError(f"No registration for interface: {interface!r}") from exc

        if reg.singleton:
            if reg.instance is None:
                reg.instance = reg.factory()
            return reg.instance  # type: ignore[return-value]

        # transient
        return reg.factory()  # type: ignore[return-value]
