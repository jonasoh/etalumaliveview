from etalumacontrol import LumaScope, EtalumaStage
import PySimpleGUI as sg
import numpy as np
import cv2

RESOLUTION = 640


def get_image_bytes(scope):
    '''
    Return the current image buffer as PNG-encoded bytes.
    '''
    npbuf = np.frombuffer(scope.get_raw_image_buffer(), dtype=np.uint8)
    npbuf = np.resize(npbuf, (RESOLUTION, RESOLUTION, 3))
    cvimg = cv2.cvtColor(npbuf, cv2.COLOR_RGB2BGR)
    return cv2.imencode('.png', cvimg)[1].tobytes()


if __name__ == '__main__':
    splash = sg.Window('Etaluma Live View',
                        layout=[[sg.T('Initializing...', font="Arial 20")]])
    splash.read(timeout=0)

    with EtalumaStage() as stage, LumaScope(resolution=RESOLUTION) as scope:
        splash.close()

        frame = get_image_bytes(scope) # data to initialize the layout with
        scope.gain = 20
        scope.set_led(15)
        scope.shutter = 70

        layout = [
            [sg.Image(data=frame, key='LSVIEW')],
            [sg.T('X:'), sg.I('-60.0', key='X', size=(6,1)), 
                sg.T('Y:'), sg.I('-30.0', key='Y', size=(6,1)), 
                sg.T('Z:'), sg.I('7.982', key='Z', size=(6,1)), 
                sg.B('Move')],
            [sg.T('LED brightness:'), sg.I('15', key='LED'), sg.B('Set', key='SetLED')], 
            [sg.T('Global gain:'), sg.I('20', key='GAIN'), sg.B('Set', key='SetGain')],
            [sg.T('Shutter (ms):'), sg.I('70', key='SHUTTER'), sg.B('Set', key='SetShutter')]
        ]

        window = sg.Window('Etaluma Live View', layout)

        while True:
            event, value = window.read(timeout=0)

            frame = get_image_bytes(scope)
            window['LSVIEW'].update(data=frame)

            if event == 'Exit' or event == sg.WIN_CLOSED:
                break
            elif event == 'Move':
                for axis in ['X', 'Y', 'Z']:
                    if value[axis] is not None:
                        stage.move(axis, float(value[axis]), blocking=False)
            elif event == 'SetLED':
                scope.set_led(brightness=float(value['LED']))
            elif event == 'SetGain':
                scope.gain = float(value['GAIN'])
            elif event == 'SetShutter':
                scope.shutter = float(value['SHUTTER'])

        window.close()
