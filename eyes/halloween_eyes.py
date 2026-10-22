
import io
import random
import time
import requests
from PIL import Image, ImageDraw

# BUSY Bar connected over USB
API = "http://10.0.4.20/api"
APP = "halloween_eyes"
W, H = 72, 16

session = requests.Session()

def make_frame(pupil_x=0, blink=False, glow=255):
    img = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(img)

    # Two wide, blood-red eye shapes
    eyes = [(5, 7, 30, 14), (41, 7, 66, 14)]

    for left, top, right, bottom in eyes:
        if blink:
            d.line((left + 3, 10, right - 3, 10),
                   fill=(glow, 0, 0), width=2)
            continue

        # Red glow-like outer layers
        d.ellipse((left - 2, top - 2, right + 2, bottom + 2),
                  fill=(35, 0, 0))
        d.ellipse((left, top, right, bottom),
                  fill=(glow, 8, 12))

        # Dark pupil moves across each eye
        cx = (left + right) // 2 + pupil_x
        cy = (top + bottom) // 2
        d.ellipse((cx - 4, cy - 3, cx + 4, cy + 3),
                  fill=(8, 0, 0))

        # Tiny blood-red highlight
        d.point((cx - 2, cy - 2), fill=(255, 100, 100))

    # PNG must be uploaded as a full-screen image
    out = io.BytesIO()
    img.save(out, format="PNG")
    return out.getvalue()

def show_frame(png, index):
    filename = f"eyes{index % 4}.png"

    r = session.post(
        f"{API}/assets/upload",
        params={"application_name": APP, "file": filename},
        data=png,
        headers={"Content-Type": "application/octet-stream"},
        timeout=5,
    )
    r.raise_for_status()

    payload = {
        "application_name": APP,
        "elements": [{
            "id": "eyes",
            "type": "image",
            "display": "front",
            "path": filename,
            "x": 0,
            "y": 0,
        }],
    }

    r = session.post(
        f"{API}/display/draw",
        json=payload,
        timeout=5,
    )
    r.raise_for_status()

def main():
    print("Halloween eyes running. Press Ctrl+C to stop.")
    frame = 0

    try:
        while True:
            # Slowly stare left, center, right, then dart around
            for offset in [-3, -2, 0, 2, 3, 0,
                           random.choice([-3, 3]), 0]:
                glow = random.randint(190, 255)
                show_frame(make_frame(offset, glow=glow), frame)
                frame += 1
                time.sleep(random.uniform(0.12, 0.24))

            # Occasionally blink
            if random.random() < 0.45:
                show_frame(make_frame(blink=True), frame)
                frame += 1
                time.sleep(0.12)

    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    main()

