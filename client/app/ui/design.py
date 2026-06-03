from tkinter import ttk


WINDOW_BACKGROUND = "#eef2f7"
TEXT_COLOR = "#1f2937"
TITLE_COLOR = "#111827"
SUBTITLE_COLOR = "#64748b"
STATUS_COLOR = "#2563eb"
FORM_BACKGROUND = "#ffffff"
PANEL_BACKGROUND = "#f8fafc"
BORDER_COLOR = "#9caec3"
INPUT_BACKGROUND = "#f9fbff"
HEADER_BACKGROUND = "#0f172a"
HEADER_TEXT = "#ffffff"
ACCENT_COLOR = "#2563eb"
ACCENT_HOVER = "#1d4ed8"
TAB_BACKGROUND = "#e5eaf2"
TAB_SELECTED = "#ffffff"
BUTTON_BACKGROUND = "#e8edf5"
BUTTON_HOVER = "#dbe4f0"


def apply_design(window):
    window.configure(bg=WINDOW_BACKGROUND)
    window.option_add("*selectBackground", ACCENT_COLOR)
    window.option_add("*selectForeground", "#ffffff")

    style = ttk.Style()
    style.theme_use("clam")

    style.configure("TFrame", background=FORM_BACKGROUND)
    style.configure("Header.TFrame", background=HEADER_BACKGROUND)
    style.configure("TLabel", background=FORM_BACKGROUND, foreground=TEXT_COLOR, font=("Segoe UI", 10))
    style.configure("Field.TLabel", background=FORM_BACKGROUND, foreground="#334155", font=("Segoe UI", 10, "bold"))
    style.configure("Header.TLabel", background=HEADER_BACKGROUND, foreground=HEADER_TEXT, font=("Segoe UI", 17, "bold"))
    style.configure("HeaderName.TLabel", background=HEADER_BACKGROUND, foreground="#cbd5e1", font=("Segoe UI", 10))
    style.configure("Title.TLabel", background=WINDOW_BACKGROUND, foreground=TITLE_COLOR, font=("Segoe UI", 21, "bold"))
    style.configure("Subtitle.TLabel", background=WINDOW_BACKGROUND, foreground=SUBTITLE_COLOR, font=("Segoe UI", 10))
    style.configure("Section.TLabel", background=FORM_BACKGROUND, foreground=TITLE_COLOR, font=("Segoe UI", 14, "bold"))

    style.configure(
        "TEntry",
        padding=7,
        fieldbackground=INPUT_BACKGROUND,
        background=INPUT_BACKGROUND,
        insertcolor=TITLE_COLOR,
        selectbackground=ACCENT_COLOR,
        selectforeground="#ffffff",
        bordercolor=BORDER_COLOR,
        lightcolor=BORDER_COLOR,
        darkcolor=BORDER_COLOR,
        relief="solid",
        borderwidth=1,
        foreground=TEXT_COLOR,
    )
    style.map(
        "TEntry",
        fieldbackground=[("focus", "#ffffff")],
        bordercolor=[("focus", ACCENT_COLOR)],
        lightcolor=[("focus", ACCENT_COLOR)],
        darkcolor=[("focus", ACCENT_COLOR)],
    )

    style.configure(
        "TCombobox",
        padding=5,
        fieldbackground=INPUT_BACKGROUND,
        background=INPUT_BACKGROUND,
        bordercolor=BORDER_COLOR,
        lightcolor=BORDER_COLOR,
        darkcolor=BORDER_COLOR,
        arrowcolor=TEXT_COLOR,
        foreground=TEXT_COLOR,
        selectbackground=ACCENT_COLOR,
        selectforeground="#ffffff",
        relief="solid",
        borderwidth=1,
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", INPUT_BACKGROUND), ("focus", "#ffffff")],
        bordercolor=[("focus", ACCENT_COLOR)],
        lightcolor=[("focus", ACCENT_COLOR)],
        darkcolor=[("focus", ACCENT_COLOR)],
    )

    style.configure(
        "TButton",
        padding=(12, 8),
        font=("Segoe UI", 10, "bold"),
        background=BUTTON_BACKGROUND,
        foreground=TITLE_COLOR,
        bordercolor=BORDER_COLOR,
        focusthickness=0,
    )
    style.map(
        "TButton",
        background=[("active", BUTTON_HOVER), ("pressed", BORDER_COLOR)],
        foreground=[("disabled", "#94a3b8")],
    )

    style.configure("TCheckbutton", background=FORM_BACKGROUND, foreground=TEXT_COLOR, font=("Segoe UI", 10))

    style.configure("TNotebook", background=WINDOW_BACKGROUND, borderwidth=0, tabmargins=(0, 0, 0, 0))
    style.configure(
        "TNotebook.Tab",
        padding=(18, 9),
        font=("Segoe UI", 10),
        background=TAB_BACKGROUND,
        foreground=TEXT_COLOR,
        bordercolor=BORDER_COLOR,
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", TAB_SELECTED), ("active", "#f1f5f9")],
        foreground=[("selected", TITLE_COLOR)],
    )

    style.configure(
        "Treeview",
        background="#ffffff",
        fieldbackground="#ffffff",
        foreground=TEXT_COLOR,
        bordercolor=BORDER_COLOR,
        rowheight=28,
        font=("Segoe UI", 10),
    )
    style.configure(
        "Treeview.Heading",
        background=PANEL_BACKGROUND,
        foreground=TITLE_COLOR,
        bordercolor=BORDER_COLOR,
        font=("Segoe UI", 10, "bold"),
        padding=7,
    )
    style.map("Treeview", background=[("selected", ACCENT_COLOR)], foreground=[("selected", "#ffffff")])

    style.configure(
        "Horizontal.TProgressbar",
        background=ACCENT_COLOR,
        troughcolor="#e2e8f0",
        bordercolor=BORDER_COLOR,
        lightcolor=ACCENT_COLOR,
        darkcolor=ACCENT_COLOR,
    )
