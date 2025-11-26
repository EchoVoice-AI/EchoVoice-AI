"""Endpoints for delivery channels and HITL rules.

Supports listing and updating channels and rules, plus a `route` endpoint
that decides whether an item should be sent to delivery or routed to HITL.
"""

from __future__ import annotations

from typing import Dict

from fastapi import APIRouter, HTTPException

from .. import storage
from ..schemas import DeliveryChannel, HitlRule

router = APIRouter()


@router.get("/api/delivery")
async def get_delivery_config() -> Dict:
    return storage.load_delivery_config()


@router.put("/api/delivery/channels/{channel_id}", response_model=DeliveryChannel)
async def update_channel(channel_id: str, payload: DeliveryChannel) -> DeliveryChannel:
    cfg = storage.load_delivery_config() or {"channels": [], "hitl_rules": []}
    channels = cfg.get("channels", [])
    found = None
    for c in channels:
        if c.get("id") == channel_id:
            found = c
            break
    if not found:
        # create new
        channels.append(payload.dict())
    else:
        idx = channels.index(found)
        channels[idx] = payload.dict()
    cfg["channels"] = channels
    storage.save_delivery_config(cfg)
    return payload


@router.post("/api/delivery/hitl/rules", response_model=HitlRule)
async def create_hitl_rule(payload: HitlRule) -> HitlRule:
    cfg = storage.load_delivery_config() or {"channels": [], "hitl_rules": []}
    rules = cfg.get("hitl_rules", [])
    for r in rules:
        if r.get("id") == payload.id:
            raise HTTPException(status_code=400, detail="HITL rule id already exists")
    rules.append(payload.dict())
    cfg["hitl_rules"] = rules
    storage.save_delivery_config(cfg)
    return payload


@router.post("/api/delivery/route")
async def route_for_delivery(item: Dict) -> Dict:
    # Simple decision: check hitl rules and return routing instruction
    cfg = storage.load_delivery_config() or {"channels": [], "hitl_rules": []}
    rules = cfg.get("hitl_rules", [])
    # Naive matching: if any rule condition is met, route to hitl
    for r in rules:
        if not r.get("enabled", True):
            continue
        # For simplicity, match if any condition key exists and equals expected value
        for cond in r.get("conditions", []):
            field = cond.get("field")
            op = cond.get("op")
            value = cond.get("value")
            if field and field in item and op == "==" and item.get(field) == value:
                return {"route": "hitl", "rule_id": r.get("id"), "route_to": r.get("route_to")}  # type: ignore
    # default: deliver
    return {"route": "deliver", "channel": cfg.get("channels", [])[0] if cfg.get("channels") else None}
