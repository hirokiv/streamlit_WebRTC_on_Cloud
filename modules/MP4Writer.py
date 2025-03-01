import cv2
import streamlit as st
import time

class MP4Writer:

    def __init__(self, width, height, fps=20, chunk_duration=30):
        """
        width, height: Frame size
        fps: Frames per second (approx)
        chunk_duration: How many seconds per file before rolling over to a new file.
                        If chunk_duration=None, never roll over; just keep writing to one file.
        """
        self.width = width
        self.height = height
        self.fps = fps
        self.chunk_duration = chunk_duration

        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.video_out = None
        self.start_time = None
        self._start_new_file()

    def _start_new_file(self):
        """Open a new MP4 file writer."""
        # Make a filename based on the current timestamp (or any naming scheme you want)
        timestamp = int(time.time())
        filename = f"{timestamp}.mp4"
        st.write(f"Starting new recording file: {filename}")
        self.video_out = cv2.VideoWriter(filename, self.fourcc, self.fps, (self.width, self.height))
        self.start_time = time.time()

    def write_frame(self, frame):
        """Write a single frame to the current MP4 file."""
        self.video_out.write(frame)

    def maybe_rotate_file(self):
        """Check if chunk_duration has elapsed and rotate to a new file if needed."""
        if self.chunk_duration is None:
            return  # not using chunked mode
        elapsed = time.time() - self.start_time
        if elapsed >= self.chunk_duration:
            # Close current file
            self.video_out.release()
            # Start a new file
            self._start_new_file()

    def close(self):
        """Close the writer when we're done."""
        if self.video_out is not None:
            self.video_out.release()
            self.video_out = None
