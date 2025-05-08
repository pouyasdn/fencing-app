import arabic_reshaper
from bidi.algorithm import get_display
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

def farsi(text: str) -> str:
    return get_display(arabic_reshaper.reshape(text))

def fa_label(text, **kwargs):
    return Label(
        text=farsi(text),
        font_name="fonts/BNazanin.ttf",
        halign="right", valign="middle",
        **kwargs
    )

def fa_button(text, **kwargs):
    btn = Button(
        text=farsi(text),
        font_name="fonts/BNazanin.ttf",
        halign="center",
        **kwargs
    )
    # شفاف‌تر برای خوانایی متن
    btn.background_normal = ''
    btn.background_down = ''
    btn.background_color = [1, 1, 1, 0.5]
    return btn

def fa_popup(title, content, **kwargs):
    return Popup(
        title=farsi(title),
        title_align='center',
        content=content,
        **kwargs
    )

def generate_matches(members: list[str]) -> list[tuple[str,str]]:
    return [(members[i], members[j])
            for i in range(len(members))
            for j in range(i+1, len(members))]

class TournamentApp(App):
    def build(self):
        self.members = []
        self.matches = []
        self.match_index = 0
        self.results = {}  # {(p1,p2): winner}

        root = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.input_field = TextInput(
            hint_text=farsi("نام شرکت‌کننده را وارد کنید"),
            multiline=False, font_name="fonts/BNazanin.ttf")
        root.add_widget(self.input_field)

        root.add_widget(fa_button("افزودن", size_hint_y=None, height=40,
                                  on_press=self.add_member))

        self.members_label = fa_label("اعضا:\n")
        self.members_label.bind(size=self.members_label.setter('text_size'))
        root.add_widget(self.members_label)

        root.add_widget(fa_button("شروع مسابقات",
                                  size_hint_y=None, height=50,
                                  on_press=self.start_matches))
        return root

    def add_member(self, _):
        name = self.input_field.text.strip()
        if name and name not in self.members:
            self.members.append(name)
            self.input_field.text = ''
            self.members_label.text = farsi("اعضا:\n" + "\n".join(self.members))

    def start_matches(self, _):
        if len(self.members) < 2:
            return
        self.matches = generate_matches(self.members)
        self.match_index = 0
        self.results.clear()
        self.show_next_match()

    def show_next_match(self):
        if self.match_index >= len(self.matches):
            return self.show_match_summary()

        p1, p2 = self.matches[self.match_index]
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        layout.add_widget(fa_label(f"{p1} در برابر {p2}"))

        btn1 = fa_button(f"{p1} برنده است")
        btn1.bind(on_release=lambda _, w=p1: self._on_select(w))
        layout.add_widget(btn1)

        btn2 = fa_button(f"{p2} برنده است")
        btn2.bind(on_release=lambda _, w=p2: self._on_select(w))
        layout.add_widget(btn2)

        self.current_popup = fa_popup("نتیجه مسابقه", layout,
                                     size_hint=(0.8, 0.6))
        self.current_popup.open()

    def _on_select(self, winner: str):
        p1, p2 = self.matches[self.match_index]
        self.results[(p1, p2)] = winner
        self.current_popup.dismiss()
        self.match_index += 1
        self.show_next_match()

    def show_match_summary(self):
        layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        # اول بار هیچ امتیازی نداشتیم؛ رنکینگ بعد از ویرایش نمایش داده می‌شود
        for p1, p2 in self.matches:
            key = (p1, p2)
            # اگر کاربر قبلاً انتخاب نکرده، پیش‌فرض را p1 قرار نمی‌دهیم
            current = self.results.get(key)

            row = BoxLayout(orientation='horizontal',
                            size_hint_y=None, height=50, spacing=5)
            row.add_widget(fa_label(f"{p1} در برابر {p2}", size_hint_x=0.5))

            btn1 = fa_button(p1, size_hint_x=0.25)
            btn2 = fa_button(p2, size_hint_x=0.25)

            # ست کردن رنگ برای انتخاب فعلی
            if current == p1:
                btn1.background_color = [0,1,0,0.5]
            elif current == p2:
                btn2.background_color = [0,1,0,0.5]

            # callback تغییر برنده
            def make_cb(key, winner, b_win, b_lose):
                def cb(_):
                    self.results[key] = winner
                    # بازنویسی رنگ‌ها
                    b_win.background_color = [0,1,0,0.5]
                    b_lose.background_color = [1,1,1,0.5]
                return cb

            btn1.bind(on_release=make_cb(key, p1, btn1, btn2))
            btn2.bind(on_release=make_cb(key, p2, btn2, btn1))

            row.add_widget(btn1)
            row.add_widget(btn2)
            layout.add_widget(row)

        # دکمهٔ نمایش رنکینگ
        rank_btn = fa_button("نمایش رنکینگ", size_hint_y=None, height=50)
        rank_btn.bind(on_release=lambda _: self.show_ranking())
        layout.add_widget(rank_btn)

        scroll = ScrollView(size_hint=(1,1))
        scroll.add_widget(layout)

        self.current_popup = fa_popup("خلاصه مسابقات", scroll,
                                     size_hint=(0.95,0.95))
        self.current_popup.open()

    def show_ranking(self):
        # محاسبهٔ امتیازها از روی self.results
        scores = {name: 0 for name in self.members}
        for winner in self.results.values():
            scores[winner] += 1

        sorted_players = sorted(scores.items(), key=lambda x: -x[1])
        layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        for idx, (name, _) in enumerate(sorted_players, start=1):
            row = BoxLayout(orientation='horizontal',
                            size_hint_y=None, height=40, spacing=5)
            lbl_num = Label(text=f"{idx}.",
                            size_hint_x=0.1, halign="left", valign="middle")
            lbl_num.bind(size=lbl_num.setter('text_size'))

            lbl_name = fa_label(name, size_hint_x=0.9)
            row.add_widget(lbl_num)
            row.add_widget(lbl_name)
            layout.add_widget(row)

        scroll = ScrollView(size_hint=(1,1))
        scroll.add_widget(layout)

        fa_popup("رنکینگ نهایی", scroll, size_hint=(0.8,0.8)).open()

if __name__ == '__main__':
    TournamentApp().run()
