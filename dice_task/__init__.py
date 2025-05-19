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

# ''' ONLY WHEN TESTING ON ITS OWN'''
# def creating_session(subsession):
#     for player in subsession.get_players():
#         participant = player.participant
#         participant.progress = 1

def creating_session(subsession):
    """
    Pairs of original and reported dice from the prolific pilot.
    Must be called from a separate page or in the creating_session
    """
    for p in subsession.get_players():
        p.dice_roll()


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    original_dice = models.IntegerField(initial=0)
    reported_dice = models.IntegerField(initial=0)

    trustworthiness = models.IntegerField(
        min=0, max=100
    )

    likability = models.IntegerField(
        min=0, max=100
    )

    trust_points = models.IntegerField(
        choices=[
            [0, '0 point'], [1, '1 point'], [2, '2 points'], [3, '3 points'],
        ],
        verbose_name='',
        widget=widgets.RadioSelectHorizontal
    )


    def dice_roll(player):
        """
        Pairs of original and reported dice from the prolific pilot.
        Must be called from a separate page or in the creating_session
        """
        dice_permutations = list(product(range(1, 7), repeat=2))
        while True:
            og_dice, rep_dice = random.choice(dice_permutations)
            if og_dice <= rep_dice:
                player.original_dice = og_dice
                player.reported_dice = rep_dice
                print(player.original_dice, player.reported_dice)
                return player.original_dice, player.reported_dice



############  PAGES  #############

class Filler(Page):

    @staticmethod
    def vars_for_template(player: Player):

        return dict(
            dice_roll=player.dice_roll(),
            total_pages=player.session.config['total_pages'],
        )

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant

class DiceRatings(Page):
    form_model = "player"
    form_fields = ["trustworthiness","likability", "trust_points"]

    @staticmethod
    def vars_for_template(player: Player):

        return dict(
            #dice_roll=player.dice_roll(),
            original_dice=player.original_dice,
            reported_dice=player.reported_dice,
            total_pages=player.session.config['total_pages'],
        )

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 1
        participant.decision_page_number += 1

class Filler_end_block2(Page):

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            total_pages=player.session.config['total_pages'],
        )

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 1


class Results(Page):
    pass


page_sequence = [DiceRatings,
                 Filler_end_block2]
