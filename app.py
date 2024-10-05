from typing import List, Union

from fastapi import FastAPI
from lib import download_scene, initialize_api, logout, search_scenes
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import os

from utils import convert_tif_to_grayscale_image, extract_tar_file

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


class SearchQuery(BaseModel):
    latitude: float
    longitude: float
    start_date: str
    end_date: str
    cloud_cover: int = 100


class DownloadScene(BaseModel):
    scene_id: str
    display_id: str


class CloudData(BaseModel):
    date: str
    coverage: float


USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
api, ee = initialize_api(USERNAME, PASSWORD)


# post with json that contains: longitude, latitude, start_date, end_date, cloud_cover
@app.post("/search")
def search(query: SearchQuery):
    global api, ee

    # Search for scenes
    try:
        scenes = search_scenes(
            api,
            query.latitude,
            query.longitude,
            query.start_date,
            query.end_date,
            query.cloud_cover,
        )
    except Exception as e:
        newApi, newEe = initialize_api(USERNAME, PASSWORD)
        api = newApi
        ee = newEe
        scenes = search_scenes(
            api,
            query.latitude,
            query.longitude,
            query.start_date,
            query.end_date,
            query.cloud_cover,
        )
    return {"scenes": scenes}


#


@app.post("/download")
def download(meta: DownloadScene):
    global api, ee

    if not api:
        print("no api")

    if not ee:
        print("no ee")

    # Download the scene
    try:
        download_scene(ee, meta.scene_id, "downloads")
    except Exception as e:
        newApi, newEe = initialize_api(USERNAME, PASSWORD)
        api = newApi
        ee = newEe
        download_scene(ee, meta.scene_id, "downloads")

    tar_file_path = os.path.join("downloads", f"{meta.display_id}.tar")
    extract_to = (
        f"data/{meta.display_id}"  # You can customize this to any directory you want
    )

    # Call the extraction function
    success = extract_tar_file(tar_file_path, extract_to)

    if not success:
        return {"status": "error"}

    file_list = os.listdir(extract_to)
    file_list = [f for f in file_list if os.path.isfile(os.path.join(extract_to, f))]
    file_list = [f.lower() for f in file_list]
    file_list = [f for f in file_list if f.endswith(".tif")]

    out_dir = f"static/{meta.display_id}"

    final = []

    # filter only files ending with band.tif
    tif_files = [
        f
        for f in file_list
        if f.endswith(".tif") and any(f"_b{band}" in f for band in range(1, 12))
    ]

    for tif_file in tif_files:
        output_file = convert_tif_to_grayscale_image(
            tif_file, output_format="jpeg", output_dir=out_dir
        )

        band = tif_file.split("_")[-1]

        final.append(
            {
                "band": band,
                "image": f"https://nasa-map.elyra.games/static/{output_file}",
            }
        )

    print(final)
    return {"images": final}


@app.post("/plot/cloud")
def plot_cloud(data: List[CloudData]):
    global api, ee
