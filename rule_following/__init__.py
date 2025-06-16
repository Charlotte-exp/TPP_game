from otree.api import *

import itertools
import random

from translations import get_translation

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'rule_following'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    points_per_slider = 1


class Subsession(BaseSubsession):
    pass


def creating_session(subsession):

    treatments = itertools.cycle(['hurt_me', 'hurt_other'])
    for p in subsession.get_players():
        p.rule_following_condition = next(treatments)
        p.participant.rule_following_condition = p.rule_following_condition

        p.aim_number()

        # ''' ONLY WHEN TESTING ON ITS OWN'''
        # p.participant.decision_page_number = 0  # For testing only
        # p.participant.progress = 1
        # p.participant.language = 'en'


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    rule_following_condition = models.StringField()
    rule_aim = models.IntegerField()

    slider1 = models.IntegerField(
        min=0, max=100
    )

    slider2 = models.IntegerField(
        min=0, max=100
    )

    slider3 = models.IntegerField(
        min=0, max=100
    )


    def aim_number(player):
        """
        Pairs of original and reported dice from the prolific pilot.
        Must be called from a separate page or in the creating_session
        """
        slider_list = list(range(1,100))
        rule_aim = random.choice(slider_list)
        player.rule_aim = rule_aim
        # print(player.rule_aim)
        return player.rule_aim


######## PAGES ########

class RuleFollowing(Page):
    form_model = "player"
    form_fields = ["slider1", "slider2", "slider3"]

    @staticmethod
    def vars_for_template(player: Player):
        participant = player.participant
        lang = participant.language

        return dict(
            condition= player.rule_following_condition,
            points_per_slider=C.points_per_slider,
            total_pages=player.session.config['total_pages'],
            rule_instru=get_translation("rule_instru", lang),
            rule_aim_another=get_translation("rule_aim_another", lang,
                                             aim=player.rule_aim,
                                             points_per_slider=C.points_per_slider),
            rule_aim_me=get_translation("rule_aim_me", lang,
                                             aim=player.rule_aim,
                                            points_per_slider=C.points_per_slider),
            rule_rule=get_translation("rule_rule", lang,
                                      aim=player.rule_aim),
            rule_another_lose=get_translation("rule_another_lose", lang),
            rule_me_lose=get_translation("rule_me_lose", lang),
            aim= player.rule_aim,
            button_next=get_translation('button_next', lang),
            button_decision=get_translation('button_decision', lang),
            button_block=get_translation('button_block', lang),
            error_all_sliders=get_translation('error_all_sliders', lang),
        )

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 1
        participant.decision_page_number += 1



page_sequence = [RuleFollowing,
                 ]
