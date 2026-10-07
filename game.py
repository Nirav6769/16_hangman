import random

from stats import SessionStats
from words import HINTS, WORDS


class HangmanGame:
    DIFFICULTIES = {
        "easy": {"lives": 8, "win_points": 5, "hint_penalty": 1},
        "medium": {"lives": 6, "win_points": 10, "hint_penalty": 2},
        "hard": {"lives": 4, "win_points": 15, "hint_penalty": 3},
    }

    def __init__(self):
        # Session-level state: survives across rounds.
        self.score = 0
        self.streak = 0
        self.stats = SessionStats()

        # Selection/session state.
        self.category = "technology"
        self.difficulty = "medium"

        # Round-level state: reset by start_round().
        self.secret = ""
        self.guessed = set()
        self.wrong = set()
        self.lives = 0
        self.hint_used = False

    def start_round(self):
        """Reset only round state; keep score, streak, and session stats."""
        self.secret = random.choice(WORDS[self.category])
        self.guessed.clear()
        self.wrong.clear()
        self.lives = self.DIFFICULTIES[self.difficulty]["lives"]
        self.hint_used = False

    def masked(self):
        return " ".join(ch if ch in self.guessed else "_" for ch in self.secret)

    def won(self):
        return all(ch in self.guessed for ch in set(self.secret))

    def guess(self, letter):
        """Process exactly one letter. Invalid/repeated input changes nothing."""
        letter = letter.strip().lower()

        if len(letter) != 1 or not letter.isalpha():
            return "Invalid input: enter one letter."

        # A letter is an attempted guess whether it was right or wrong.
        if letter in self.guessed or letter in self.wrong:
            return f"'{letter}' was already guessed. No life lost."

        if letter in self.secret:
            self.guessed.add(letter)
            return f"Correct: '{letter}'."

        self.wrong.add(letter)
        self.lives -= 1
        return f"Wrong: '{letter}'. One life lost."

    def use_hint(self):
        """Use at most one hint per round and apply the difficulty-specific penalty."""
        if self.hint_used:
            return "Hint already used this round."

        self.hint_used = True
        penalty = self.DIFFICULTIES[self.difficulty]["hint_penalty"]
        self.score = max(0, self.score - penalty)
        return HINTS.get(self.secret, "No hint available.")

    def _finish_round(self, won):
        """Update session score/streak/statistics exactly once for a completed round."""
        if won:
            self.streak += 1
            settings = self.DIFFICULTIES[self.difficulty]
            points = settings["win_points"] + self.lives + self.streak
            self.score += points
            self.stats.record(True, self.streak)
            print("Solved:", self.secret)
            print("Round points:", points)
        else:
            self.streak = 0
            self.stats.record(False, self.streak)
            print("Out of lives. The word was:", self.secret)

    def play_round(self):
        self.start_round()

        while self.lives > 0 and not self.won():
            print("\nWord:", self.masked())
            print("Wrong:", " ".join(sorted(self.wrong)) or "-")
            print(
                "Lives:", self.lives,
                "Score:", self.score,
                "Streak:", self.streak,
                "Difficulty:", self.difficulty,
            )

            raw = input("Letter, /hint, or /quit: ").strip().lower()

            if raw == "/quit":
                return False

            if raw == "/hint":
                print(self.use_hint())
                continue

            print(self.guess(raw))

        won = self.won()
        self._finish_round(won)
        return True

    def choose_category(self):
        """Return True when a valid category was selected, False on session quit."""
        print("\nCategories:", ", ".join(WORDS))
        raw = input("Choose category or q: ").strip().lower()

        if raw == "q":
            return False
        if raw not in WORDS:
            print("Unknown category. No game state changed.")
            return None

        self.category = raw
        print("Category selected:", self.category)
        return True

    def choose_difficulty(self):
        """Return True when a valid difficulty was selected, False on session quit."""
        print("Difficulties: easy (8 lives), medium (6), hard (4)")
        raw = input("Choose difficulty or q: ").strip().lower()

        if raw == "q":
            return False
        if raw not in self.DIFFICULTIES:
            print("Unknown difficulty. No game state changed.")
            return None

        self.difficulty = raw
        print("Difficulty selected:", self.difficulty)
        return True

    def run(self):
        print("Hangman Challenge")
        print("A session consists of multiple rounds.")

        while True:
            category_result = self.choose_category()
            if category_result is False:
                return
            if category_result is None:
                continue

            difficulty_result = self.choose_difficulty()
            if difficulty_result is False:
                return
            if difficulty_result is None:
                continue

            if not self.play_round():
                return

            print(
                "Session stats:",
                f"Rounds={self.stats.rounds},",
                f"Wins={self.stats.wins},",
                f"Best streak={self.stats.best_streak}",
            )

            again = input("Another round? [y/n]: ").strip().lower()
            if again == "y":
                continue
            if again == "n" or again == "q":
                print("Final score:", self.score, " Streak:", self.streak)
                print(
                    "Final stats:",
                    f"Rounds={self.stats.rounds},",
                    f"Wins={self.stats.wins},",
                    f"Best streak={self.stats.best_streak}",
                )
                return

            print("Invalid choice. Enter y, n, or q. No game state changed.")
