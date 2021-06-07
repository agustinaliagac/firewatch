from typing import Optional
from pydantic import BaseModel


class CameraEventRequest(BaseModel):
    camera_id: int
    status: str
    score: Optional[float]
    annotated_image: Optional[str]


class CameraEventResponse(BaseModel):
    id: int
    score: Optional[float]
    status: str
    camera_id: int

    class Config:
        orm_mode = True


class CameraUpdate(BaseModel):
    status: Optional[str]


class CameraResponse(BaseModel):
    id: int
    name: str
    status: str
    location_lat: float
    location_lng: float

    class Config:
        orm_mode = True


class AlertCreate(BaseModel):
    status: str
    camera_id: int
    details: Optional[str]
    location_lat: Optional[float]
    location_lng: Optional[float]


class AlertUpdate(BaseModel):
    status: Optional[str]
    details: Optional[str]
    location_lat: Optional[float]
    location_lng: Optional[float]


class AlertResponse(BaseModel):
    id: int
    status: str
    details: Optional[str]
    location_lat: Optional[float]
    location_lng: Optional[float]
    camera_id: int
    camera: CameraResponse

    class Config:
        orm_mode = True


class NotificationCreate(BaseModel):
    pass
