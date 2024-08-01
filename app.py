'''
FastAPI part of the application
'''
from fastapi import FastAPI, File, Form, UploadFile, Request
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
from PIL import Image
import numpy as np 
import io 
from texture_mapping import image_resize


IMG_FOLDER = os.path.join("static", "IMG")
DATA_FOLDER = os.path.join("static", "data")

ROOM_IMAGE = os.path.join(IMG_FOLDER, "room.jpg")
COLORED_ROOM_PATH = os.path.join(IMG_FOLDER, "colored_room.jpg")
TEXTURED_ROOM_PATH = os.path.join(IMG_FOLDER, "textured_room.jpg")
TEXTURE_PATH = os.path.join(IMG_FOLDER, "texture.jpg")
MASK_PATH = os.path.join(DATA_FOLDER, "image_mask.npy")
CORNERS_PATH = os.path.join(DATA_FOLDER, "corners_estimation.npy")


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "room": ROOM_IMAGE})


@app.get("/redirect-to-texture")
async def redirect_to_texture(request: Request):
    return templates.TemplateResponse("applied_layout.html", {"request": request, "room": ROOM_IMAGE})


@app.post("/prediction")
async def predict_image_room(request: Request, file: UploadFile = File(...), button: str = Form(...)):
    try:
        contents = await file.read()
        op_img = Image.open(io.BytesIO(contents))
        op_img = np.asarray(op_img)

        if op_img.shape[0] > 600:
            op_img = image_resize(op_img, height=600)

        op_img = Image.fromarray(op_img)

        op_img.save(ROOM_IMAGE)
        op_img.save(COLORED_ROOM_PATH)
        op_img.save(TEXTURED_ROOM_PATH)


        if button == "texture":
            return RedirectResponse(url="/textured_room")

        return templates.TemplateResponse("result.html", {"request": request})

    except Exception as e:
        return templates.TemplateResponse("result.html", {"request": request, "err": "Error"})


@app.get("/textured_room")
async def textured_room(request: Request):
    return templates.TemplateResponse("applied_texture.html", {"request": request, "new_room": TEXTURED_ROOM_PATH})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9090)