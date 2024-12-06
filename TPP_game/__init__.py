from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'TPP_game'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 20

    total_endowment = 30
    dictator_keeps = 23
    punishment_points = 10
    punishment_effectiveness = 3


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):


    number = models.IntegerField(  # change this to punishment_decision at some point...
        initial=0,
        choices=[
            [0, f'value 0'],[1, f'value 1'],[2, f'value 2'],[3, f'value 3'],[4, f'value 4'],[5, f'value 5'],
            [6, f'value 6'],[7, f'value 7'],[8, f'value 8'],[9, f'value 9'],[10, f'value 10'],
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
            number=player.number,
        )


class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    pass

page_sequence = [
                 Punishment,
                 ]
