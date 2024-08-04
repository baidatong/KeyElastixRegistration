from kivy.uix.floatlayout import FloatLayout
from kivy.uix.filechooser import FileChooserListView ,FileChooserIconView
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.app import App



class Filechooser(FloatLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.file_chooser = FileChooserIconView(dirselect = True)

        self.file_chooser.path = './'
        self.btn_pop_downloader = Button(text='Select',
                               font_size = 20,
                               size=["100dp","50dp"],
                               size_hint = [None,None],
                               state = 'down',
                               pos = ["0dp","0dp"],
                            )
        self.btn_pop_downloader.bind(on_press = self.get_file)
        self.btn_pop_downloader.bind(on_release= self.set_file)
        self.content_pop_download = BoxLayout(orientation='vertical',pos = ['0dp',"0dp"],size_hint = [0.8,0.9])
        self.content_pop_download.add_widget(self.file_chooser)
        self.content_pop_download.add_widget(self.btn_pop_downloader)
        print("root window:")
        print(self.get_root_window())
        self.pop_downloader = Popup(title ='Load file',
                                content =self.content_pop_download,
                                size_hint=(0.9, 0.9),auto_dismiss = 'False')

    def open_Popup(self):
        self.pop_downloader.open()
        print("popup01:")
        print(self)
        print(self.pop_downloader)
    def get_file(self,instance):

        print(self.file_chooser.selection)
        self.image1_name = self.file_chooser.selection
    def set_file(self,instance):
        print(self.file_chooser.selection)
        print("popup02:")
        print(self)

        print(self.pop_downloader)
        self.pop_downloader.dismiss()
        App.get_running_app().sm_all[self.next_sm].RegScreen01.file_path = self.file_chooser.selection
        App.get_running_app().sm_all[self.next_sm].RegScreen01.load_image()
        App.get_running_app().sm.current = self.next_sm
        #App.get_running_app().sm.current.dismiss()
    def get_next_sm(self,next_sm):
        self.next_sm = next_sm