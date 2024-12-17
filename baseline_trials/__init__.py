from otree.api import *
import random

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'baseline_trials'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 8

    TREATMENTS = ['DG give', 'DG give norm', '3PP give', '3PP punish', '3PP punish norm', '2PP give', '2PP punish', '2PP punish norm']
    # total_endowment = 30
    # receiver_endowment = 0
    # punishment_points = 10
    # punishment_effectiveness = 3
    # dictator_keeps = 23  # Should eventually be list: [30, 25, 20, 15]
    # norm_strategy_dic_gives = 5 # Should eventually be list: [0, 5, 10, 15] : different levels of dictator giving
    # norm_strategy_dic_gives_binary = 10 # Should eventually be list: ??? [0, 10]? Selfish or less selfish dictator
    # norm_strategy_punish_norm = 3 # Should eventually be list with 3-4 scenarios: ??? [0, 3, 7, 10]?
    total_endowment = 12
    receiver_endowment = 0
    punishment_points = 4
    punishment_effectiveness = 3
    dictator_keeps = 8  # Should eventually be list: [30, 25, 20, 15]
    norm_strategy_dic_gives = 2  # Should eventually be list: [0, 5, 10, 15] : different levels of dictator giving
    norm_strategy_dic_gives_binary = 3  # Should eventually be list: ??? [0, 10]? Selfish or less selfish dictator
    norm_strategy_punish_norm = 1  # Should eventually be list with 3-4 scenarios: ??? [0, 3, 7, 10]?



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
    dic_decision1 = models.IntegerField(
        initial=0,
        choices=[
            [0, f'value 0'], [1, f'value 1'], [2, f'value 2'], [3, f'value 3'], [4, f'value 4'], [5, f'value 5'],
            [6, f'value 6'], [7, f'value 7'], [8, f'value 8'], [9, f'value 9'], [10, f'value 10'], [11, f'value 11'], [12, f'value 12'], [13, f'value 13'], [14, f'value 14'], [15, f'value 15'],
            [16, f'value 16'], [17, f'value 17'], [18, f'value 18'], [19, f'value 19'], [20, f'value 20'], [21, f'value 21'], [22, f'value 22'], [23, f'value 23'], [24, f'value 24'], [25, f'value 25'],
            [26, f'value 26'], [27, f'value 27'], [28, f'value 28'], [29, f'value 29'], [30, f'value 30'],
        ],
        verbose_name='[Your decision]',
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )
    dic_norm_decision1 = models.IntegerField(
        initial=0,
        choices=[
            [0, f'value 0'], [1, f'value 1'], [2, f'value 2'], [3, f'value 3'], [4, f'value 4'], [5, f'value 5'],
        ],
        verbose_name='[Your decision]',
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )
    pun_decision1 = models.IntegerField(
        initial=0,
        choices=[
            [0, f'value 0'], [1, f'value 1'], [2, f'value 2'], [3, f'value 3'], [4, f'value 4'], [5, f'value 5'],
            [6, f'value 6'], [7, f'value 7'], [8, f'value 8'], [9, f'value 9'], [10, f'value 10'],
        ],
        verbose_name='[Your decision]',
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )
    pun_norm_decision1 = models.IntegerField(
        initial=0,
        choices=[
            [0, f'value 0'], [1, f'value 1'], [2, f'value 2'], [3, f'value 3'], [4, f'value 4'], [5, f'value 5'],
        ],
        verbose_name='[Your decision]',
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )

    treatment = models.StringField()
    #dictator_country = models.StringField()
    #receiver_country = models.StringField()


# PAGES
class PunishmentPage(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.treatment == "3PP punish" or player.treatment == "2PP punish"
    form_model = 'player'
    form_fields = ['pun_decision1']#, 'decision2']
    @staticmethod
    def vars_for_template(player: Player):
        text = "How much do you punish Person A?"
        image = 'baseline/{}.png'.format(player.treatment)
        print('Generating image path and round number - 1', image, player.round_number - 1)

        return {
            'treatment': player.treatment,
            'treatment_text': text,
            'image': image,
            'pun_decision1':player.pun_decision1,
            #'decision2': player.decision2,
            #'receiver_country': player.receiver_country
        }
    def before_next_page(player: Player, timeout_happened):
        #player.payoff = 10 - player.pun_decision1
        player.payoff = C.punishment_points - player.pun_decision1



class DictatorPage(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.treatment == "3PP give" or player.treatment == "DG give" or player.treatment == "2PP give"

    form_model = 'player'
    form_fields = ['dic_decision1']  # , 'decision2']

    @staticmethod
    def vars_for_template(player: Player):
        text = "How much do you give to Person B?"
        image = 'baseline/{}.png'.format(player.treatment)
        print('Generating image path and round number - 1', image, player.round_number - 1)

        return {
            'treatment': player.treatment,
            'treatment_text': text,
            'image': image,
            'dic_decision1': player.dic_decision1,
            # 'decision2': player.decision2,
            # 'receiver_country': player.receiver_country
        }
    def before_next_page(player: Player, timeout_happened):
        player.payoff = C.total_endowment - player.dic_decision1


class DictatorNormPage(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.treatment == "3PP give norm" or player.treatment == "DG give norm" or player.treatment == "2PP give norm"

    form_model = 'player'
    form_fields = ['dic_norm_decision1']

    @staticmethod
    def vars_for_template(player: Player):
        text = "How socially acceptable is it to give"
        image = 'baseline/{}.png'.format(player.treatment)
        print('Generating image path and round number - 1', image, player.round_number - 1)

        return {
            'treatment': player.treatment,
            'treatment_text': text,
            'image': image,
            'dic_norm_decision1': player.dic_norm_decision1,
            # 'decision2': player.decision2,
            # 'receiver_country': player.receiver_country
        }
    # def before_next_page(player: Player, timeout_happened):
    #     player.payoff = C.total_endowment - player.dic_norm_decision1

class PunishmentNormPage(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.treatment == "3PP punish norm" or player.treatment == "2PP punish norm"

    form_model = 'player'
    form_fields = ['pun_norm_decision1']

    @staticmethod
    def vars_for_template(player: Player):
        text1 = "How socially acceptable is it to punish"
        text2 = "when Person A gave"
        image = 'baseline/{}.png'.format(player.treatment)
        print('Generating image path and round number - 1', image, player.round_number - 1)

        return {
            'treatment': player.treatment,
            'treatment_text1': text1,
            'treatment_text2': text2,
            'image': image,
            'pun_norm_decision1': player.pun_norm_decision1,
            # 'decision2': player.decision2,
            # 'receiver_country': player.receiver_country
        }
    # def before_next_page(player: Player, timeout_happened):
    #     player.payoff = C.total_endowment - player.dic_norm_decision1

class Results(Page):
    pass

class instructionPage(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

#page_sequence = [instructionPage, baselinePage, Results]
page_sequence = [DictatorPage, PunishmentPage, DictatorNormPage, PunishmentNormPage]
#page_sequence = [PunishmentPage]
