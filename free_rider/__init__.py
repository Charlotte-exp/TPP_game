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

''' ONLY WHEN TESTING ON ITS OWN'''
def creating_session(subsession):
    for player in subsession.get_players():
        participant = player.participant
        participant.progress = 1


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    ## Relational Mobility
    wealthy_contribution = models.StringField(
        choices=[
            [0, 'Strongly disagree'], [1, 'Disagree'], [2, 'Slightly disagree'],
            [3, 'Slightly agree'], [4, 'Agree'], [5, 'Strongly agree'],
        ],
        verbose_name='',
        widget=widgets.RadioSelectHorizontal
    )
    wealthy_merit = models.StringField(
        choices=[
            [0, 'Strongly disagree'], [1, 'Disagree'], [2, 'Slightly disagree'],
            [3, 'Slightly agree'], [4, 'Agree'], [5, 'Strongly agree'],
        ],
        verbose_name='',
        widget=widgets.RadioSelectHorizontal
    )
    poor_contribution = models.StringField(
        choices=[
            [0, 'Strongly disagree'], [1, 'Disagree'], [2, 'Slightly disagree'],
            [3, 'Slightly agree'], [4, 'Agree'], [5, 'Strongly agree'],
        ],
        verbose_name='',
        widget=widgets.RadioSelectHorizontal
    )
    poor_merit = models.StringField(
        choices=[
            [0, 'Strongly disagree'], [1, 'Disagree'], [2, 'Slightly disagree'],
            [3, 'Slightly agree'], [4, 'Agree'], [5, 'Strongly agree'],
        ],
        verbose_name='',
        widget=widgets.RadioSelectHorizontal
    )


#########  PAGES  ###########
class Narratives(Page):
    form_model = "player"
    form_fields = ["wealthy_contribution", "wealthy_merit", "poor_contribution", "poor_merit"]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            total_pages=player.session.config['total_pages'],
        )

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 1


page_sequence = [Narratives,
                 #ResultsWaitPage,
                 ]
