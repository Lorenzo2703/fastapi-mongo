from bson import ObjectId
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from uuid import UUID, uuid4
from db import db_manager
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/items/")
async def create_item(item: Dict):
    return await db_manager.create_item(item)


@app.get("/items/")
async def read_items():
    return await db_manager.read_items()

@app.get("/score/")
async def get_scores():
    items=await db_manager.read_items()
    count=len(items)
    merged_result = {}


    for d in items:
        for key, sub_dict in d.items():
            if key.split('-')[0] not in merged_result:
                merged_result[key.split('-')[0]] = []
            merged_result[key.split('-')[0]].append(sub_dict)

    return merged_result
    


@app.get("/items/{item_id}")
async def read_item(item_id: str):
    item = await db_manager.read_item(ObjectId(item_id))
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.put("/items/{item_id}")
async def update_item(item_id: str, item):
    updated_item = await db_manager.update_item(ObjectId(item_id), item.model_dump())
    if updated_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated_item

@app.delete("/items/{item_id}")
async def delete_item(item_id: str):
    deleted = await db_manager.delete_item(ObjectId(item_id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    return "Item deleted successfully"




"""
treshold = 80.00
scale_value = (100%/number of questions)/3
"""