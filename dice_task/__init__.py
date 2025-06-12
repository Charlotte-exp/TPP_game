from otree.api import *

import random
from itertools import product

from translations import get_translation

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'dice_task'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    points_to_send = 3

class Subsession(BaseSubsession):
    pass

def creating_session(subsession):
    """
    Pairs of original and reported dice from the prolific pilot.
    Must be called from a separate page or in the creating_session
    """
    for p in subsession.get_players():
        p.dice_roll()

        ''' ONLY WHEN TESTING APP ON ITS OWN'''
        participant = p.participant
        participant.progress = 1
        participant.decision_page_number = 0
        participant.language = 'en'


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
        participant = player.participant
        lang = participant.language

        return dict(
            original_dice=player.original_dice,
            reported_dice=player.reported_dice,
            dice_observe=get_translation("dice_observe", lang),
            dice_previous=get_translation("dice_previous", lang),
            dice_actual=get_translation("dice_actual", lang),
            dice_rolled=get_translation("dice_rolled", lang),
            dice_lie=get_translation("dice_lie", lang),
            dice_report=get_translation("dice_report", lang),
            dice_reported=get_translation("dice_reported", lang),
            dice_trustworthy=get_translation("dice_trustworthy", lang),
            dice_not_trust=get_translation("dice_not_trust", lang),
            dice_very_trust=get_translation("dice_very_trust", lang),
            dice_likable=get_translation("dice_likable", lang),
            dice_not_like=get_translation("dice_not_like", lang),
            dice_very_like=get_translation("dice_very_like", lang),
            dice_error=get_translation("dice_error", lang),
            dice_trust_game=get_translation("dice_trust_game", lang,
                                            points_to_send=C.points_to_send),
            dice_question=get_translation("dice_question", lang),
            dice_0points=get_translation("dice_0points", lang),
            dice_1points=get_translation("dice_1points", lang),
            dice_2points=get_translation("dice_2points", lang),
            dice_3points=get_translation("dice_3points", lang),
            button_next=get_translation("button_next", lang),
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
