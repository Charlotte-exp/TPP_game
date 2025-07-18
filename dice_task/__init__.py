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

        # Set language to English if English is the only offered language in that country (in this case participants do not see language selection pages)
        participant = p.participant
        if 'language' not in participant.vars:
            participant.language = 'en'

        if 'progress' not in participant.vars:
            participant.progress = 1
            participant.decision_page_number = 0


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
                # print(player.original_dice, player.reported_dice)
                return player.original_dice, player.reported_dice



############  PAGES  #############

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
            very_untrustworthy=get_translation("very_untrustworthy", lang),
            untrustworthy=get_translation("untrustworthy", lang),
            slightly_untrustworthy=get_translation("slightly_untrustworthy", lang),
            slightly_trustworthy=get_translation("slightly_trustworthy", lang),
            trustworthy=get_translation("trustworthy", lang),
            very_trustworthy=get_translation("very_trustworthy", lang),
            dice_likable=get_translation("dice_likable", lang),
            very_unlikable=get_translation('very_unlikable', lang),
            unlikable=get_translation('unlikable', lang),
            slightly_unlikable=get_translation('slightly_unlikable', lang),
            slightly_likable=get_translation('slightly_likable', lang),
            likable=get_translation('likable', lang),
            very_likable=get_translation('very_likable', lang),
            dice_error=get_translation("error3", lang),
            dice_trust_game=get_translation("dice_trust_game", lang,
                                            points_to_send=C.points_to_send),
            dice_question=get_translation("dice_question", lang),
            dice_0points=get_translation('points_button', lang,
                                                 num_points=0),
            dice_1points=get_translation('points_button', lang,
                                                 num_points=1),
            dice_2points=get_translation('points_button', lang,
                                                 num_points=2),
            dice_3points=get_translation('points_button', lang,
                                                 num_points=3),
            button_next=get_translation("button_next", lang),
            button_decision=get_translation('button_decision', lang),
            button_block=get_translation('button_block', lang),
            total_pages=player.session.config['total_pages'],
        )

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 1
        participant.decision_page_number += 1


class FillerEndBlock2(Page):

    @staticmethod
    def vars_for_template(player: Player):
        participant = player.participant
        lang = participant.language

        return dict(
            filler_title=get_translation("block_complete", lang, block_num=2),
            filler_completed=get_translation("filler2b_completed", lang),
            filler_next_page=get_translation("filler2b_next_page", lang),
            button_next=get_translation("button_next", lang),
            total_pages=player.session.config['total_pages'],
        )

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 1


class Results(Page):
    pass


page_sequence = [DiceRatings,
                 FillerEndBlock2]
