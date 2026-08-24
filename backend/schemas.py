from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from datetime import datetime


class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str  # 'sme' or 'ff'
    company: Optional[str] = None
    phone: Optional[str] = None
    license_number: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    company: Optional[str]
    phone: Optional[str]

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    token: str
    user: UserOut


class CreateListingRequest(BaseModel):
    vessel_name: str
    imo_number: Optional[str] = None
    shipping_line: Optional[str] = None
    from_port: str
    to_port: str
    departure_date: datetime
    available_teu: int
    total_teu: Optional[int] = None
    price_per_teu: float
    cargo_types: Optional[str] = "General"
    container_sizes: Optional[str] = "20ft, 40ft"
    contact_email: Optional[str] = None


class UpdateListingRequest(BaseModel):
    available_teu: Optional[int] = None
    price_per_teu: Optional[float] = None
    status: Optional[str] = None


class ListingOut(BaseModel):
    id: int
    forwarder_id: Optional[int]
    vessel_name: str
    imo_number: Optional[str]
    shipping_line: Optional[str]
    from_port: str
    to_port: str
    departure_date: datetime
    available_teu: int
    total_teu: Optional[int]
    price_per_teu: float
    cargo_types: Optional[str]
    container_sizes: Optional[str]
    contact_email: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class BookingRequest(BaseModel):
    listing_id: int
    teu_count: int
    payment_method: str = "upi"
    note: Optional[str] = ""


class BookingOut(BaseModel):
    id: int
    reference: str
    sme_id: int
    listing_id: int
    teu_count: int
    total_amount: float
    payment_method: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class BookingRequestOut(BaseModel):
    id: int
    booking_id: int
    forwarder_id: int
    sme_name: str
    sme_company: str
    teu_count: int
    total_amount: float
    note: str
    status: str
    rejection_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class RejectRequest(BaseModel):
    message: str


class SearchResponse(BaseModel):
    live: List[ListingOut]
    predicted: List[Any]
