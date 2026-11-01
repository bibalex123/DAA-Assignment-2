import math
import tkinter as tk
from tkinter import ttk, messagebox

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
except ImportError:
    Figure = None
    FigureCanvasTkAgg = None


APP_TITLE = "Smart Password Security Estimator"
LOWER = "abcdefghijklmnopqrstuvwxyz"
UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGITS = "0123456789"
SYMBOLS = "!@#$%^&*()-_=+[]{};:,.?/"

def format_duration(seconds):
    """Format a non-negative duration into a readable estimate."""
    if seconds < 1:
        return f"{seconds:.2g} seconds"
    units = [
        ("year", 365.25 * 24 * 3600),
        ("day", 24 * 3600),
        ("hour", 3600),
        ("minute", 60),
        ("second", 1),
    ]
    for name, size in units:
        if seconds >= size:
            value = seconds / size
            if value >= 100:
                return f"{value:,.0f} {name}{'' if value == 1 else 's'}"
            return f"{value:,.2f} {name}{'' if value == 1 else 's'}"
    return "Less than one second"


def analyze_password(password, guesses_per_second=1_000_000_000):
    """
    Estimate the theoretical search space from character categories.
    This is a rough model, not a real cracking benchmark or guarantee.
    """
    if not password:
        raise ValueError("Enter a sample password first.")
    if guesses_per_second <= 0:
        raise ValueError("Guessing rate must be greater than zero.")

    pool = 0
    categories = {
        "Lowercase letters": any(c in LOWER for c in password),
        "Uppercase letters": any(c in UPPER for c in password),
        "Digits": any(c in DIGITS for c in password),
        "Special characters": any(c in SYMBOLS for c in password),
        "Other characters": any(not (c in LOWER or c in UPPER or c in DIGITS or c in SYMBOLS)
                                for c in password),
    }
    if categories["Lowercase letters"]:
        pool += len(LOWER)
    if categories["Uppercase letters"]:
        pool += len(UPPER)
    if categories["Digits"]:
        pool += len(DIGITS)
    if categories["Special characters"]:
        pool += 32  # Approximate common printable ASCII symbol set
    if categories["Other characters"]:
        # Treat other Unicode characters as a broad, approximate category.
        pool += 100

    # If a password includes no recognized category, use a conservative fallback.
    pool = max(pool, 1)
    length = len(password)
    log10_space = length * math.log10(pool)
    entropy_bits = length * math.log2(pool)

    # Keep the calculation in log-space so very large spaces do not overflow.
    log10_seconds = log10_space - math.log10(guesses_per_second)
    if log10_seconds > 300:
        seconds = float("inf")
        duration = "Far beyond practical timescales"
    else:
        seconds = 10 ** log10_seconds
        duration = format_duration(seconds)

    # Heuristic strength label; this is not a formal password audit.
    if length < 8 or entropy_bits < 28:
        strength = "Very weak"
    elif length < 10 or entropy_bits < 40:
        strength = "Weak"
    elif length < 12 or entropy_bits < 60:
        strength = "Moderate"
    elif length < 16 or entropy_bits < 80:
        strength = "Strong"
    else:
        strength = "Very strong"

    return {
        "length": length,
        "pool": pool,
        "categories": categories,
        "entropy_bits": entropy_bits,
        "log10_space": log10_space,
        "log10_seconds": log10_seconds,
        "duration": duration,
        "strength": strength,
        "guesses_per_second": guesses_per_second,
    }


class PasswordEstimatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1120x780")
        self.root.minsize(940, 680)
        self.root.configure(bg="#101722")

        self.bg = "#101722"
        self.panel = "#182333"
        self.panel2 = "#202e40"
        self.text = "#edf4ff"
        self.muted = "#a8b7cc"
        self.accent = "#4dd0e1"
        self.green = "#67e8a5"
        self.orange = "#ffca70"
        self.red = "#ff7d8a"

        self.password_var = tk.StringVar()
        self.rate_var = tk.StringVar(value="1,000,000,000")
        self.show_password_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="Enter a sample password and select Analyze.")
        self.demo_target_var = tk.StringVar(value="c")
        self.demo_index = 0
        self.demo_candidates = list("abcdef")
        self.demo_running = False

        self._configure_styles()
        self._build_ui()
        self._draw_chart()

    def _configure_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TCombobox", fieldbackground=self.panel2, background=self.panel2,
                        foreground=self.text, arrowcolor=self.text)
        style.configure("TProgressbar", troughcolor=self.panel2, background=self.accent,
                        bordercolor=self.panel2, lightcolor=self.accent, darkcolor=self.accent)

    def _label(self, parent, text, size=10, color=None, bold=False):
        return tk.Label(parent, text=text, bg=parent.cget("bg"),
                        fg=color or self.text, font=("Segoe UI", size, "bold" if bold else "normal"))

    def _build_ui(self):
        header = tk.Frame(self.root, bg=self.bg)
        header.pack(fill="x", padx=24, pady=(18, 10))
        tk.Label(header, text="🔐  SMART PASSWORD SECURITY ESTIMATOR",
                 bg=self.bg, fg=self.text, font=("Segoe UI", 19, "bold")).pack(anchor="w")
        tk.Label(header, text="DAA project • Brute-force search-space analysis • Educational simulation",
                 bg=self.bg, fg=self.muted, font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 0))

        top = tk.Frame(self.root, bg=self.bg)
        top.pack(fill="x", padx=24, pady=8)

        input_card = tk.Frame(top, bg=self.panel, padx=18, pady=16)
        input_card.pack(side="left", fill="both", expand=True, padx=(0, 8))
        self._label(input_card, "PASSWORD SAMPLE", 10, self.accent, True).pack(anchor="w")
        row = tk.Frame(input_card, bg=self.panel)
        row.pack(fill="x", pady=(8, 10))
        self.password_entry = tk.Entry(row, textvariable=self.password_var, show="•",
                                       bg=self.panel2, fg=self.text, insertbackground=self.text,
                                       relief="flat", font=("Consolas", 13))
        self.password_entry.pack(side="left", fill="x", expand=True, ipady=9, padx=(0, 8))
        tk.Checkbutton(row, text="Show", variable=self.show_password_var, command=self._toggle_password,
                       bg=self.panel, fg=self.muted, selectcolor=self.panel2, activebackground=self.panel,
                       activeforeground=self.text).pack(side="right")
        self._label(input_card, "Guessing-rate assumption (guesses/second)", 9, self.muted).pack(anchor="w")
        rate_row = tk.Frame(input_card, bg=self.panel)
        rate_row.pack(fill="x", pady=(5, 10))
        self.rate_entry = tk.Entry(rate_row, textvariable=self.rate_var, bg=self.panel2, fg=self.text,
                                   insertbackground=self.text, relief="flat", font=("Segoe UI", 10))
        self.rate_entry.pack(side="left", fill="x", expand=True, ipady=6)
        tk.Button(rate_row, text="Analyze", command=self.analyze, bg="#087e8b", fg="white",
                  activebackground="#0b9cab", activeforeground="white", relief="flat",
                  font=("Segoe UI", 10, "bold"), padx=20, pady=7).pack(side="left", padx=(8, 0))
        tk.Label(input_card, text="Use a sample password, not one you actively use.",
                 bg=self.panel, fg=self.orange, font=("Segoe UI", 9)).pack(anchor="w")

        result_card = tk.Frame(top, bg=self.panel, padx=18, pady=16, width=320)
        result_card.pack(side="right", fill="both", padx=(8, 0))
        result_card.pack_propagate(False)
        self._label(result_card, "ESTIMATED STRENGTH", 10, self.accent, True).pack(anchor="w")
        self.strength_label = tk.Label(result_card, text="—", bg=self.panel, fg=self.text,
                                       font=("Segoe UI", 22, "bold"))
        self.strength_label.pack(anchor="w", pady=(8, 2))
        self.strength_bar = ttk.Progressbar(result_card, maximum=5, value=0, length=240)
        self.strength_bar.pack(fill="x", pady=(3, 12))
        self.entropy_label = tk.Label(result_card, text="Entropy: —", bg=self.panel, fg=self.muted,
                                      font=("Segoe UI", 10))
        self.entropy_label.pack(anchor="w")
        self.space_label = tk.Label(result_card, text="Search space: —", bg=self.panel, fg=self.muted,
                                    font=("Segoe UI", 10))
        self.space_label.pack(anchor="w", pady=(5, 0))
        self.time_label = tk.Label(result_card, text="Estimated time: —", bg=self.panel, fg=self.muted,
                                   font=("Segoe UI", 10), wraplength=270, justify="left")
        self.time_label.pack(anchor="w", pady=(5, 0))

        middle = tk.Frame(self.root, bg=self.bg)
        middle.pack(fill="both", expand=True, padx=24, pady=(8, 8))

        chart_card = tk.Frame(middle, bg=self.panel, padx=12, pady=12)
        chart_card.pack(side="left", fill="both", expand=True, padx=(0, 8))
        tk.Label(chart_card, text="SEARCH-SPACE GROWTH", bg=self.panel, fg=self.text,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.chart_area = tk.Frame(chart_card, bg=self.panel)
        self.chart_area.pack(fill="both", expand=True, pady=(4, 0))

        info_card = tk.Frame(middle, bg=self.panel, padx=16, pady=14, width=335)
        info_card.pack(side="right", fill="y", padx=(8, 0))
        info_card.pack_propagate(False)
        tk.Label(info_card, text="CHARACTER ANALYSIS", bg=self.panel, fg=self.text,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.category_labels = {}
        for name in ["Lowercase letters", "Uppercase letters", "Digits", "Special characters", "Other characters"]:
            label = tk.Label(info_card, text="○  " + name, bg=self.panel, fg=self.muted,
                             font=("Segoe UI", 10), anchor="w")
            label.pack(fill="x", pady=5)
            self.category_labels[name] = label
        tk.Frame(info_card, bg=self.panel2, height=1).pack(fill="x", pady=10)
        tk.Label(info_card, text="DAA COMPLEXITY", bg=self.panel, fg=self.accent,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Label(info_card, text="N = Rᴸ\nR = character-set size\nL = password length\n\nWorst-case time: O(N)\nAuxiliary space: O(1)*",
                 bg=self.panel, fg=self.text, justify="left", font=("Consolas", 10)).pack(anchor="w", pady=(7, 0))
        tk.Label(info_card, text="*For a generator-based search that stores one candidate at a time.",
                 bg=self.panel, fg=self.muted, wraplength=290, justify="left",
                 font=("Segoe UI", 8)).pack(anchor="w", pady=(8, 0))

        demo = tk.Frame(self.root, bg=self.panel, padx=18, pady=12)
        demo.pack(fill="x", padx=24, pady=(0, 12))
        demo_header = tk.Frame(demo, bg=self.panel)
        demo_header.pack(fill="x")
        tk.Label(demo_header, text="SAFE BRUTE-FORCE CONCEPT DEMO",
                 bg=self.panel, fg=self.text, font=("Segoe UI", 11, "bold")).pack(side="left")
        tk.Label(demo_header, text="Toy alphabet only • Does not test your password",
                 bg=self.panel, fg=self.orange, font=("Segoe UI", 9)).pack(side="right")
        demo_row = tk.Frame(demo, bg=self.panel)
        demo_row.pack(fill="x", pady=(8, 0))
        tk.Label(demo_row, text="Toy target:", bg=self.panel, fg=self.muted).pack(side="left")
        self.demo_target_entry = tk.Entry(demo_row, textvariable=self.demo_target_var, width=5,
                                          bg=self.panel2, fg=self.text, insertbackground=self.text,
                                          relief="flat")
        self.demo_target_entry.pack(side="left", padx=(6, 12), ipady=4)
        tk.Button(demo_row, text="Next candidate", command=self.demo_next, bg=self.panel2,
                  fg=self.text, activebackground="#31445b", relief="flat", padx=10, pady=5).pack(side="left")
        tk.Button(demo_row, text="Reset demo", command=self.demo_reset, bg=self.panel2,
                  fg=self.text, activebackground="#31445b", relief="flat", padx=10, pady=5).pack(side="left", padx=6)
        self.demo_output = tk.Label(demo_row, text="Candidate sequence: a → b → c → d → e → f",
                                    bg=self.panel, fg=self.accent, font=("Consolas", 10))
        self.demo_output.pack(side="left", padx=12)
        self.status = tk.Label(self.root, textvariable=self.status_var, bg=self.bg, fg=self.muted,
                               font=("Segoe UI", 9), anchor="w")
        self.status.pack(fill="x", padx=24, pady=(0, 12))

    def _draw_chart(self):
        if Figure is None:
            tk.Label(self.chart_area, text="Install matplotlib to display the graph.\nRun: pip install matplotlib",
                     bg=self.panel, fg=self.orange, font=("Segoe UI", 10)).pack(expand=True)
            return
        self.figure = Figure(figsize=(6.0, 3.1), dpi=100, facecolor=self.panel)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor(self.panel)
        lengths = list(range(1, 17))
        values = [length * math.log10(94) for length in lengths]
        self.ax.plot(lengths, values, marker="o", linewidth=2)
        self.ax.set_title("Illustrative search space (94 possible characters)", color=self.text, fontsize=10)
        self.ax.set_xlabel("Password length", color=self.muted)
        self.ax.set_ylabel("log₁₀(number of candidates)", color=self.muted)
        self.ax.tick_params(colors=self.muted, labelsize=8)
        for spine in self.ax.spines.values():
            spine.set_color("#53657a")
        self.ax.grid(True, alpha=0.2)
        self.figure.tight_layout()
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.chart_area)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.canvas.draw()

    def _toggle_password(self):
        self.password_entry.configure(show="" if self.show_password_var.get() else "•")

    def analyze(self):
        password = self.password_var.get()
        try:
            rate_text = self.rate_var.get().replace(",", "").replace(" ", "")
            rate = float(rate_text)
            result = analyze_password(password, rate)
        except (ValueError, OverflowError) as exc:
            messagebox.showerror("Cannot analyze", str(exc) or "Please check the inputs.")
            return

        self.strength_label.configure(text=result["strength"])
        strength_values = {"Very weak": 1, "Weak": 2, "Moderate": 3, "Strong": 4, "Very strong": 5}
        self.strength_bar["value"] = strength_values[result["strength"]]
        strength_colors = {"Very weak": self.red, "Weak": self.orange, "Moderate": "#ffe680",
                           "Strong": self.green, "Very strong": self.accent}
        self.strength_label.configure(fg=strength_colors[result["strength"]])
        self.entropy_label.configure(text=f"Estimated entropy: {result['entropy_bits']:.1f} bits")
        if result["log10_space"] < 15:
            search_space = f"{10 ** result['log10_space']:,.0f} candidates"
        else:
            search_space = f"About 10^{result['log10_space']:.1f} candidates"
        self.space_label.configure(text=f"Search space: {search_space}")
        self.time_label.configure(text=f"Estimated exhaustive-search time: {result['duration']}")
        for name, active in result["categories"].items():
            marker = "●" if active else "○"
            color = self.green if active else self.muted
            self.category_labels[name].configure(text=f"{marker}  {name}", fg=color)
        self.status_var.set(
            f"Analyzed {result['length']} characters using a character pool of {result['pool']}. "
            "Results are theoretical estimates, not a security guarantee."
        )

    def demo_next(self):
        target = self.demo_target_var.get().strip()
        if len(target) != 1 or target not in self.demo_candidates:
            messagebox.showinfo("Toy demo", "Choose one target character from a, b, c, d, e, or f.")
            return
        if self.demo_index >= len(self.demo_candidates):
            self.demo_output.configure(text="All toy candidates checked. Reset to replay.")
            return
        candidate = self.demo_candidates[self.demo_index]
        self.demo_index += 1
        if candidate == target:
            self.demo_output.configure(text=f"Try {self.demo_index}: '{candidate}' — MATCH FOUND")
            self.status_var.set("Toy demonstration finished. This sequence is separate from the password analyzer.")
        else:
            self.demo_output.configure(text=f"Try {self.demo_index}: '{candidate}' — no match")
            self.status_var.set(f"Toy candidate '{candidate}' tested; move to the next candidate.")

    def demo_reset(self):
        self.demo_index = 0
        self.demo_output.configure(text="Candidate sequence: a → b → c → d → e → f")
        self.status_var.set("Toy demo reset. Press Next candidate to step through the sequence.")


def main():
    root = tk.Tk()
    PasswordEstimatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
