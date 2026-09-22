from collections import defaultdict


class HeadToHead:

    def __init__(self):

        self.history = defaultdict(
            lambda: {
                "matches": 0,
                "team1_wins": 0
            }
        )

    def get_stats(self, team1, team2):

        key = (team1, team2)

        reverse_key = (team2, team1)

        if key in self.history:

            stats = self.history[key]

            if stats["matches"] == 0:
                return 0.5, 0

            return (
                stats["team1_wins"] / stats["matches"],
                stats["matches"]
            )

        elif reverse_key in self.history:

            stats = self.history[reverse_key]

            if stats["matches"] == 0:
                return 0.5, 0

            team1_wins = (
                stats["matches"] - stats["team1_wins"]
            )

            return (
                team1_wins / stats["matches"],
                stats["matches"]
            )

        return 0.5, 0

    def update(self, team1, team2, winner):

        key = (team1, team2)

        self.history[key]["matches"] += 1

        if winner == team1:
            self.history[key]["team1_wins"] += 1