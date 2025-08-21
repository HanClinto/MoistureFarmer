from typing import TYPE_CHECKING, Optional, Type

from pydantic import BaseModel
from simulation.entity.component.Component import Component

if TYPE_CHECKING:
    from simulation.entity.Chassis import Chassis  # type: ignore

class ComponentSlot(BaseModel):
    slot_id: Optional[str] = None
    accepts: Type[Component]
    component: Optional[Component] = None

#ComponentSlot.model_rebuild()
