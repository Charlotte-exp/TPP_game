from otree.api import *
import random

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'baseline_trials'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 6
    TREATMENTS = ['DG give', 'DG give norm', '3PP give', '3PP give norm', '3PP punish', '3PP punish norm']


class Subsession(BaseSubsession):
    pass


def creating_session(subsession):
    print('Creating session; round number: {}'.format(subsession.round_number))
    if subsession.round_number == 1:
        for player in subsession.get_players():
            participant = player.participant
            participant.treatment_order = random.sample(C.TREATMENTS, len(C.TREATMENTS))
            print('set treatment_order to', participant.treatment_order)
    for player in subsession.get_players():
        player.treatment = player.participant.treatment_order[player.round_number - 1]
        print('set treatment to', player.treatment)

class Group(BaseGroup):
    pass


class Player(BasePlayer):
    dictator_amount = models.IntegerField(min=0, max=10)
    treatment = models.StringField()


# PAGES
class baselinePage(Page):
    form_model = 'player'
    form_fields = ['dictator_amount']
    @staticmethod
    def vars_for_template(player: Player):
        print('Generating template variables')

        # Create page per treatment
        if player.treatment == 'DG give':
            text = "How much do you give to Person B?"
        elif player.treatment == 'DG give norm':
            text = "How socially appropriate is it to give to Person B?"
        elif player.treatment == '3PP give':
            text = "How much do you give to Person B?"
        elif player.treatment == '3PP give norm':
            text = "How socially appropriate is it to give to Person B?"
        elif player.treatment == '3PP punish':
            text = "How much do you punish Person A?"
        else:
            text = "How socially appropriate is it to punish Person A?"

        # Load path of treatment image
        image = 'baseline/{}.png'.format(player.treatment)
        print('Generating image path', image)

        return {
            'treatment': player.treatment,
            'treatment_text': text,
            'image': image,
        }

    def before_next_page(player: Player, timeout_happened):
        player.payoff = 10 - player.dictator_amount


class Results(Page):
    pass

class instructionPage(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

#page_sequence = [instructionPage, baselinePage, Results]
page_sequence = [baselinePage, Results]
