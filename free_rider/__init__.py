from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'free_rider'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    ## Relational Mobility
    wealthy_contribution = models.StringField(
        choices=[
            [0, 'Strongly disagree'], [1, 'Disagree'], [2, 'Slightly disagree'],
            [3, 'Slightly agree'], [4, 'Agree'], [5, 'Strongly agree'],
        ],
        verbose_name='The wealthiest 1% in my country should contribute more to society.',
        widget=widgets.RadioSelectHorizontal
    )
    wealthy_merit = models.StringField(
        choices=[
            [0, 'Strongly disagree'], [1, 'Disagree'], [2, 'Slightly disagree'],
            [3, 'Slightly agree'], [4, 'Agree'], [5, 'Strongly agree'],
        ],
        verbose_name='The wealthiest 1% in my country are in their current position largely due to their own actions and decisions.',
        widget=widgets.RadioSelectHorizontal
    )
    poor_contribution = models.StringField(
        choices=[
            [0, 'Strongly disagree'], [1, 'Disagree'], [2, 'Slightly disagree'],
            [3, 'Slightly agree'], [4, 'Agree'], [5, 'Strongly agree'],
        ],
        verbose_name='The poorest 1% in my country should contribute more to society.',
        widget=widgets.RadioSelectHorizontal
    )
    poor_merit = models.StringField(
        choices=[
            [0, 'Strongly disagree'], [1, 'Disagree'], [2, 'Slightly disagree'],
            [3, 'Slightly agree'], [4, 'Agree'], [5, 'Strongly agree'],
        ],
        verbose_name='The poorest 1% in my country are in their current position largely due to their own actions and decisions.',
        widget=widgets.RadioSelectHorizontal
    )


#########  PAGES  ###########
class Narratives(Page):
    form_model = "player"
    form_fields = ["wealthy_contribution", "wealthy_merit", "poor_contribution", "poor_merit"]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
        )



page_sequence = [Narratives,
                 #ResultsWaitPage,
                 ]
