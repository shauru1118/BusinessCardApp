import base64

with open("static/flag.png", "rb") as image_file:
    encoded = base64.b64encode(image_file.read()).decode("utf-8")
    print(f"data:image/png;base64,{encoded}")
