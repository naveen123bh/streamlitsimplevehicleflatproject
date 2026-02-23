# quotes.py

import random

# ==============================
# LIST OF QUOTES
# ==============================
QUOTES = [
    "The mind is a mirror, see the reflection, not the shadow.\nPeace is the awareness of what is.",
    "Everything happens by itself; the doer is an illusion.\nWitness the flow and be free.",
    "Silence carries the answer; the world is but a play.\nBe the observer, not the actor.",
    "When you stop chasing, you arrive.\nWhat is, is enough for this moment.",
    "Nothing belongs to you, yet everything unfolds within you.\nLet love arise without effort."
]

# ==============================
# FUNCTION TO GET RANDOM QUOTE
# ==============================
def get_random_quote():
    return random.choice(QUOTES)