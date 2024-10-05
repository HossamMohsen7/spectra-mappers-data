from datetime import datetime
import os
import json
from landsatxplore.api import API
from landsatxplore.earthexplorer import EarthExplorer


def initialize_api(username, password):
    """Initialize API and EarthExplorer instances."""
    try:
        api = API(username, password)
        ee = EarthExplorer(username, password)
        return api, ee
    except Exception as e:
        print(f"Error initializing API/EarthExplorer: {e}")
        return None, None


def search_scenes(api, latitude, longitude, start_date, end_date, cloud_cover=100):
    """Search for Landsat scenes based on parameters."""
    try:
        scenes = api.search(
            dataset="landsat_ot_c2_l1",  # Dataset for Landsat 8 and 9
            latitude=latitude,
            longitude=longitude,
            start_date=start_date,
            end_date=end_date,
            max_cloud_cover=cloud_cover,
        )
        print(f"{len(scenes)} scenes found.")
        return scenes
    except Exception as e:
        print(f"Error searching for scenes: {e}")
        return []


def download_scene(ee, scene_id, download_dir):
    """Download the specified scene to the given directory."""
    try:
        os.makedirs(download_dir, exist_ok=True)  # Ensure directory exists
        ee.download(scene_id, download_dir)
        print(f"Downloaded scene: {scene_id} to {download_dir}")
    except Exception as e:
        print(f"Error downloading scene: {e}")


def logout(api, ee):
    """Logout from API and EarthExplorer."""
    if api:
        api.logout()
    if ee:
        ee.logout()


def main(username, password, latitude, longitude, start_date, end_date, download_dir):
    # Initialize API and EarthExplorer
    api, ee = initialize_api(username, password)
    if not api or not ee:
        return  # Exit if initialization fails

    # Search for scenes
    scenes = search_scenes(api, latitude, longitude, start_date, end_date)

    if scenes:
        # Print keys of the first scene to inspect structure
        print("Scene keys:", scenes[0].keys())

        # Find the most recent scene based on acquisition date
        try:
            most_recent_scene = max(scenes, key=lambda x: x["acquisition_date"])
            print(
                f"Most recent scene ID: {most_recent_scene['entity_id']}, Date: {most_recent_scene['acquisition_date']}"
            )

            # Download the most recent scene
            download_scene(ee, most_recent_scene["entity_id"], download_dir)
        except KeyError as e:
            print(f"Key error: {e}. Check scene data structure.")
    else:
        print("No scenes found.")

    # Ensure proper logout
    logout(api, ee)


if __name__ == "__main__":
    # Define search parameters
    latitude = 30.033333  # Cairo, Egypt
    longitude = 31.233334
    start_date = "2023-01-01"
    end_date = "2023-12-31"

    # Specify the output directory for downloads
    download_dir = os.path.join(os.getcwd(), "downloads")  # Default download directory
    # download_dir = "/path/to/your/custom/download/location"  # Optionally customize download location

    # Run the main function
    main(USERNAME, PASSWORD, latitude, longitude, start_date, end_date, download_dir)
