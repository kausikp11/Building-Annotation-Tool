# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import datetime
from enum import Enum
from fastapi import FastAPI,UploadFile,File
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import signal
import sys
from types import FrameType
from typing import Annotated
from utils.logging import logger


class Geo_coordinate(BaseModel):
    latitude:float
    longitude:float
    altitude:float
    accuracy:float

class Level(str,Enum):
    ground = "Ground"
    stilt = "Stilt"
    other = "Other"

class BuildingUse(str,Enum):
    resdential = "Residential"
    commercial = "Commercial"
    hospital = "Hospital"
    institutional = "Institutional"
    recreational = "Recreational"
    government = "Government"
    religious = "Religious"

class StructureType(str,Enum):
    rcc_framed = "RCC Framed"
    load_bearing = "Load Bearing"
    other = "Other"

class VisualAnalysis(str,Enum):
    exposed_brick = "Expose brick"
    wood = "Wood"
    acp = "ACP - Aluminum composite panel"
    stone = "Stone"
    hpl = "HPL - High Pressure Laminate"
    glass = "Glass"
    textured_plaster = "Textured Plaster"
    terracotta = "Terracotta"
    metal_cladding = "Metal cladding"
    tiles = "Ceramic Slab/tiles"
    concrete = "Concrete"
    plain_paint = "Plain paint"
    other = "Other"

class Annotation(BaseModel):
    username:str
    building_id:str
    street_name:str | None = None
    # front_elevation:Annotated[UploadFile,File()]
    geo_coordinate:Geo_coordinate
    date_time:datetime
    level:Level #Enum
    other_level:str|None
    no_of_storeys:int
    use:list[BuildingUse] #Enum
    multiple_spec:str|None = None
    structure_type:StructureType #Enum
    other_structure:str|None = None
    age_analysis: str|None = None
    age: float
    visual_analysis: list[VisualAnalysis] #Enum
    other_visual_analysis:str|None = None

def enum_list(enumerator):
    value: list[enumerator] = [enum for enum in enumerator]
    return value

app = FastAPI()

@app.get("/test")
async def root():
    return {"message":"Hello World"}

@app.get("/level")
async def level():
    return enum_list(Level)

@app.get("/use")
async def use():
    return enum_list(BuildingUse)

@app.get("/structre")
async def structre():
    return enum_list(StructureType)

@app.get("/visual")
async def visual():
    return enum_list(VisualAnalysis)

@app.post("/map_data")
async def annotation_input(data:Annotation):
    return data

def shutdown_handler(signal_int:int,frame:FrameType)->None:
    logger.info(f"Caught Signal {signal.strsignal(signal_int)}")
    from utils.logging import flush

    print("came")
    flush()

    sys.exit(0)

app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    signal.signal(signal.SIGINT,shutdown_handler)
else:
    signal.signal(signal.SIGTERM,shutdown_handler)
