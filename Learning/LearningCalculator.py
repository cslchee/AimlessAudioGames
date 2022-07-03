import PySimpleGUI as sg

def create_window(theme,theme_menu):
    sg.theme(theme)
    sg.set_options(font='Franklin 14', button_element_size=(6, 3))
    butt_s = (6, 3)
    layout = [
        [sg.Text(
            '0',
            font='Franklin 16',
            justification='right',
            expand_x=True, pad=(10, 20),
            right_click_menu=theme_menu,
            key='TEXT')
        ],  # or use sg.Push()
        [sg.Button('Clear', expand_x=True), sg.Button('Enter', expand_x=True)],
        [sg.Button('7', size=butt_s), sg.Button('8', size=butt_s), sg.Button('9', size=butt_s),
         sg.Button('*', size=butt_s)],
        [sg.Button('4', size=butt_s), sg.Button('5', size=butt_s), sg.Button('6', size=butt_s),
         sg.Button('/', size=butt_s)],
        [sg.Button('1', size=butt_s), sg.Button('2', size=butt_s), sg.Button('3', size=butt_s),
         sg.Button('-', size=butt_s)],
        [sg.Button('0', expand_x=True), sg.Button('.', size=butt_s), sg.Button('+', size=butt_s)]
    ]
    return sg.Window("Calculator", layout)

def main():
    theme_menu = ['menu',['LightGrey1','dark','DarkGray8','random']]
    window = create_window('LightGrey1',theme_menu)

    current_num = []
    full_operation = []

    while True:
        event, values = window.read()
        if event in theme_menu[1]:
            window.close()
            window = create_window(event, theme_menu)

        if event in ['0','1','2','3','4','5','6','7','8','9']:
            current_num.append(event)
            num_string = ''.join(current_num)
            window["TEXT"].update(num_string)

        if event in ['+','-','/','*']:
            full_operation.append(''.join(current_num))
            current_num = []
            full_operation.append(event)


        if event == "Enter":
            full_operation.append(''.join(current_num))
            window["TEXT"].update(eval(' '.join(full_operation)))
            full_operation = []
            current_num = []

        if event == "Clear":
            current_num = []
            full_operation = []
            window["TEXT"].update('0')

        if event == sg.WIN_CLOSED:
            break
    window.close()

if __name__ == '__main__':
    main()