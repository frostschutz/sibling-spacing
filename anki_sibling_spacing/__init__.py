#!/usr/bin/python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Sibling Spacing is an addon for Anki 2 - http://ankisrs.net
# ---------------------------------------------------------------------------
# Author:      Andreas Klauer (Andreas Klauer@metamorpher.de)
# Version:     0.01 (2013-02-22)
# License:     GPL
# ---------------------------------------------------------------------------

# --- Imports: ---

from anki.hooks import addHook, wrap
from anki.lang import _
from aqt import *
from aqt.utils import showInfo

config = mw.addonManager.getConfig(__name__)

# --- Globals: ---

__version__ = 0.02

# --- Functions: ---


def siblingIvl(self, card, idealIvl, _old):
    origIvl = _old(self, card, idealIvl)
    ivl = origIvl

    # Penalty
    minIvl = self.col.db.scalar(
        """SELECT MIN(ivl) FROM cards WHERE ivl > 0 AND nid = ? AND id != ? AND queue = 2""",
        card.nid,
        card.id,
    )

    while minIvl and minIvl > 0 and ivl > minIvl * 4:
        ivl = max(1, int(ivl / 2.0))

    # Boost
    delta = max(1, int(ivl * 0.15))
    boost = max(1, int(ivl * 0.5))

    siblings = True

    while siblings:
        siblings = self.col.db.scalar(
            """SELECT count() FROM cards WHERE due >= ? AND due <= ? AND nid = ? AND id != ? AND queue = 2""",
            self.today + ivl - delta,
            self.today + ivl + delta,
            card.nid,
            card.id,
        )
        if siblings:
            ivl += boost

    if config["Debug"]:
        if minIvl and minIvl > 0:
            print(
                "Sibling Spacing %d%+d = %d days for card %d (sibling has %d days)"
                % (origIvl, ivl - origIvl, ivl, card.id, minIvl)
            )
        else:
            print(
                "Sibling Spacing == %d days for card %d without visible siblings"
                % (ivl, card.id)
            )

    return ivl


def profileLoaded():
    # add scheduler
    anki.sched.Scheduler._adjRevIvl = wrap(
        anki.sched.Scheduler._adjRevIvl, siblingIvl, "around"
    )


# --- Hooks: ---

addHook("profileLoaded", profileLoaded)

# --- End of file. ---
