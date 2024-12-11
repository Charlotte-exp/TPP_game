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
    total_endowment = 30
    dictator_keeps = 23
    punishment_points = 10
    punishment_effectiveness = 3


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
    #dictator_amount = models.IntegerField(min=0, max=10)
    dictator_amount = models.IntegerField(  # change this to punishment_decision at some point...
        initial=0,
        choices=[
            [0, f'value 0'], [1, f'value 1'], [2, f'value 2'], [3, f'value 3'], [4, f'value 4'], [5, f'value 5'],
            [6, f'value 6'], [7, f'value 7'], [8, f'value 8'], [9, f'value 9'], [10, f'value 10'],
        ],
        verbose_name='[Your decision]',
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )

    treatment = models.StringField()
    #dictator_country = models.StringField()
    #receiver_country = models.StringField()


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
            'number':player.dictator_amount,
            #'receiver_country': player.receiver_country
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
