import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class GUI:
    def __init__(self) -> None:
        self.root = ctk.CTk()
        self.root.geometry("300x300")
        self.center_window(self.root)
        self.position = {"pady": 12, "padx": 10}
        self._url = ctk.StringVar(self.root)
        self._save = ctk.BooleanVar(self.root)
        self._alert = ctk.BooleanVar(self.root)
        self.create_widgets()

    @property
    def url(self):
        return self._url.get()

    @property
    def save(self):
        return self._save.get()

    @property
    def alert(self):
        return self._alert.get()

    def center_window(self, window):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        x = (screen_width - window.winfo_reqwidth()) // 2
        y = (screen_height - window.winfo_reqheight()) // 2

        window.geometry(f"+{x}+{y}")

    def close(self, *args: any) -> None:
        self.root.destroy()

    def create_widgets(self):
        frame = ctk.CTkFrame(master=self.root)
        frame.pack(
            pady=20,
            padx=60,
            fill="both",
            expand=True,
        )

        label = ctk.CTkLabel(
            master=frame,
            text="Wklej URL:",
        )
        label.pack(**self.position)

        url_box = ctk.CTkEntry(
            master=frame,
            textvariable=self._url,
        )
        url_box.pack(**self.position)

        default_url_checkbox = ctk.CTkCheckBox(
            master=frame,
            text="Zapisz jako domyślny",
            variable=self._save,
        )
        default_url_checkbox.pack(**self.position)

        alert_checkbox = ctk.CTkCheckBox(
            master=frame,
            text="Włącz powiadomienie",
            variable=self._alert,
        )
        alert_checkbox.pack(**self.position)

        button = ctk.CTkButton(
            master=frame,
            text="Szukaj",
            command=self.close,
        )
        button.pack(**self.position)

        self.root.bind("<Return>", self.close)
        self.root.mainloop()
