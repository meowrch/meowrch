import os
import sys
from PIL import Image


wallpaper_path = None
monitor_size = "1920x1080"

black_list = [
    "gif", "swf", "bmp", "htt", "tif", "x",
    "htm", "ini", "txt", "mp4", "js", "html",
    "css", "ucs2le", "avi", "md", "cpyr"
]


if len(sys.argv) <= 1:
    raise SystemExit("specify the path to the wallpaper")
else:
    wallpaper_path = sys.argv[1]
    print(f"Wallpaper Path: {wallpaper_path}")
    print(f"Image Size: {monitor_size}\n")


for wallpaper in os.listdir(wallpaper_path):
    path = os.path.join(wallpaper_path, wallpaper)
    if os.path.isfile(path):
        wallpaper_extension = wallpaper.split('.')[-1].lower()

        # Remove blacklist extensions
        if wallpaper_extension in black_list:
            remove_ext = os.path.join(wallpaper_path, wallpaper)
            print(f"Remove invalid extension: {wallpaper}")
            os.remove(remove_ext)
            continue

        image = Image.open(path)
        (width, height) = image.size
        wallpaper_size = f"{width}x{height}"

        if wallpaper_size != monitor_size:
            os.remove(path)
            print(f"{wallpaper} removed. size: {wallpaper_size}")
        
