import streamlit
from streamlit_webrtc import webrtc_streamer
import av
import asyncio
# from streamlit.web import bootstrap
import streamlit as st
import threading
import time
import cv2
import yaml

from modules.MP4Writer import MP4Writer
from modules.apply_filters import apply_filters

lock = threading.Lock()

# We'll store both unfiltered and filtered images in the shared container
img_container = {
    "unfiltered": None,
    "filtered": None
}


def video_frame_callback(frame):
    """
    Returns the 'filtered' frame for display,
    but also stores both original & filtered into the global container.
    """
    # Original (unfiltered)
    unfiltered_img = frame.to_ndarray(format="bgr24")

    # Apply filters
    filtered_img = apply_filters(unfiltered_img)

    # Save both to container
    with lock:
        img_container["unfiltered"] = unfiltered_img
        img_container["filtered"] = filtered_img

    # Return the filtered frame for display
    return av.VideoFrame.from_ndarray(filtered_img, format="bgr24")

def run_streamlit_app(rtc_configuration):
    """
    Start the WebRTC streaming and use 'video_frame_callback' to process frames.
    """
    ctx = webrtc_streamer(
        key="example",
        video_frame_callback=video_frame_callback,
        rtc_configuration=rtc_configuration
    )
    return ctx

if __name__ == "__main__":
    # ---------------------
    # 1) Load config
    # ---------------------
    with open("configs/config.yaml", "r") as f:
        config = yaml.safe_load(f)

    rtc_configuration = config["rtc_configuration"]
    video_config = config["video"]
    default_width = video_config["default_width"]
    default_height = video_config["default_height"]
    fps = video_config["fps"]
    chunk_duration = video_config["chunk_duration"]

    # ---------------------
    # 2) Start WebRTC
    # ---------------------
    ctx = run_streamlit_app(rtc_configuration)

    # We'll keep track of two MP4Writer objects
    writer_unfiltered = None
    writer_filtered = None

    # Start with guessed size
    width = default_width
    height = default_height

    while True:
        # If the WebRTC connection is not playing, break
        if not ctx.state.playing:
            break

        # Grab both frames from the shared container
        with lock:
            unfiltered_img = img_container["unfiltered"]
            filtered_img = img_container["filtered"]

        if unfiltered_img is None or filtered_img is None:
            # No frame yet, just wait a bit
            time.sleep(0.05)
            continue

        # First time we have a frame => figure out actual dimensions
        if writer_unfiltered is None or writer_filtered is None:
            height, width = unfiltered_img.shape[:2]

            # Create two writers, e.g. prefix them differently:
            writer_unfiltered = MP4Writer(
                width=width,
                height=height,
                fps=fps,
                chunk_duration=chunk_duration,
                base_name="unfiltered_"  # hypothetical argument
            )
            writer_filtered = MP4Writer(
                width=width,
                height=height,
                fps=fps,
                chunk_duration=chunk_duration,
                base_name="filtered_"  # hypothetical argument
            )

        # Write frames to each file
        writer_unfiltered.write_frame(unfiltered_img)
        writer_filtered.write_frame(filtered_img)

        # Maybe rotate (i.e., create new chunk files) if chunk_duration has passed
        writer_unfiltered.maybe_rotate_file()
        writer_filtered.maybe_rotate_file()

        time.sleep(0.05)

    # ---------------------
    # 3) Cleanup
    # ---------------------
    if writer_unfiltered is not None:
        writer_unfiltered.close()
    if writer_filtered is not None:
        writer_filtered.close()

    st.write("Recording finished.")

