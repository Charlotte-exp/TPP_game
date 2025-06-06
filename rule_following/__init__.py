from otree.api import *

import itertools

import random

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
        print(player.rule_aim)
        return player.rule_aim


######## PAGES ########
class Filler(Page):

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            total_pages=player.session.config['total_pages'],
        )

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 1



class RuleFollowing(Page):
    form_model = "player"
    form_fields = ["slider1", "slider2", "slider3"]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            condition= player.rule_following_condition,
            points_per_slider=C.points_per_slider,
            total_pages=player.session.config['total_pages'],
            aim= player.rule_aim,
        )

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 1
        participant.decision_page_number += 1



page_sequence = [RuleFollowing,
                 ]
