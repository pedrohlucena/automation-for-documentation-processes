import PySimpleGUI as sg

class Popup:
    def mount_send_discord_message_popup(self, pr_url):
        column_to_be_centered = [
            [sg.Text('Link da PR:', size=(45, 1), justification="center")],
            [sg.Text(
                pr_url, 
                tooltip=pr_url, 
                enable_events=True, 
                size=(140, 1), 
                justification="center",
                key=f'URL {pr_url}')],
            [sg.Text('A pr já foi revisada? Posso mandar a mensagem no discord pro pessoal?', size=(60, 1), justification="center")],
            [sg.Button("Sim"), sg.Button("Não")]
        ]

        layout = [
            [sg.VPush()],
            [sg.Push(), sg.Column(column_to_be_centered,element_justification='c'), sg.Push()],
            [sg.VPush()]
        ]

        window = sg.Window("Pó manda?", layout)

        return window

    def mount_conflict_popup(self):
        column_to_be_centered = [
            [sg.Text(
                'Já resolveu os conflitos? Posso terminar de fazer a subida?', 
                size=(50, 1), 
                justification="center")
            ], 
            [sg.Button("Sim"), sg.Button("Não")]
        ]

        layout = [
            [sg.VPush()],
            [sg.Push(), sg.Column(column_to_be_centered,element_justification='c'), sg.Push()],
            [sg.VPush()]
        ]

        window = sg.Window("Conflitos na subida...", layout)

        return window