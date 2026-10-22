
from PIL import Image
from busylib import BusyBar, converter, types

APP = "elle-woods"
HOST = "10.0.4.20"

# BUSY Bar front display dimensions
WIDTH, HEIGHT = 72, 16

QUOTE = "what, like it's hard?"

def prepare_portrait(source="elle.png", output="elle_pixel.png"):
    """Create a tiny, pixelated portrait."""
    image = Image.open(source).convert("RGB")

    # Crop to a square around the center
    side = min(image.size)
    left = (image.width - side) // 2
    top = (image.height - side) // 2
    image = image.crop((left, top, left + side, top + side))

    # Pixel-art effect, then enlarge with nearest-neighbor scaling
    image = image.resize((8, 8), Image.Resampling.NEAREST)
    image = image.resize((16, 16), Image.Resampling.NEAREST)
    image.save(output)
    return output

def main():
    portrait_path = prepare_portrait()

    with BusyBar(HOST) as bar:
        version = bar.version()
        print(f"Connected to BUSY Bar: {version.api_semver}")

        # Upload the portrait asset
        with open(portrait_path, "rb") as file:
            filename, payload = converter.convert_for_storage(
                portrait_path, file.read()
            )

        bar.assets_upload(
            application_name=APP,
            filename=filename,
            data=payload,
        )

        # Draw portrait at the left and quote in the remaining space
        bar.display_draw(
            types.DisplayElements(
                application_name=APP,
                elements=[
                    types.ImageElement(
                        id="elle",
                        type="image",
                        x=0,
                        y=0,
                        path=filename,
                        display=types.DisplayName.FRONT,
                    ),
                    types.TextElement(
                        id="quote",
                        type="text",
                        x=18,
                        y=4,
                        width=54,
                        text=QUOTE,
                        font="tiny",
                        color="#FF69B4",
                        scroll_rate=1200,
                        scroll_start_delay=500,
                        scroll_repeat_delay=500,
                        display=types.DisplayName.FRONT,
                    ),
                ],
            )
        )

        print("Elle Woods is ready. Press Ctrl+C to exit.")

if __name__ == "__main__":
    main()

