"""
Very laggy when using larger images
"""
import PySimpleGUI as sg
from PIL import Image, ImageFilter, ImageOps
from io import BytesIO

def main():
    image_path = sg.popup_get_file('Open',no_window=True)
    control_col = sg.Column([
        [sg.Frame('Blur', layout=[[sg.Slider(range=(0, 10), orientation='h', key='blur')]])],
        [sg.Frame('Contrast', layout=[[sg.Slider(range=(0, 10), orientation='h', key='contrast')]])],
        [sg.Checkbox('Emboss', key='emboss'), sg.Checkbox('Contour', key='contour')],
        [sg.Checkbox('Flip X', key='flipx'), sg.Checkbox('Flip Y', key='flipy')],
        [sg.Button('Save Image', key='save')]
    ])
    image_col = sg.Column([[sg.Image(image_path,key='image')]])
    layout = [[control_col, image_col]]
    window = sg.Window("Image Editor", layout, size=(800, 800))

    def update_image(original, blur, contrast, emboss, contour, flipx, flipy):
        global image
        image = original.filter(ImageFilter.GaussianBlur(blur))
        image = image.filter(ImageFilter.UnsharpMask(contrast))
        if emboss:
            image = image.filter(ImageFilter.EMBOSS())
        if contour:
            image = image.filter(ImageFilter.CONTOUR())
        if flipx:
            image = ImageOps.mirror(image)
        if flipy:
            image = ImageOps.flip(image)

        bio = BytesIO()
        image.save(bio, format="PNG")
        window['image'].update(data=bio.getvalue())

    original = Image.open(image_path)
    while True:
        event, values = window.read(timeout=10)
        if event == sg.WIN_CLOSED: break

        update_image(original,
                     values['blur'],
                     values['contrast'],
                     values['emboss'],
                     values['contour'],
                     values['flipx'], values['flipy'])

        if event == "save":
            save_path = sg.popup_get_file('Save',save_as=True,no_window=True) + '.png'
            image.save(save_path,"PNG")

    window.close()


if __name__ == '__main__':
    main()
