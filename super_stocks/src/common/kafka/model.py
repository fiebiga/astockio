from datetime import datetime
from typing import TypeVar, Generic, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel


EventBodyType = TypeVar("EventBodyType")


class KafkaEventHeader(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    created: datetime = Field(default_factory=datetime.now)


class KafkaEvent(GenericModel, Generic[EventBodyType]):
    header: KafkaEventHeader = Field(default_factory=KafkaEventHeader)
    data: Optional[EventBodyType]


class KafkaUpdateEvent(KafkaEvent, Generic[EventBodyType]):
    old: Optional[EventBodyType]
