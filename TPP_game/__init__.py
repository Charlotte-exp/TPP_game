from otree.api import *

import random

import os

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'TPP_game'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 20

    total_endowment = 12
    dictator_keeps_1 = total_endowment  # everything
    dictator_keeps_2 = total_endowment*(1/4)  # quarter
    dictator_keeps_3 = total_endowment*(1/3)  # third
    dictator_keeps_4 = total_endowment*(1/2)  # half
    punishment_points = total_endowment*(1/3)
    punishment_effectiveness = 3


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    dictator_country = models.StringField()
    receiver_country = models.StringField()

    decision_1 = models.IntegerField(  # I don't know why I need the string as well...
        initial=0,
        choices=[
            [0, f'value 0'],[1, f'value 1'],[2, f'value 2'],[3, f'value 3'],[4, f'value 4'],[5, f'value 5'],
            [6, f'value 6'],[7, f'value 7'],[8, f'value 8'],[9, f'value 9'],[10, f'value 10'],
        ],
        verbose_name='[Your decision]',
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )

    decision_2 = models.IntegerField(
        initial=0,
        choices=[
            [0, f'value 0'], [1, f'value 1'], [2, f'value 2'], [3, f'value 3'], [4, f'value 4'], [5, f'value 5'],
            [6, f'value 6'], [7, f'value 7'], [8, f'value 8'], [9, f'value 9'], [10, f'value 10'],
        ],
        verbose_name='[Your decision]',
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )

    decision_3 = models.IntegerField(
        initial=0,
        choices=[
            [0, f'value 0'], [1, f'value 1'], [2, f'value 2'], [3, f'value 3'], [4, f'value 4'], [5, f'value 5'],
            [6, f'value 6'], [7, f'value 7'], [8, f'value 8'], [9, f'value 9'], [10, f'value 10'],
        ],
        verbose_name='[Your decision]',
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )

    decision_4 = models.IntegerField(
        initial=0,
        choices=[
            [0, f'value 0'], [1, f'value 1'], [2, f'value 2'], [3, f'value 3'], [4, f'value 4'], [5, f'value 5'],
            [6, f'value 6'], [7, f'value 7'], [8, f'value 8'], [9, f'value 9'], [10, f'value 10'],
        ],
        verbose_name='[Your decision]',
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )

####### FUNCTIONS ########

def read_countries():
    """
    All the country codes are stored in the country_codes.txt file.
    This functions opens the file and reads the codes.
    At the moment it only works with this convoluted absolute file code. not sure how that'll go on a server.
    """
    current_dir = os.path.dirname(__file__) # Get the absolute path of the current script
    file_path = os.path.join(current_dir, 'country_codes.txt')
    with open(file_path, 'r') as file:
        country_codes = [line.strip() for line in file.readlines()]
    return country_codes

# code that does not work - file path problem
# def get_countries():
#     with open(file_path, 'r') as file:
#         country_codes = [line.strip() for line in file.readlines()]
#     return country_codes

def get_2_countries(player: Player):
    """
    selects two random countries from the country list.
    checks they are different before returning them.
    """
    country_codes = read_countries()
    while True:
        country_1, country_2 = random.choices(country_codes, k=2)
        if country_1 != country_2:
            player.receiver_country = country_1
            #print('receiver', player.receiver_country)
            player.dictator_country = country_2
            #print('dictator', player.dictator_country)
            return player.receiver_country, player.dictator_country

####### PAGES #######

class Punishment(Page):
    form_model = 'player'
    form_fields = ['decision_1', 'decision_2', 'decision_3', 'decision_4']


    def vars_for_template(player: Player):
        return dict(
            decisions=[
                dict(
                    index=1,
                    decision=player.decision_1,
                    dictator_keeps=C.dictator_keeps_1,
                    receiver=C.total_endowment - C.dictator_keeps_1,
                ),
                dict(
                    index=2,
                    decision=player.decision_2,
                    dictator_keeps=C.dictator_keeps_2,
                    receiver=C.total_endowment - C.dictator_keeps_2,
                ),
                dict(
                    index=3,
                    decision=player.decision_3,
                    dictator_keeps=C.dictator_keeps_3,
                    receiver=C.total_endowment - C.dictator_keeps_3,
                ),
                dict(
                    index=4,
                    decision=player.decision_4,
                    dictator_keeps=C.dictator_keeps_4,
                    receiver=C.total_endowment - C.dictator_keeps_4,
                ),
            ],
            # decision_1=player.decision_1,
            # decision_2=player.decision_2,
            # decision_3=player.decision_3,
            # decision_4=player.decision_4,
            receiver_country=player.receiver_country,
            dictator_country=player.dictator_country,
            punishment_points=range(0, int(C.punishment_points) + 1),
            punishment_effectiveness=C.punishment_effectiveness,
        )

    # also does not display...
    # @staticmethod
    # def error_message(player: Player, values):
    #     if values['decision_1'] is None:
    #         return 'Please make a selection before proceeding.'


class ResultsWaitPage(WaitPage):
    pass


class Results(Page):

    def vars_for_template(player: Player):
        return dict(
            country_codes = get_2_countries(player),
        )

page_sequence = [Results,
                 Punishment,
                 ]
