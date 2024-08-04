from kivy.uix.image import Image
from kivy.core.window import Window
from random import random
from kivy.graphics import Color, Rectangle, Point
from kivy.uix.label import Label

class MyImage(Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._keyboard = Window.request_keyboard(
            self._keyboard_closed, self, 'text')
        self.coordinates_select = (None,None)
        self.pre_ud = None
        self.pre_touch = None
        if self._keyboard.widget:
            # If it exists, this widget is a VKeyboard object which you can use
            # to change the keyboard layout.
            pass
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
    def del_select(self,record):
        group = record['group']
        self.canvas.remove_group(group)

    def plot_select(self,  record):  #绘制button
        ud_group_record = record['ud_group_record']
        record_touch = record['pre_touch']
        num = record['num']
        # print('record _detect_button:')
        with self.canvas:
            pointsize = 40
            Color(ud_group_record['color'], 1, 1, mode='hsv')
            lines = [
              #   Rectangle(pos=(record_touch.x, self.pos[1]), size=(1, self.height), group=ud_group_record['group']),
              #   Rectangle(pos=(self.pos[0], record_touch.y), size=(self.width, 1), group=ud_group_record['group']),
              #   Point(pos=(record_touch.x, record_touch.y), source='particle.png', pointsize=pointsize, group=ud_group_record['group'])
                Rectangle(pos=(record_touch.x, record_touch.y), size=(10, 10),group=record['group'])
            ]
            return lines
    def on_touch_down(self, touch):
        # 只在鼠标左键点击时获取坐标
        pass
        return   # 返回True表示我们已处理事件
    def on_touch_up(self, touch):
        if touch.button == 'left':
            if self.collide_point(*touch.pos):
                # win = self.height
                if self.pre_ud is not None:
                   ud = self.pre_ud
                   self.canvas.remove_group(ud['group'])
                   self.remove_widget(ud['label'])
                ud = touch.ud
                ud['group']  = str(touch.uid)
                if 'pressure' in touch.profile:
                    ud['pressure'] = touch.pressure
                    #pointsize = self.normalize_pressure(touch.pressure)
                ud['color'] = random()
                ud['lines'] = self.plot_coordinate(ud, touch)

                ud['label'] = Label(size_hint=(None, None))
                self.update_touch_label(ud['label'], touch)
                self.add_widget(ud['label'])
                touch.grab(self)
                self.pre_ud = ud
                self.pre_touch = touch
                self.coordinates_select = [touch.x, touch.y]
                return self
    def plot_coordinate(self,ud,touch_pre):
        with self.canvas:
            pointsize = 15
            Color(ud['color'], 1, 1, mode='hsv', group=ud['group'])
            lines = [
                Rectangle(pos=(touch_pre.x, self.pos[1]), size=(1, self.height), group=ud['group']),
                Rectangle(pos=(self.pos[0], touch_pre.y), size=(self.width, 1), group=ud['group']),
                Point(pos=(touch_pre.x, touch_pre.y), source='particle.png', pointsize=pointsize, group=ud['group'])
            ]
            return lines
    def update_touch_label(self, label, touch):
        label.text = 'ID: %s\nPos: (%d, %d)\nClass: %s' % (
            touch.id, touch.x, touch.y, touch.__class__.__name__)
        label.texture_update()
        label.pos = touch.pos
        label.size = label.texture_size[0] + 20, label.texture_size[1] + 20

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        print('The key', keycode, 'have been pressed')
        print(' - text is %r' % text)
        print(' - modifiers are %r' % modifiers)
        # Keycode is composed of an integer + a string
        # If we hit escape, release the keyboard
        if keycode[1] == 'escape':
            keyboard.release()
        if keycode[1] =='lctrl':
            touch = self.on_touch_down()
            print(f"Mouse clicked at: {touch.x}, {touch.y}")
       # Return True to accept the key. Otherwise, it will be used by
        # the system.
        return True
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None
