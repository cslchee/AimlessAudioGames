import PySimpleGUI as sg

def main():
    layout = [
        [
            sg.Input(key='-INPUT-'),
            sg.Spin(['km to mile','kg to pound','sec to min'],key='-UNITS-'),
            sg.Button('Convert',key='-CONVERT-')
        ],
        [sg.Text('Output: '), sg.Text('Awaiting Orders', key='-OUTPUT-')]
    ]
    window = sg.Window("Converter",layout)
    while True:
        event, values = window.read()

        if event == '-CONVERT-':
            input_value = values['-INPUT-']
            if input_value.isnumeric():
                match values['-UNITS-']:
                    case 'km to mile':
                        output = round(float(input_value) * 0.6214,2)
                        output_string = f'{input_value} km is equal to {output} miles'
                    case 'kg to pound':
                        output = round(float(input_value) * 2.20462, 2)
                        output_string = f'{input_value} kg is equal to {output} pounds'
                    case 'sec to min':
                        output = round(float(input_value) / 60, 2)
                        output_string = f'{input_value} sec is equal to {output} min'
                window['-OUTPUT-'].update(output_string)
            else:
                window['-OUTPUT-'].update("Please enter a number!")

        if event == sg.WIN_CLOSED:
            break
    window.close()


if __name__ == '__main__':
    main()
