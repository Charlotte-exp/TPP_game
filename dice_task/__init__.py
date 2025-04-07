from otree.api import *

import random
from itertools import product

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'dice_task'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    original_dice = models.IntegerField(initial=0)
    reported_dice = models.IntegerField(initial=0)

    trustworthiness = models.IntegerField(
        min=0, max=100
    )

    def dice_roll(player):
        """
        Pairs of original and reported dice from the prolific pilot.
        could also be attributed to all participants when the session is created but then must be in the creating_session of the first app...
        """
        dice_permutations = list(product(range(1, 7), repeat=2))
        player.original_dice, player.reported_dice = random.choice(dice_permutations)
        # print(player.original_dice, player.reported_dice)


############  PAGES  #############
class DiceRatings(Page):
    form_model = "player"
    form_fields = ["trustworthiness"]

    @staticmethod
    def vars_for_template(player: Player):

        return dict(
            dice_roll=player.dice_roll(),
            original_dice=player.original_dice,
            reported_dice=player.reported_dice,
        )


class Results(Page):
    pass


page_sequence = [DiceRatings,
                 # Results
                 ]
