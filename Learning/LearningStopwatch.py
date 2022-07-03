import PySimpleGUI as sg
from time import time

def create_window():
    sg.theme('black')
    layout = [
        [sg.Image('X.png', size=(50, 50), pad=0, enable_events=True, key="CLOSE"), sg.Push()],
        [sg.VPush()],
        [sg.Text('', font='Arial 35', key="TIME")],
        [
            sg.Button('Start', button_color=('#FF0000', '#FFFFFF'), border_width=0, key="STARTSTOP"),
            sg.Button('Lap', button_color=('#FF0000', '#FFFFFF'), border_width=0, key="LAP", visible=False)
        ],
        [sg.Column([[]],key="LAPS")],
        [sg.VPush()]
    ]
    return sg.Window(
        "Stopwatch",
        layout,
        size=(450, 450),
        no_titlebar=True,
        element_justification='center')

def main():
    window = create_window()

    start_time = 0
    active = False
    lap_amount = 1

    while True:
        event, values = window.read(timeout=10)

        if event == "STARTSTOP":
            if active:
                active = False
                window['STARTSTOP'].update('Reset')
                window['LAP'].update(visible=False)
            else:
                if start_time > 0:
                    window.close()
                    window = create_window()
                    start_time = 0
                    lap_amount = 1
                else:
                    start_time = time()
                    active = True
                    window['STARTSTOP'].update('Stop')
                    window['LAP'].update(visible=True)

        if active:
            elapsed_time = round(time() - start_time,1)
            window['TIME'].update(elapsed_time)

        if event == 'LAP':
            window.extend_layout(window['LAPS'], [[sg.Text(lap_amount),sg.VSeparator(),sg.Text(elapsed_time)]])
            lap_amount += 1






        if event in (sg.WIN_CLOSED, 'CLOSE'):
            break
    window.close()

if __name__ == '__main__':
    main()