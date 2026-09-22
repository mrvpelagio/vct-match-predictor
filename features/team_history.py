from collections import deque, defaultdict


class TeamHistory:
    """
    Stores all historical information for one team.

    Every feature in our ML model will be computed from this object.
    """

    def __init__(self):

        # ------------------------
        # Team strength
        # ------------------------

        self.elo = 1500

        self.matches_played = 0

        # ------------------------
        # Recent results
        # ------------------------

        self.results = deque(maxlen=5)

        # ------------------------
        # Rolling statistics
        # (last 10 maps)
        # ------------------------

        self.acs = deque(maxlen=10)

        self.rating = deque(maxlen=10)

        self.kast = deque(maxlen=10)

        self.adr = deque(maxlen=10)

        self.fk = deque(maxlen=10)

        self.fd = deque(maxlen=10)

        # ------------------------
        # Map history
        # Example:
        # self.maps["Ascent"] = [1,0,1]
        # ------------------------

        self.maps = defaultdict(lambda: deque(maxlen=10))

    # ==========================================================
    # Generic helpers
    # ==========================================================

    def average(self, values):

        if len(values) == 0:
            return None

        return sum(values) / len(values)

    # ==========================================================
    # Win rate
    # ==========================================================

    def last5_winrate(self):

        if len(self.results) == 0:
            return 0.5

        return sum(self.results) / len(self.results)

    # ==========================================================
    # Rolling averages
    # ==========================================================

    def avg_acs(self):
        return self.average(self.acs)

    def avg_rating(self):
        return self.average(self.rating)

    def avg_kast(self):
        return self.average(self.kast)

    def avg_adr(self):
        return self.average(self.adr)

    def avg_fk(self):
        return self.average(self.fk)

    def avg_fd(self):
        return self.average(self.fd)

    # ==========================================================
    # Map win rate
    # ==========================================================

    def map_winrate(self, map_name):

        if len(self.maps[map_name]) == 0:
            return 0.5

        return sum(self.maps[map_name]) / len(self.maps[map_name])

    # ==========================================================
    # Update history
    # ==========================================================

    def update(
        self,
        win,
        acs,
        rating,
        kast,
        adr,
        fk,
        fd,
        map_name=None
    ):

        self.results.append(win)

        if acs is not None:
            self.acs.append(acs)

        if rating is not None:
            self.rating.append(rating)

        if kast is not None:
            self.kast.append(kast)

        if adr is not None:
            self.adr.append(adr)

        if fk is not None:
            self.fk.append(fk)

        if fd is not None:
            self.fd.append(fd)

        if map_name is not None:
            self.maps[map_name].append(win)

        self.matches_played += 1