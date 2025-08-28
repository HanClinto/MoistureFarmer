from typing import TYPE_CHECKING, Optional, Type

from pydantic import BaseModel
from simulation.core.entity.component.Component import Component


class ComponentSlot(BaseModel):
    slot_id: Optional[str] = None
    accepts: Optional[Type[Component]] = Component
    _component: Optional[Component] = None
    default_component: Optional[Type[Component]] = None

    def __init__(self, slot_id: Optional[str] = None, accepts: Optional[Type[Component]] = Component, component: Optional[Component] = None, default_component: Optional[Type[Component]] = None, **data):
        super().__init__(**data)
        self.slot_id = slot_id
        self.accepts = accepts
        self.component = component
        self.default_component = default_component
        # If we have a default component set but no component, then initialize one
        # TODO: Are we going to need to include kwargs for the default component as another parameter?
        if default_component and not self._component:
            self._component = default_component()

    @property
    def component(self) -> Optional[Component]:
        return self._component

    @component.setter
    def component(self, value: Optional[Component]):
        # TODO: Also call Chassis.install_component on this (but we need to hold a reference to the chassis on this slot first)
        if value and not isinstance(value, self.accepts):
            raise TypeError(f"Component must be of type {self.accepts.__name__}")
        self._component = value
