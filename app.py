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
from fastapi import FastAPI,UploadFile,File, Form
from fastapi.staticfiles import StaticFiles
import json
from pydantic import BaseModel
import signal
import sys
from types import FrameType
from typing import Annotated
from utils.logging import logger

from google.cloud import storage

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
    geo_coordinate:Geo_coordinate
    date_time:datetime
    level:Level #Enum selectedLevel
    other_level:str|None
    no_of_storeys:int
    use:list[BuildingUse] #Enum selectedBuilding
    multiple_spec:str|None = None
    structure_type:StructureType #Enum selectedStructure
    other_structure:str|None = None
    age_analysis: str|None = None
    age: float
    visual_analysis: list[VisualAnalysis] #Enum selectedVisual
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
async def annotation_input(image:Annotated[UploadFile,File()],data: str = Form()):
    data_dict = json.loads(data)
    annotation = Annotation(**data_dict)
    bucket_name, destination_blob_name = "building-annotation-groundtruth", f"json/{annotation.username}_{annotation.building_id}_{annotation.date_time}.json"
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(annotation.model_dump_json())
    image_filename = f"images/{annotation.username}_{annotation.building_id}_{annotation.date_time}.{image.filename.split('.')[-1]}"
    upload_blob(bucket_name,image,image_filename)
    return data

def upload_blob(bucket_name, file, destination_blob_name):
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # Optional: set a generation-match precondition to avoid potential race conditions
    # and data corruptions. The request to upload is aborted if the object's
    # generation number does not match your precondition. For a destination
    # object that does not yet exist, set the if_generation_match precondition to 0.
    # If the destination object already exists in your bucket, set instead a
    # generation-match precondition using its generation number.
    generation_match_precondition = 0

    blob.upload_from_file(file.file, content_type=file.content_type,if_generation_match=generation_match_precondition)


def shutdown_handler(signal_int:int,frame:FrameType)->None:
    logger.info(f"Caught Signal {signal.strsignal(signal_int)}")
    from utils.logging import flush
    flush()

    sys.exit(0)

app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    signal.signal(signal.SIGINT,shutdown_handler)
else:
    signal.signal(signal.SIGTERM,shutdown_handler)
