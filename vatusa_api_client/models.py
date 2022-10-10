from __future__ import annotations
import datetime
from typing import Optional, List
from pydantic import BaseModel


class ControllerData(BaseModel):
    cid: int
    first_name: str
    last_name: str
    email: Optional[str]
    rating: int
    rating_short: str
    facility: str
    flags: List[str]
    global_roles: List[str]
    facility_roles: List[str]
    visits: List[ControllerFacility]
    facility_date: Optional[str]
    promotion_date: Optional[str]


class ControllerMinimal(BaseModel):
    cid: int
    name: str
    rating: int
    rating_short: str
    facility: str


class ControllerFacility(BaseModel):
    facility: str
    facility_roles: List[str]


class ControllerDetails(BaseModel):
    controller: ControllerData
    transfers: List[ControllerTransfer]
    transfer_status: ControllerTransferStatus
    promotions: List[ControllerPromotion]
    action_log: List[ControllerActionLog]


class ControllerTransfer(BaseModel):
    controller: ControllerMinimal
    from_facility: str
    to_facility: str
    reason: str
    create_date: datetime.date
    action: Optional[str]
    action_cid: Optional[int]
    action_date: datetime.date


class ControllerVisitRequest(BaseModel):
    controller: ControllerMinimal
    facility: str
    reason: str
    create_date: datetime.date
    action: Optional[str]
    action_cid: Optional[int]
    action_date: Optional[datetime.date]


class ControllerPromotion(BaseModel):
    controller: ControllerMinimal
    from_rating: int
    from_rating_short: str
    to_rating: int
    to_rating_short: str
    grantor: Optional[ControllerMinimal]
    promotion_date: datetime.date


class ControllerTransferStatus(BaseModel):
    controller: ControllerMinimal
    is_pending_transfer: bool
    is_transfer_eligible: bool
    is_transfer_override: bool

    is_home_controller: bool
    is_basic_training_complete: bool
    is_transfer_stable: bool  # No Transfers in the past 90 days
    is_first_facility: bool
    is_recently_joined_facility: bool
    is_rating_stable: bool  # Not promoted to S1 -> C1 in the past 90 days
    is_staff: bool
    is_instructor: bool


class ControllerActionLog(BaseModel):
    admin_controller: Optional[ControllerMinimal]
    log: str
    log_date: datetime.date


class FacilityData(BaseModel):
    facility: str
    name: str
    url: str
    region: int
    atm: Optional[ControllerMinimal]
    datm: Optional[ControllerMinimal]
    ta: Optional[ControllerMinimal]
    ec: Optional[ControllerMinimal]
    fe: Optional[ControllerMinimal]
    wm: Optional[ControllerMinimal]
    is_active: bool
    is_special: bool


class FacilityRequestsData(BaseModel):
    transfers: List[ControllerTransfer]
    visit_requests: List[ControllerVisitRequest]


class ConfigItemFacilityRole(BaseModel):
    role: str
    name: str


class ConfigItemGlobalRole(BaseModel):
    role: str
    name: str


class ConfigItemRating(BaseModel):
    rating: int
    short: str
    long: str


class Config(BaseModel):
    facility_roles: List[ConfigItemFacilityRole]
    global_roles: List[ConfigItemGlobalRole]
    ratings: List[ConfigItemRating]


ControllerData.update_forward_refs()
ControllerDetails.update_forward_refs()
