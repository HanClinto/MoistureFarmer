from typing import TYPE_CHECKING, Optional, Type

from pydantic import BaseModel
from simulation.core.entity.component.Chassis import Component



class ComponentSlot(BaseModel):
    slot_id: Optional[str] = None
    accepts: Optional[Type[Component]] = Component
    component: Optional[Component] = None
    default_component: Optional[Type[Component]] = None

    def __init__(self, slot_id: Optional[str] = None, accepts: Optional[Type[Component]] = Component, component: Optional[Component] = None, default_component: Optional[Type[Component]] = None, **data):
        super().__init__(**data)
        self.slot_id = slot_id
        self.accepts = accepts
        self.component = component
        self.default_component = default_component
        # If we have a default component set but no component, then initialize one
        # TODO: Are we going to need to include kwargs for the default component as another parameter?
        if default_component and not component:
            self.component = default_component()
            

