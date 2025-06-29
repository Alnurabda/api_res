import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

USERNAME = os.getenv("HIKVISION_USERNAME")
PASSWORD = os.getenv("HIKVISION_PASSWORD")
DEVICE_IP = os.getenv("DEVICE_IP")
PORT = os.getenv("PORT", "80")

# Base URL for the Hikvision device API
BASE_URL = f"http://{DEVICE_IP}:{PORT}/ISAPI"

# Setup session
session = requests.Session()
session.auth = (USERNAME, PASSWORD)
session.headers.update({"Content-Type": "application/json"})

def get_camera_metadata():
    """
    Retrieve metadata from the Hikvision surveillance system.
    """
    endpoint = f"{BASE_URL}/Streaming/channels"
    try:
        response = session.get(endpoint, timeout=5)
        response.raise_for_status()
        data = response.json()
        return parse_metadata(data)
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to connect to {DEVICE_IP}: {e}")
        return None

def parse_metadata(data):
    """
    Parse the metadata from JSON response.
    """
    cameras = []
    channels = data.get("StreamingChannelList", {}).get("StreamingChannel", [])
    for channel in channels:
        cam_info = {
            "id": channel.get("id"),
            "name": channel.get("channelName"),
            "enabled": channel.get("enabled"),
            "videoCodecType": channel.get("video", {}).get("videoCodecType"),
            "resolution": channel.get("video", {}).get("videoResolution")
        }
        cameras.append(cam_info)
    return cameras

def save_to_json(data, filename="camera_metadata.json"):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"[INFO] Metadata saved to {filename}")

if __name__ == "__main__":
    print(f"[INFO] Connecting to device at {DEVICE_IP}")
    metadata = get_camera_metadata()
    if metadata:
        save_to_json(metadata)
