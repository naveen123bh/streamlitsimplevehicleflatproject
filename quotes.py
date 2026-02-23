# quotes.py
import random

LAO_TZU = [
"Nature does not hurry, yet everything is accomplished.",
"Silence is a source of great strength.",
"Mastering others is strength; mastering yourself is true power.",
"The mind creates the abyss; the heart crosses it.",
"The journey of a thousand miles begins with a single step.",
"He who knows does not speak; he who speaks does not know.",
"Be still like a mountain and flow like a river.",
"To the mind that is still, the whole universe surrenders.",
"To be natural is the highest spirituality.",
"Knowing others is intelligence; knowing yourself is wisdom.",
"The soft overcomes the hard.",
"Stop thinking and end your problems.",
"Respond intelligently even to unintelligent treatment.",
"When there is no desire, all things are at peace.",
"At the center of your being you have the answer."
]

BUDDHA = [
"Peace comes from within. Do not seek it outside.",
"In deep acceptance, transformation happens by itself.",
"Freedom begins the moment you stop pretending.",
"Attachment leads to suffering.",
"Three things cannot be hidden: the sun, the moon, and the truth.",
"Nothing can harm you as much as your own unguarded thoughts.",
"Health is the greatest gift.",
"Better than a thousand hollow words is one word that brings peace.",
"The moment you understand, the problem dissolves.",
"Hatred does not cease by hatred.",
"The root of suffering is attachment.",
"Be a lamp unto yourself.",
"Life is a dance — if you resist, you stumble.",
"Mind is a beautiful servant but a dangerous master.",
"Understanding is the path to freedom."
]

GEETA = [
"You have a right to action, but not to its fruits.",
"Whenever righteousness declines and unrighteousness rises, I manifest Myself.",
"I am the source of all; from Me everything proceeds.",
"Better is one’s own duty, though imperfectly done, than the duty of another well performed.",
"One who sees inaction in action is wise.",
"The wise see the same in all beings.",
"Established in yoga, perform action.",
"Approach the wise with humility, inquiry, and service; they will impart knowledge to you.",
"Whatever you do, do it as an offering.",
"Equanimity is yoga.",
"Detach from success and failure; they are just events.",
"Surrender all duties unto Me.",
"The one who is disciplined in yoga sees the Self in all.",
"Whatever you do, whatever you eat, whatever you offer or give away — do it as an offering unto Me."
]

ASHTAVAKRA = [
"You are not the body nor the mind.",
"The more silent you become, the more you can hear.",
"The world arises from ignorance and dissolves in understanding of the Self.",
"Freedom is knowing you are the witness.",
"Abandon identification and be happy.",
"You are the infinite ocean in which the universe appears like a wave.",
"The mind alone is bondage.",
"Rest as awareness and you will be untouched.",
"All effort binds; effortless awareness liberates.",
"The wise see no difference between action and inaction.",
"The universe arises in you.",
"You are not the doer; the three gunas of prakriti — sattva, rajas, tamas — are constantly in play.",
"Desirelessness is freedom.",
"He who knows the Self is untouched by sorrow.",
"Let the world rise and fall — you are the unmoving reality."
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
"The observer is the observed.",
"Knowledge is not wisdom; wisdom is deeper than knowledge.",
"Freedom from the known is the beginning of intelligence.",
"In awareness there is transformation."
]

MEERA = [
"I have found my true love within.",
"Where there is devotion, there is no fear.",
"Happiness is not a goal; it is a by-product of being in tune.",
"My heart sings only for the Divine.",
"In devotion, I dissolve.",
"I drink the nectar of love.",
"The world fades before devotion.",
"My Lord lives in my breath.",
"I seek nothing but Him.",
"Love is my only path.",
"I dance in surrender.",
"The Beloved is my refuge.",
"I have given myself completely.",
"In longing, I find union.",
"Divine dance is the result of surrender."
]

PATANJALI = [
"Yoga is the cessation of the fluctuations of the mind.",
"When the mind is still, the Seer abides in his nature.",
"Practice and detachment lead to freedom.",
"Through discipline comes clarity.",
"The purpose of yoga is freedom.",
"Study of the Self leads to wisdom.",
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
"Creativity is the fragrance of freedom.",
"Be a light unto yourself.",
"Watch your thoughts.",
"Relax into being.",
"Simplicity is the ultimate sophistication of the spirit."
]

KABIR = [
"Where do you search me? I am with you.",
"The river that flows in you flows in me.",
"Between you and the Beloved, there is no wall.",
"Look within, the treasure is there.",
"Drop the ego and see.",
"The divine is in every breath.",
"Your heart is the temple.",
"Do not go outside; turn inward.",
"Truth is simple.",
"The guest is within you.",
"Awaken before this body ceases to exist.",
"The sky is inside you.",
"Listen to the inner sound.",
"The drop merges in the ocean.",
"Existence trusts you more than you trust yourself."
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
    author, quotes = random.choice(ALL_CATEGORIES)
    quote = random.choice(quotes)
    return f'"{quote}"\n\n— {author}'