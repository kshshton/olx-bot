import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


def url_input():
    root = ctk.CTk()
    root.geometry("300x250")
    center_window(root)
    position = {"pady": 12, "padx": 10}

    frame = ctk.CTkFrame(master=root)
    frame.pack(
        pady=20,
        padx=60,
        fill="both",
        expand=True,
    )

    def close(*args: any) -> None:
        root.destroy()

    url = ctk.StringVar(root)

    label = ctk.CTkLabel(
        master=frame,
        text="Wklej URL:",
    )
    label.pack(**position)

    url_box = ctk.CTkEntry(
        master=frame,
        textvariable=url,
    )
    url_box.pack(**position)

    save_url_as_default = ctk.BooleanVar(root)

    checkbox = ctk.CTkCheckBox(
        master=frame,
        text="Zapisz",
        variable=save_url_as_default,
    )
    checkbox.pack(**position)

    button = ctk.CTkButton(
        master=frame,
        text="Szukaj",
        command=close,
    )
    button.pack(**position)

    root.bind("<Return>", close)
    root.mainloop()

    return {
        "url": url.get(),
        "save": save_url_as_default.get(),
    }


def center_window(window):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width - window.winfo_reqwidth()) // 2
    y = (screen_height - window.winfo_reqheight()) // 2

    window.geometry(f"+{x}+{y}")
