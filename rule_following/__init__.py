from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'rule_following'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

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
class RuleFollowing(Page):
    form_model = "player"
    form_fields = ["slider1", "slider2", "slider3"]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
        )



page_sequence = [RuleFollowing,
                 ]
