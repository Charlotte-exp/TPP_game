from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'TPP_game'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 20


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    punishment_decision = models.IntegerField(
        initial=0,
        choices=[
            [0, f'value 0'],
            [1, f'value 1'],
        ],
        verbose_name='[Your decision]',
        widget=widgets.RadioSelect
    )

    number = models.IntegerField(
        initial=0,
        choices=[
            [0, f'value 0'],
            [1, f'value 1'],
            [0, f'value 2'],
            [1, f'value 3'],
            [4, f'value 4'],
            [5, f'value 5'],
            [6, f'value 6'],
            [7, f'value 7'],
            [8, f'value 8'],
            [9, f'value 9'],
            [10, f'value 10'],
        ],
        verbose_name='[Your decision]',
        widget=widgets.RadioSelect
    )


###### PAGES #######

class Punishment(Page):
    form_model = 'player'
    form_fields = ['number']


    def vars_for_template(player: Player):
        return dict(
            number=player.number
        )


class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    form_model = 'player'
    form_fields = ['punishment_decision']

    def vars_for_template(player: Player):
        return dict(
            punishment_decision=player.punishment_decision
        )


page_sequence = [Results,
                 Punishment,
                 ]
