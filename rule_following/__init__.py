from otree.api import *

import itertools


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'rule_following'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass

def creating_session(subsession):

    treatments = itertools.cycle(['hurt_me', 'hurt_other'])
    for p in subsession.get_players():
        p.rule_following_condition = next(treatments)
        p.participant.rule_following_condition = p.rule_following_condition


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    rule_following_condition = models.StringField()

    slider1 = models.IntegerField(
        min=0, max=100
    )

    slider2 = models.IntegerField(
        min=0, max=100
    )

    slider3 = models.IntegerField(
        min=0, max=100
    )


######## PAGES ########
class Filler(Page):

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
        )

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        #participant.progress += 1



class RuleFollowing(Page):
    form_model = "player"
    form_fields = ["slider1", "slider2", "slider3"]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            condition= player.rule_following_condition,
        )



page_sequence = [RuleFollowing,
                 ]
