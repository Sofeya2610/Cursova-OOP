import tkinter as tk
from tkinter import messagebox

from backend_client import GameBackend
import stats  
from pathlib import Path


WORD_LENGTH = 5
MAX_ATTEMPTS = 5
# EXE_PATH = "../build/game_logic.exe"
EXE_PATH = str(Path(__file__).resolve().parents[2] / "build" / "game_logic.exe")

BG_COLOR = "#121213"
CELL_BG = "#3a3a3c"
GREEN = "#538d4e"
YELLOW = "#b59f3b"
GRAY = "#3a3a3c"


class WordleApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Guess the Word (C++ + Python)")
        self.root.geometry("520x780")
        self.root.configure(bg=BG_COLOR)


        self.backend = GameBackend(EXE_PATH)

        self.current_attempt = 0
        self.game_running = False
        self.hint_used = False
        self.difficulty = "EASY"  # EASY або HARD
        self.username = ""

        # статистика поточної сесії
        self.games_played = 0
        self.games_won = 0
        self.score = 0

        self.menu_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.game_frame = tk.Frame(self.root, bg=BG_COLOR)

        self.create_menu_ui()
        self.create_game_ui()

        self.show_menu()


    def create_menu_ui(self):
        title = tk.Label(
            self.menu_frame,
            text="WORD GUESS GAME",
            font=("Arial", 28, "bold"),
            bg=BG_COLOR,
            fg="white",
            pady=30
        )
        title.pack()

        # ім'я користувача
        name_label = tk.Label(
            self.menu_frame,
            text="Player name:",
            font=("Arial", 12),
            bg=BG_COLOR,
            fg="white"
        )
        name_label.pack(pady=(10, 5))

        self.name_entry = tk.Entry(
            self.menu_frame,
            font=("Arial", 14),
            width=20,
            justify="center",
            bg="#272728",
            fg="white",
            insertbackground="white",
            border=0
        )
        self.name_entry.pack(pady=5)

        # Вибір складності
        diff_label = tk.Label(
            self.menu_frame,
            text="Choose difficulty:",
            font=("Arial", 14),
            bg=BG_COLOR,
            fg="white",
            pady=10
        )
        diff_label.pack()

        self.menu_mode_var = tk.StringVar(value="EASY")

        diff_frame = tk.Frame(self.menu_frame, bg=BG_COLOR)
        diff_frame.pack(pady=5)

        tk.Radiobutton(
            diff_frame, text="Easy", variable=self.menu_mode_var, value="EASY",
            font=("Arial", 12),
            bg=BG_COLOR, fg="white", selectcolor=BG_COLOR,
            activebackground=BG_COLOR, activeforeground="white"
        ).pack(side=tk.LEFT, padx=10)

        tk.Radiobutton(
            diff_frame, text="Hard", variable=self.menu_mode_var, value="HARD",
            font=("Arial", 12),
            bg=BG_COLOR, fg="white", selectcolor=BG_COLOR,
            activebackground=BG_COLOR, activeforeground="white"
        ).pack(side=tk.LEFT, padx=10)

        btn_frame = tk.Frame(self.menu_frame, bg=BG_COLOR)
        btn_frame.pack(pady=40)

        start_btn = tk.Button(
            btn_frame,
            text="START GAME",
            command=self.start_from_menu,
            font=("Arial", 14, "bold"),
            bg="#565758",
            fg="white",
            width=15,
            height=2,
            activebackground="#818384"
        )
        start_btn.grid(row=0, column=0, padx=5, pady=5)

        stats_btn = tk.Button(
            btn_frame,
            text="SHOW STATS",
            command=self.show_stats_menu,
            font=("Arial", 14, "bold"),
            bg="#565758",
            fg="white",
            width=15,
            height=2
        )
        stats_btn.grid(row=1, column=0, padx=5, pady=5)

        exit_btn = tk.Button(
            btn_frame,
            text="EXIT",
            command=self.root.destroy,
            font=("Arial", 14, "bold"),
            bg="#565758",
            fg="white",
            width=15,
            height=2
        )
        exit_btn.grid(row=2, column=0, padx=5, pady=5)

        self.menu_stats_label = tk.Label(
            self.menu_frame,
            text="",
            font=("Arial", 11),
            bg=BG_COLOR,
            fg="white",
            justify="left",
            wraplength=480
        )
        self.menu_stats_label.pack(pady=10)

    def start_from_menu(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Name", "Please enter your name.")
            return
        self.username = name
        self.difficulty = self.menu_mode_var.get()
        self.show_game()
        self.start_new_game()

    def show_menu(self):
        self.game_frame.pack_forget()
        self.menu_frame.pack(fill=tk.BOTH, expand=True)

    def show_game(self):
        self.menu_frame.pack_forget()
        self.game_frame.pack(fill=tk.BOTH, expand=True)

    def show_stats_menu(self):
        """
        Показати статистику гравця з stats.json у головному меню.
        Ім'я береться з поля name_entry.
        """
        stats_dict = stats.load_stats_dict()

        player_name = self.name_entry.get().strip()
        if not player_name:
            self.menu_stats_label.config(
                text="Enter player name to see statistics.",
                fg="orange"
            )
            return

        player_data = stats_dict.get("players", {}).get(player_name)

        if not player_data:
            self.menu_stats_label.config(
                text=f"Статистику для цього користувача не знайдено: {player_name}",
                fg="orange"
            )
            return

        msg = (
            f"Player: {player_name}\n"
            f"Games: {player_data.get('games', 0)} | "
            f"Wins: {player_data.get('wins', 0)} | "
            f"Score: {player_data.get('score', 0)}\n"
            f"Avg attempts: {player_data.get('avg_attempts', 0.0)} | "
            f"Last attempts: {player_data.get('last_attempts', 0)}\n"
            f"Last difficulty: {player_data.get('last_difficulty', '-')}\n"
            f"Last play: {player_data.get('last_play', '-')}"
        )

        self.menu_stats_label.config(text=msg, fg="white")


    def create_game_ui(self):
        title_label = tk.Label(
            self.game_frame,
            text="GUESS THE WORD",
            font=("Arial", 26, "bold"),
            bg=BG_COLOR,
            fg="white",
            pady=20
        )
        title_label.pack()

        # Кнопка повернення до меню
        top_btn_frame = tk.Frame(self.game_frame, bg=BG_COLOR)
        top_btn_frame.pack(pady=5)

        back_btn = tk.Button(
            top_btn_frame,
            text="MENU",
            command=self.back_to_menu,
            font=("Arial", 10, "bold"),
            bg="#565758",
            fg="white",
            width=8,
            height=1
        )
        back_btn.pack()

        self.grid_frame = tk.Frame(self.game_frame, bg=BG_COLOR)
        self.grid_frame.pack(pady=10)

        self.cells = []
        for r in range(MAX_ATTEMPTS):
            row_cells = []
            for c in range(WORD_LENGTH):
                cell = tk.Label(
                    self.grid_frame,
                    text="",
                    font=("Arial", 24, "bold"),
                    width=3,
                    height=1,
                    fg="white",
                    bg=CELL_BG,
                    highlightthickness=2,
                    highlightbackground="#565758"
                )
                cell.grid(row=r, column=c, padx=5, pady=5)
                row_cells.append(cell)
            self.cells.append(row_cells)

        self.entry = tk.Entry(
            self.game_frame,
            font=("Arial", 20),
            width=10,
            justify="center",
            insertbackground="white",
            bg="#272728",
            fg="white",
            border=0
        )
        self.entry.pack(pady=20)
        self.entry.bind("<Return>", lambda event: self.submit_guess())
        self.entry.focus_set()

        btn_frame = tk.Frame(self.game_frame, bg=BG_COLOR)
        btn_frame.pack(pady=10)

        self.submit_btn = tk.Button(
            btn_frame,
            text="GUESS",
            command=self.submit_guess,
            font=("Arial", 12, "bold"),
            bg="#565758",
            fg="white",
            width=10,
            height=2,
            activebackground="#818384"
        )
        self.submit_btn.grid(row=0, column=0, padx=5)

        hint_btn = tk.Button(
            btn_frame,
            text="HINT",
            command=self.request_hint,
            font=("Arial", 12, "bold"),
            bg="#565758",
            fg="white",
            width=10,
            height=2
        )
        hint_btn.grid(row=0, column=1, padx=5)

        new_game_btn = tk.Button(
            btn_frame,
            text="NEW GAME",
            command=self.start_new_game,
            font=("Arial", 12, "bold"),
            bg="#565758",
            fg="white",
            width=10,
            height=2
        )
        new_game_btn.grid(row=0, column=2, padx=5)

        self.status_label = tk.Label(
            self.game_frame,
            text="",
            font=("Arial", 12),
            bg=BG_COLOR,
            fg="white"
        )
        self.status_label.pack(pady=5)

        self.hint_label = tk.Label(
            self.game_frame,
            text="",
            font=("Arial", 11, "italic"),
            bg=BG_COLOR,
            fg="#AAAAAA"
        )
        self.hint_label.pack(pady=5)

        self.score_label = tk.Label(
            self.game_frame,
            text="Score: 0",
            font=("Arial", 12, "bold"),
            bg=BG_COLOR,
            fg="white"
        )
        self.score_label.pack(pady=5)

    def back_to_menu(self):
        self.backend.stop()
        self.show_menu()


    def start_new_game(self):
        self.backend.stop()

        self.current_attempt = 0
        self.game_running = False
        self.hint_used = False
        self.entry.delete(0, tk.END)
        self.submit_btn.config(state=tk.NORMAL)
        self.hint_label.config(text="")
        self.status_label.config(text="", fg="white")

        for r in range(MAX_ATTEMPTS):
            for c in range(WORD_LENGTH):
                self.cells[r][c].config(text="", bg=CELL_BG)

        # перевіряємо, що exe існує
        if not Path(EXE_PATH).exists():
            self.status_label.config(
                text=f"C++ executable not found: {EXE_PATH}\nBuild the project to create game_logic.exe",
                fg="red"
            )
            return

        # створюємо backend з правильним шляхом і запускаємо процес
        self.backend = GameBackend(EXE_PATH)
        ok = self.backend.start_process()
        if not ok:
            self.status_label.config(
                text=f"Error starting C++ process. Check executable: {EXE_PATH}",
                fg="red"
            )
            return

        self.backend.set_mode(self.difficulty)

        # START
        resp_start = self.backend.start_game()

        if "READY" in resp_start:
            self.game_running = True
            self.status_label.config(
                text=f"Player: {self.username} | Mode: {self.difficulty}. Enter a 5-letter word.",
                fg="white"
            )
        else:
            self.status_label.config(
                text="Error starting game (no READY).",
                fg="red"
            )

    def submit_guess(self):
        if not self.game_running:
            return

        guess = self.entry.get().strip().upper()
        if len(guess) != WORD_LENGTH:
            self.status_label.config(
                text=f"Word must have {WORD_LENGTH} letters.",
                fg="orange"
            )
            return

        response = self.backend.send_guess(guess)

        # DEBUG: show raw backend response
        # (debug removed) don't overwrite status label with raw backend response

        if "FEEDBACK" in response or "WIN" in response:
            parts = response.split()
            feedback = parts[-1]

            self.show_feedback(guess.upper(), feedback)

            if "WIN" in response:
                self.game_running = False
                self.submit_btn.config(state=tk.DISABLED)

                self.games_played += 1
                self.games_won += 1

                if self.current_attempt == 0:
                    gain = 5
                elif self.current_attempt == 1:
                    gain = 4
                elif self.current_attempt == 2:
                    gain = 3
                else:
                    gain = 1

                if self.hint_used and gain > 1:
                    gain -= 1

                self.score += gain
                self.score_label.config(text=f"Score: {self.score}")

                # оновляємо JSON-статистику
                attempts = self.current_attempt + 1
                try:
                    stats.update_player_stats(self.username or "ANON", True, self.difficulty, attempts)
                except Exception as e:
                    print("Failed to update stats:", e)

                self.status_label.config(
                    text=f"{self.username}, YOU WIN! Word: {guess.upper()}  (+{gain} score)",
                    fg=GREEN
                )
                self.hint_label.config(text="")
            else:
                self.current_attempt += 1
                self.entry.delete(0, tk.END)

                if self.current_attempt >= MAX_ATTEMPTS:
                    self.game_running = False
                    self.submit_btn.config(state=tk.DISABLED)

                    self.games_played += 1

                    attempts = MAX_ATTEMPTS
                    stats.update_player_stats(
                        player_name=self.username,
                        won=False,
                        attempts=attempts,
                        score_change=0,
                        difficulty=self.difficulty
                    )

                    self.status_label.config(
                        text="GAME OVER. No attempts left. Try again!",
                        fg="red"
                    )
                    self.hint_label.config(text="")
        elif "INVALID" in response:
            self.status_label.config(
                text="Invalid input.",
                fg="orange"
            )

    def request_hint(self):
        if not self.game_running:
            return
        if self.hint_used:
            self.hint_label.config(text="You have already used the hint.")
            return

        response = self.backend.request_hint()

        if response.startswith("HINT"):
            parts = response.split()
            if len(parts) == 3:
                pos_str, letter = parts[1], parts[2]
                try:
                    pos = int(pos_str)
                except ValueError:
                    self.hint_label.config(text="No hint available.")
                    return

                self.hint_used = True
                self.hint_label.config(
                    text=f"Hint: letter at position {pos + 1} is {letter}"
                )
            else:
                self.hint_label.config(text="No hint available.")
        else:
            self.hint_label.config(text="No hint available.")

    def show_feedback(self, guess: str, feedback: str):
        row = self.current_attempt
        for i in range(WORD_LENGTH):
            char = guess[i] if i < len(guess) else ""
            code = feedback[i] if i < len(feedback) else "B"

            color = GRAY
            if code == "G":
                color = GREEN
            elif code == "Y":
                color = YELLOW

            self.cells[row][i].config(text=char, bg=color)


if __name__ == "__main__":
    root = tk.Tk()
    app = WordleApp(root)
    root.mainloop()