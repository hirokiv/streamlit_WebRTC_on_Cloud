import streamlit
from streamlit_webrtc import webrtc_streamer
import av
import asyncio
# from streamlit.web import bootstrap
import streamlit as st
from modules.MP4Writer import MP4Writer
import threading
import time
import cv2



lock = threading.Lock()
img_container = {"img": None}


def video_frame_callback(frame):
    img = frame.to_ndarray(format="bgr24")
    with lock:
        img_container["img"] = img

    return frame


RTC_CONFIGURATION = {
    "iceServers": [
        {
            "urls": ["stun:stun.l.google.com:19302"]
        },
        {
            "urls": ["turn:34.31.136.194:3478?transport=udp"],
            "username": "demo",
            "credential": "pass123"
        }
    ]
}



def run_streamlit_app():
    ctx = webrtc_streamer(key="example", 
                    video_frame_callback=video_frame_callback,
                    rtc_configuration=RTC_CONFIGURATION)

    return ctx

if __name__ == "__main__":
    ctx = run_streamlit_app()

    # We'll need the frame size. We can't know it until we see the first frame.
    width = 640  # default guess
    height = 480

    # We won't create the writer until we see at least one frame with known dimensions:
    writer = None


    while True:
        # If the WebRTC connection is not playing, break
        if not ctx.state.playing:
            break

        with lock:
            img = img_container["img"]

        if img is None:
            # No frame yet, just continue
            time.sleep(0.05)
            continue

        # If we haven't initialized the writer, do it now
        if writer is None:
            height, width = img.shape[:2]  # get actual frame size from the first frame
            # e.g., chunk_duration=30 means every 30s we start a new .mp4
            writer = MP4Writer(width=width, height=height, fps=5, chunk_duration=30)

        # 2. Write the frame to the current file
        writer.write_frame(img)

        # 3. Optionally rotate the file if 30s have passed
        writer.maybe_rotate_file()

        # 4. Do your histogram logic
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        time.sleep(0.05)  # minor pause so we don't spin too fast

    # Outside the while loop => webrtc streaming ended
    if writer is not None:
        writer.close()
    st.write("Recording finished.")
