try:
	import requests
	import webbrowser
	from urllib.parse import urlencode
	from kivy.core.text import LabelBase
	from kivy.uix.videoplayer import VideoPlayer
	from kivy.uix.modalview import ModalView
	from kivy.uix.image import AsyncImage
	import kivy
	from kivy.app import App
	from kivy.uix.boxlayout import BoxLayout
	from kivy.uix.label import Label
	from kivy.uix.button import Button
	from kivy.uix.textinput import TextInput
	from kivy.uix.scrollview import ScrollView
	from kivy.uix.popup import Popup
	from kivy.uix.gridlayout import GridLayout
except:
	print('导入模块失败，可在终端输入:pip install kivy requests')
# Register the font before using it
LabelBase.register(name="NotoSansCJK", fn_regular="fonts/NotoSansCJK-Regular.ttc")  # Path to your font file

class Movie:
    def __init__(self, id, name, pic):
        self.id = id
        self.name = name
        self.pic = pic

def search(name, page):
    try:
        if page == 1:
            url = 'https://ikan234.com/index.php/ajax/suggest'
            data = {
                'mid': (page - 1) * 10 + 1,
                'wd': name,
                'limit': '10',
                'timestamp': '1743741123771'
            }
            resp = requests.get(url, params=data)
            movies = resp.json().get('list', [])
            return [Movie(m['id'], m['name'], m['pic']) for m in movies]
        else:
            url = f'https://ikan234.com/search/{urlencode({"wd": name}).strip("wd=")}----------{str(page)}---.html'
            resp = requests.get(url)
            content = resp.content.decode()
            content = content.split('<ul class="stui-vodlist__media col-pd clearfix">')[1].split('</ul>')[0].split('</li>')
            info = []
            for i in content:
                try:
                    name = i.split('title="')[1].split('"')[0]
                    id = i.split('href="/vod/')[1].split('.html')[0]
                    pic = i.split('data-original="')[1].split('"')[0]
                    info.append(Movie(id=id, name=name, pic=pic))
                except:
                    continue
            return info
    except Exception as e:
        show_error(f"搜索出错：{e}")
        return []

def get_movie(id, th, set_):
    url2 = f'https://ikan234.com/play/{id}-{th}-{set_}.html'
    resp2 = requests.get(url2)
    return resp2.content.decode().split('url":"')[3].split('"')[0].replace('\\', '')

def show_error(message):
    popup = Popup(title='error',
                  content=Label(text=message, font_name="NotoSansCJK"),
                  size_hint=(0.8, 0.3))
    popup.open()

def show_input(title, callback):
    layout = BoxLayout(orientation='vertical')
    title = Label(text=title, font_name="fonts/NotoSansCJK-Regular.ttc", font_size="18sp", size_hint_y=None)
    input_field = TextInput(multiline=False, font_name="NotoSansCJK",height=40)
    submit = Button(text='确定', font_name="NotoSansCJK")
    layout.add_widget(title)
    layout.add_widget(input_field)
    layout.add_widget(submit)
    popup = Popup(title='',content=layout, size_hint=(0.8, 0.4))

    def on_submit(instance):
        value = input_field.text
        popup.dismiss()
        callback(value)

    submit.bind(on_press=on_submit)
    popup.open()

class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.movies = []
        self.name_input = TextInput(hint_text='请输入剧名', size_hint_y=None, height=80, font_name="NotoSansCJK")
        self.page_input = TextInput(hint_text='页码', size_hint_y=None, height=80, font_name="NotoSansCJK")
        self.add_widget(self.name_input)
        self.add_widget(self.page_input)
        self.search_btn = Button(text='搜索', size_hint_y=None, height=80, font_name="NotoSansCJK")
        self.search_btn.bind(on_press=self.do_search)
        self.add_widget(self.search_btn)

        self.scroll = ScrollView()
        self.result_layout = GridLayout(cols=1, size_hint_y=None)
        self.result_layout.bind(minimum_height=self.result_layout.setter('height'))
        self.scroll.add_widget(self.result_layout)
        self.add_widget(self.scroll)

    def do_search(self, instance):
        name = self.name_input.text.strip()
        page = self.page_input.text.strip()
        if not page.isdigit():
            show_error('页码必须是数字')
            return

        self.movies = search(name, int(page))
        self.result_layout.clear_widgets()
        for idx, m in enumerate(self.movies):
            item_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=100, padding=5, spacing=10)

            # 添加封面图
            image = AsyncImage(source=m.pic, size_hint=(None, 1), width=70)
            
            # 添加标题按钮
            btn = Button(text=f"{idx + 1}. {m.name}", font_name="NotoSansCJK", size_hint_x=1)
            btn.bind(on_press=lambda btn, idx=idx: self.select_movie(idx))

            item_layout.add_widget(image)
            item_layout.add_widget(btn)
            self.result_layout.add_widget(item_layout)
    def select_movie(self, index):
	    movie = self.movies[index]
	
	    def on_set_entered(set_):
	        if not set_.isdigit():
	            show_error("集数无效")
	            return
	
	        def on_th_entered(th):
	            if not th.isdigit() or not (1 <= int(th) <= 4):
	                show_error("线路必须为1-4之间")
	                return
	            url = get_movie(movie.id, int(th), set_)
	                
	
	            webbrowser.open(url)
	
	        show_input("请输入线路 (1-4)", on_th_entered)
	
	    show_input("请输入集数 (电影填1)", on_set_entered)
class IkanApp(App):
    def build(self):
        return MainScreen()

if __name__ == '__main__':
    IkanApp().run()