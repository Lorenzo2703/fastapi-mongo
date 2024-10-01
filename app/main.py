from bson import ObjectId
from fastapi import FastAPI, HTTPException
from uuid import UUID, uuid4
from db import db_manager
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
    merged_result = {}
    for d in items:
        for key, sub_dict in d.items():
            if key.split('-')[0] not in merged_result:
                merged_result[key.split('-')[0]] = []
            merged_result[key.split('-')[0]].append(sub_dict)

    return merged_result

@app.get("/scoreAll/")
async def get_score_All():
    items = await read_items()
    merged_result = {}
    for d in items:
        for key, sub_dict in d.items():
            base_key = key.split('-')[0]
            if base_key not in merged_result:
                merged_result[base_key] = []
            merged_result[base_key].append(sub_dict)
    
    atos = {}
    prevail = {}
    astop = False
    pstop = False
    rlLvA = 0
    rlLvP = 0
    prev_key = None

    for key, sub_list in merged_result.items():
        a = []
        b = []
    

        for values in sub_list:
            if isinstance(values, dict):   
                a.append(values.get("Atos"))
                b.append(values.get("Prevail"))
            
        if len(a) != 0:
            avg_a = sum(a) / len(a)  # Calculate average once
            atos[key] = avg_a

            if key[:3] != prev_key:
                rlLvA = 0
                astop = False

            if avg_a > 2.9 and not astop:
                rlLvA += 1
                atos[key[:3] + "Lv"] = rlLvA    
            else:
                astop = True   

        
        if len(b) != 0:
            avg_b = sum(b) / len(b)
            prevail[key]=avg_b

            if key[:3] != prev_key:  # Reset rlLvP when the key changes
                rlLvP = 0
                pstop = False

            if avg_b>2.9 and not pstop:
                rlLvP += 1
                prevail[key[:3]+"Lv"] = rlLvP
            else:
                pstop = True

        prev_key = key[:3]  # Update prev_key for the next iteration

    # Insert into the database
    await db_manager.update_item(item={"Atos": atos, "Prevail": prevail})
    
    return [atos, prevail]


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