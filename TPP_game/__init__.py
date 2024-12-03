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

    punishment_1 = models.IntegerField()



###### PAGES #######
class Punishment(Page):

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == 1:
            return True

    def vars_for_template(player: Player):
        return {
            'participation_fee': player.session.config['participation_fee'],
        }


class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    pass


page_sequence = [Punishment,
                 ]
