# quotes.py

import random

LAO_TZU = [
"Nature does not hurry, yet everything is accomplished.",
"Silence is a source of great strength.",
"Mastering others is strength; mastering yourself is true power.",
"When I let go of what I am, I become what I might be.",
"The journey of a thousand miles begins with a single step.",
"He who knows does not speak; he who speaks does not know.",
"Be still like a mountain and flow like a river.",
"To the mind that is still, the whole universe surrenders.",
"Act without expectation.",
"Knowing others is intelligence; knowing yourself is wisdom.",
"The soft overcomes the hard.",
"Stop thinking and end your problems.",
"Respond intelligently even to unintelligent treatment.",
"When there is no desire, all things are at peace.",
"At the center of your being you have the answer."
]

BUDDHA = [
"Peace comes from within. Do not seek it outside.",
"What you think, you become.",
"The mind is everything.",
"Attachment leads to suffering.",
"Three things cannot be hidden: the sun, the moon, and the truth.",
"Nothing can harm you as much as your own thoughts.",
"Health is the greatest gift.",
"Better than a thousand hollow words is one word that brings peace.",
"You yourself must strive.",
"Hatred does not cease by hatred.",
"The root of suffering is attachment.",
"Be a lamp unto yourself.",
"All that we are is the result of what we have thought.",
"Work out your own salvation.",
"Understanding is the path to freedom."
]

GEETA = [
"You have a right to action, but not to its fruits.",
"The self is never born and never ceases to exist.",
"When meditation is mastered, the mind is unwavering.",
"Perform action without attachment.",
"One who sees inaction in action is wise.",
"The wise see the same in all beings.",
"Established in yoga, perform action.",
"The mind is restless, but can be controlled.",
"Whatever you do, do it as an offering.",
"The soul is neither killed nor kills.",
"Equanimity is yoga.",
"Detach from success and failure.",
"Surrender all duties unto Me.",
"The one who is disciplined in yoga sees the Self in all.",
"Desire leads to anger and confusion."
]

ASHTAVAKRA = [
"You are not the body nor the mind.",
"You are pure awareness.",
"The world is illusion (quantum physics double slit experiment ) ; the Self alone is real.",
"Freedom is knowing you are the witness.",
"Abandon identification and be happy.",
"You are the solitary witness of all.",
"The mind alone is bondage.",
"Rest as awareness,and you will untouched.",
"Nothing binds you.",
"You are ever free.",
"The universe arises in you.",
"You are not the doer but the 3 gunas of prakriti satv ,rajas ,tamas are constantly in play inside you.",
"Desirelessness is freedom.",
"Know yourself as consciousness.",
"Be still and know."
]

KRISHNAMURTI = [
"Truth is a pathless land.",
"It is no measure of health to be well adjusted to a sick society.",
"Observation without evaluation is the highest intelligence.",
"Freedom begins with self-knowledge.",
"The ability to observe without judging is intelligence.",
"Fear ends when thought ends.",
"Understanding comes through awareness.",
"Relationship is the mirror.",
"To understand yourself is the beginning of wisdom.",
"Choiceless awareness is freedom.",
"Desire breeds conflict.",
"The observer is the observed.",
"Knowledge is not wisdom,wisdom is more deeper than that .",
"Listen completely.",
"In awareness there is transformation."
]

MEERA = [
"I have found my true love within.",
"Where there is devotion , there is no fear.",
"I belong to the One alone.",
"My heart sings only for the Divine.",
"In devotion, I dissolve.",
"I drink the nectar of love.",
"The world fades before devotion .",
"My Lord lives in my breath.",
"I seek nothing but Him.",
"Love is my only path.",
"I dance in surrender.",
"The Beloved is my refuge.",
"I have given myself completely.",
"In longing, I find union.",
"devine dance is the result of surrender."
]

PATANJALI = [
"Yoga is the cessation of the fluctuations of the mind.",
"When the mind is still, the Seer abides in his nature.",
"Practice and detachment lead to freedom.",
"Through discipline comes clarity.",
"The purpose of yoga is freedom.",
"Self-study leads to wisdom.",
"Balance effort with ease.",
"Concentration brings insight.",
"Control of breath steadies the mind.",
"The mind takes the shape of what it rests upon.",
"Dispassion removes disturbance.",
"Meditation reveals truth.",
"Silence reveals the Self.",
"Consistency is the path.",
"Inner stillness is liberation."
]

OSHO = [
"Be realistic: plan for a miracle.",
"Courage is a love affair with the unknown.",
"Life begins where fear ends.",
"Meditation is a way of being.",
"Truth is not something outside to be discovered.",
"Awareness is the key.",
"Drop the mind and be.",
"Celebrate life.",
"Silence is the language of existence.",
"Love is the ultimate alchemy.",
"Die each moment to the past.",
"Be a light unto yourself.",
"Watch your thoughts.",
"Relax into being.",
"Meditation is witnessing."
]

KABIR = [
"Where do you search me? I am with you.",
"The river that flows in you flows in me.",
"Between you and the Beloved, there is no wall.",
"Look within, the treasure is there.",
"Drop the ego and see.",
"The divine is in every breath.",
"Your heart is the temple.",
"Do not go outside, turn inward.",
"Truth is simple.",
"The guest is within you.",
"Awaken before this body ceases to exist.",
"The sky is inside you.",
"Listen to the inner sound.",
"The drop merges in the ocean.",
"Realize the Self."
]

ALL_CATEGORIES = [
("Lao Tzu", LAO_TZU),
("Buddha", BUDDHA),
("Bhagavad Gita", GEETA),
("Ashtavakra Gita", ASHTAVAKRA),
("J. Krishnamurti", KRISHNAMURTI),
("Meera", MEERA),
("Patanjali", PATANJALI),
("Osho", OSHO),
("Kabir", KABIR)
]

def get_random_quote():
    selected_quotes = []
    for author, quotes in ALL_CATEGORIES:
        selected_quotes.append((author, random.choice(quotes)))
    
    author, quote = random.choice(selected_quotes)
    return f'"{quote}"\n\n— {author}'