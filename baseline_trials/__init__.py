from otree.api import *
import random

from otree.models import player

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'baseline_trials'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 5

    CURRENT_COUNTRY = 'us' # CHANGE TO COUNTRY FOR THIS LINK

    ### Treatments

    ## 1) Baseline

    trials_DG = ['0DG give', '0DG give norm']
    trials_3PP = ['3PP give', '3PP punish', '3PP punish norm']
    trials_2PP = ['2PP give', '2PP punish', '2PP punish norm']
    trials_3PR = ['3PR give', '3PR reward', '3PR reward norm']
    trials_3PC = ['3PC give', '3PC comp', '3PC comp norm']

    ## 2) Ingroup - outgroup

    trials_3PP_INOUT = ['3PP give IN', '3PP give OUT', '3PP give norm IN', '3PP give norm OUT',
                        '3PP punish IN IN', '3PP punish IN OUT', '3PP punish OUT IN',
                        '3PP punish OUT OUT',
                        '3PP punish norm IN IN', '3PP punish norm OUT OUT']
    trials_3PR_INOUT = ['3PR give IN', '3PR give OUT', '3PR give norm IN', '3PR give norm OUT',
                        '3PR reward IN IN', '3PR reward IN OUT', '3PR reward OUT IN',
                        '3PR reward OUT OUT',
                        '3PR reward norm IN IN', '3PR reward norm OUT OUT']
    trials_3PC_INOUT = ['3PC give IN', '3PC give OUT', '3PC give norm IN', '3PC give norm OUT',
                        '3PC comp IN IN', '3PC comp IN OUT', '3PC comp OUT IN',
                        '3PC comp OUT OUT',
                        '3PC comp norm IN IN', '3PC comp norm OUT OUT']

    # total_endowment = 30
    # receiver_endowment = 0
    # TP_points = 10
    # TP_effectiveness = 3
    # dictator_keeps = 23  # Should eventually be list: [30, 25, 20, 15]
    # norm_strategy_dic_gives = 5 # Should eventually be list: [0, 5, 10, 15] : different levels of dictator giving
    # norm_strategy_dic_gives_binary = 10 # Should eventually be list: ??? [0, 10]? Selfish or less selfish dictator
    # norm_strategy_punish_norm = 3 # Should eventually be list with 3-4 scenarios: ??? [0, 3, 7, 10]?
    total_endowment = 12
    dictator_keeps_1 = total_endowment  # everything
    dictator_keeps_2 = total_endowment * (1 / 4)  # quarter
    dictator_keeps_3 = total_endowment * (1 / 3)  # third
    dictator_keeps_4 = total_endowment * (1 / 2)  # half
    punishment_points = total_endowment * (1 / 3)


    receiver_endowment = 0
    TP_points = 4
    TP_effectiveness = 3
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

            ### RANDOMIZATION

            ## 1) Baseline trials

            trials_DG_current = random.sample(C.trials_DG, len(C.trials_DG)) # Randomize the order of give, punish, norm per treatment type (DG, 3PP, 2PP, 3PR, 3PC)
            trials_3PP_current = random.sample(C.trials_3PP, len(C.trials_3PP))
            #trials_2PP_current = random.sample(C.trials_2PP, len(C.trials_2PP))
            #trials_3PR_current = random.sample(C.trials_3PR, len(C.trials_3PR))
            #trials_3PC_current = random.sample(C.trials_3PC, len(C.trials_3PC))
            #order_baseline = random.sample([trials_3PP_current, trials_2PP_current, trials_3PR_current, trials_3PC_current], 4)
            #order_baseline_flat = [item for sublist in order_baseline for item in sublist]  # Flatten the nested lists
            # Assign randomized list (DG always first)
            #participant.treatment_order_baseline  = trials_DG_current + order_baseline_flat
            participant.treatment_order_baseline  = trials_DG_current + trials_3PP_current

            #print('set treatment_order_baseline to', participant.treatment_order_baseline)

            ## 2) Ingroup - outgroup trials
            trials_3PP_INOUT_current = random.sample(C.trials_3PP_INOUT, len(C.trials_3PP_INOUT))
            trials_3PR_INOUT_current = random.sample(C.trials_3PR_INOUT, len(C.trials_3PR_INOUT))
            trials_3PC_INOUT_current = random.sample(C.trials_3PC_INOUT, len(C.trials_3PC_INOUT))

            order_INOUT = random.sample(
                [trials_3PP_INOUT_current, trials_3PR_INOUT_current, trials_3PC_INOUT_current], 3)
            order_INOUT_flat = [item for sublist in order_INOUT for item in sublist]  # Flatten the nested lists
            participant.treatment_order_INOUT = order_INOUT_flat

            #print('set treatment_order_INOUT to', participant.treatment_order_INOUT)

            ## 3) Country partners

            ## 4) Put all treatment orders together
            participant.treatment_order = participant.treatment_order_baseline + participant.treatment_order_INOUT
            print('set treatment_order to', participant.treatment_order)

            ## 5) Put instruction round before trials from new treatment type
            # participant.instruction_round = [trials_DG_current[0], trials_3PP_current[0], trials_2PP_current[0],
            #                                  trials_3PR_current[0], trials_3PC_current[0],
            #                                  trials_3PP_INOUT_current[0], trials_3PR_INOUT_current[0], trials_3PC_INOUT_current[0]]

            participant.instruction_round = [trials_3PP_current[0]]

    for player in subsession.get_players():
        #player.treatment = player.participant.treatment_order_baseline[player.round_number - 1] # For testing only baseline
        #player.treatment = player.participant.treatment_order_INOUT[player.round_number - 1] # For testing only INOUT
        player.treatment = player.participant.treatment_order[player.round_number - 1]
        player.instruction_round_true = player.treatment in player.participant.instruction_round # Boolean that indicates if instruction page should be shown: Always before the first trial of a new treatment type
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
    TP_decision1 = models.IntegerField(
        initial=0,
        choices=[
            [0, f'value 0'], [1, f'value 1'], [2, f'value 2'], [3, f'value 3'], [4, f'value 4'], [5, f'value 5'],
            [6, f'value 6'], [7, f'value 7'], [8, f'value 8'], [9, f'value 9'], [10, f'value 10'],
        ],
        verbose_name='[Your decision]',
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )
    TP_decision2 = models.IntegerField(
        initial=0,
        choices=[
            [0, f'value 0'], [1, f'value 1'], [2, f'value 2'], [3, f'value 3'], [4, f'value 4'], [5, f'value 5'],
            [6, f'value 6'], [7, f'value 7'], [8, f'value 8'], [9, f'value 9'], [10, f'value 10'],
        ],
        verbose_name='[Your decision]',
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )
    TP_decision3 = models.IntegerField(
        initial=0,
        choices=[
            [0, f'value 0'], [1, f'value 1'], [2, f'value 2'], [3, f'value 3'], [4, f'value 4'], [5, f'value 5'],
            [6, f'value 6'], [7, f'value 7'], [8, f'value 8'], [9, f'value 9'], [10, f'value 10'],
        ],
        verbose_name='[Your decision]',
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )
    TP_decision4 = models.IntegerField(
        initial=0,
        choices=[
            [0, f'value 0'], [1, f'value 1'], [2, f'value 2'], [3, f'value 3'], [4, f'value 4'], [5, f'value 5'],
            [6, f'value 6'], [7, f'value 7'], [8, f'value 8'], [9, f'value 9'], [10, f'value 10'],
        ],
        verbose_name='[Your decision]',
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )
    TP_norm_decision1 = models.IntegerField(
        initial=0,
        choices=[
            [0, f'value 0'], [1, f'value 1'], [2, f'value 2'], [3, f'value 3'], [4, f'value 4'], [5, f'value 5'],
        ],
        verbose_name='[Your decision]',
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )

    treatment = models.StringField()
    instruction_round_true = models.BooleanField()
    #dictator_country = models.StringField()
    #receiver_country = models.StringField()


# PAGES
class TPPage(Page):
    @staticmethod
    def is_displayed(player: Player):
        # return player.treatment == "3PP punish" or player.treatment == "2PP punish" or player.treatment == '3PR reward' or player.treatment == '3PC comp'
        return ("punish" in player.treatment or "reward" in player.treatment or "comp" in player.treatment) and "norm" not in player.treatment
    form_model = 'player'
    form_fields = ['TP_decision1', 'TP_decision2', 'TP_decision3', 'TP_decision4']
    @staticmethod
    def vars_for_template(player: Player):
        if "2PP punish" in player.treatment:
            text_action = "take away"
            text_receiver = "from Person A"
            image = 'baseline/2PP punish.png'
        if "3PP punish" in player.treatment:
            text_action = "take away"
            text_receiver = "from Person A"
            image = 'baseline/3PP punish.png'
        if "reward" in player.treatment:
            text_action = "give"
            text_receiver = "to Person A"
            image = 'baseline/3PR reward.png'
        if "comp" in player.treatment:
            text_action = "give"
            text_receiver = "to Person B"
            image = 'baseline/3PC comp.png'

        print('Generating image path and round number - 1', image, player.round_number - 1)

        # For INOUT trials, check identity of dictator and recipient
        if "IN IN" in player.treatment:
            dic_identity = C.CURRENT_COUNTRY
            recip_identity = C.CURRENT_COUNTRY
        if "IN OUT" in player.treatment:
            dic_identity = C.CURRENT_COUNTRY
            recip_identity = "out"
        if "OUT IN" in player.treatment:
            dic_identity = "out"
            recip_identity = C.CURRENT_COUNTRY
        if "OUT OUT" in player.treatment:
            dic_identity = "out"
            recip_identity = "out"
        if "OUT" not in player.treatment and "IN" not in player.treatment:
            dic_identity = "baseline"
            recip_identity = "baseline"

        return dict(
            TP_decisions=[
                dict(
                    index=1,
                    TP_decision=player.TP_decision1,
                    dictator_keeps=C.dictator_keeps_1,
                    receiver=C.total_endowment - C.dictator_keeps_1,
                ),
                dict(
                    index=2,
                    TP_decision=player.TP_decision2,
                    dictator_keeps=C.dictator_keeps_2,
                    receiver=C.total_endowment - C.dictator_keeps_2,
                ),
                dict(
                    index=3,
                    TP_decision=player.TP_decision3,
                    dictator_keeps=C.dictator_keeps_3,
                    receiver=C.total_endowment - C.dictator_keeps_3,
                ),
                dict(
                    index=4,
                    TP_decision=player.TP_decision4,
                    dictator_keeps=C.dictator_keeps_4,
                    receiver=C.total_endowment - C.dictator_keeps_4,
                ),
            ],
            #receiver_country=player.receiver_country,
            #dictator_country=player.dictator_country,
            TP_points=range(0, int(C.TP_points) + 1),
            TP_effectiveness=C.TP_effectiveness,
            treatment=player.treatment,
            dic_identity=dic_identity,
            recip_identity=recip_identity,
            treatment_text_action=text_action,
            treatment_text_receiver=text_receiver,
            image=image,
            )

    def before_next_page(player: Player, timeout_happened):
        #player.payoff = 10 - player.TP_decision1
        player.payoff = C.TP_points - player.TP_decision1


class TPNormPage(Page):
    @staticmethod
    def is_displayed(player: Player):
        # return player.treatment == "3PP punish norm" or player.treatment == "2PP punish norm"  or player.treatment == '3PR reward norm' or player.treatment == '3PC comp norm'
        return ("punish" in player.treatment or "reward" in player.treatment or "comp" in player.treatment) and "norm" in player.treatment

    form_model = 'player'
    form_fields = ['TP_norm_decision1']

    @staticmethod
    def vars_for_template(player: Player):
        # text1 = "How socially acceptable is it to punish"
        if "2PP punish" in player.treatment:
            text_action = "take away"
            text_receiver = "from Person A"
            image = 'baseline/2PP punish.png'
        if "3PP punish" in player.treatment:
            text_action = "take away"
            text_receiver = "from Person A"
            image = 'baseline/3PP punish.png'
        if "reward" in player.treatment:
            text_action = "give"
            text_receiver = "to Person A"
            image = 'baseline/3PR reward.png'
        if "comp" in player.treatment:
            text_action = "give"
            text_receiver = "to Person B"
            image = 'baseline/3PC comp.png'

        print('Generating image path and round number - 1', image, player.round_number - 1)

        # For INOUT trials, check identity of dictator and recipient
        if "IN IN" in player.treatment:
            dic_identity = C.CURRENT_COUNTRY
            recip_identity = C.CURRENT_COUNTRY
        if "IN OUT" in player.treatment:
            dic_identity = C.CURRENT_COUNTRY
            recip_identity = "out"
        if "OUT IN" in player.treatment:
            dic_identity = "out"
            recip_identity = C.CURRENT_COUNTRY
        if "OUT OUT" in player.treatment:
            dic_identity = "out"
            recip_identity = "out"
        if "OUT" not in player.treatment and "IN" not in player.treatment:
            dic_identity = "baseline"
            recip_identity = "baseline"

        return {
            'treatment': player.treatment,
            'dic_identity': dic_identity,
            'recip_identity': recip_identity,
            'treatment_text_action': text_action,
            'treatment_text_receiver': text_receiver,
            'image': image,
            'TP_norm_decision1': player.TP_norm_decision1,
            # 'decision2': player.decision2,
            # 'receiver_country': player.receiver_country
        }

class DictatorPage(Page):
    @staticmethod
    def is_displayed(player: Player):
        # return player.treatment == "3PP give" or player.treatment == "0DG give" or player.treatment == "2PP give" or player.treatment == "3PR give" or player.treatment == "3PC give"
        return "give" in player.treatment and "norm" not in player.treatment

    form_model = 'player'
    form_fields = ['dic_decision1']  # , 'decision2']

    @staticmethod
    def vars_for_template(player: Player):
        # text = "How much do you give to Person B?"
        image = 'baseline/{}.png'.format(player.treatment)
        image = image.replace(" IN", "")
        image = image.replace(" OUT", "")
        print('Generating image path and round number - 1', image, player.round_number - 1)

        # For INOUT trials, check identity of recipient
        if player.treatment[-3:] == "OUT":
            recip_identity = "out"
            dic_identity = C.CURRENT_COUNTRY  # In give trials, participant is the dicatator --> identity of dictator is current country
        if player.treatment[-3:] == " IN":
            recip_identity = C.CURRENT_COUNTRY
            dic_identity = C.CURRENT_COUNTRY
        if "OUT" not in player.treatment and "IN" not in player.treatment:
            dic_identity = "baseline"
            recip_identity = "baseline"

        return {
                'treatment': player.treatment,
                'dic_identity': dic_identity,
                'recip_identity': recip_identity,
                # 'treatment_text': text,
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
        # return player.treatment == "3PP give norm" or player.treatment == "0DG give norm" or player.treatment == "2PP give norm"
        return "give" in player.treatment and "norm" in player.treatment

    form_model = 'player'
    form_fields = ['dic_norm_decision1']

    @staticmethod
    def vars_for_template(player: Player):
        # text = "How socially acceptable is it to give"
        image = 'baseline/{}.png'.format(player.treatment)
        image = image.replace(" norm", "")
        image = image.replace(" IN", "")
        image = image.replace(" OUT", "")

        print('Generating image path and round number - 1', image, player.round_number - 1)

        # For INOUT trials, check identity of recipient
        if player.treatment[-3:] == "OUT":
            recip_identity = "out"
            dic_identity = C.CURRENT_COUNTRY  # In give trials, participant is the dicatator --> identity of dictator is current country
        if player.treatment[-3:] == " IN":
            recip_identity = C.CURRENT_COUNTRY
            dic_identity = C.CURRENT_COUNTRY

        if "OUT" not in player.treatment and "IN" not in player.treatment:
            dic_identity = "baseline"
            recip_identity = "baseline"

        return {
            'treatment': player.treatment,
            'dic_identity': dic_identity,
            'recip_identity': recip_identity,
            # 'treatment_text': text,
            'image': image,
            'dic_norm_decision1': player.dic_norm_decision1,
            # 'decision2': player.decision2,
            # 'receiver_country': player.receiver_country
        }
    # def before_next_page(player: Player, timeout_happened):
    #     player.payoff = C.total_endowment - player.dic_norm_decision1



class Results(Page):
    pass

class instructionPage(Page):
    # print('player.participant.instruction_round', player.participant.instruction_round)
    @staticmethod
    def is_displayed(player: Player):
        # return player.round_number == 1
        return player.instruction_round_true

    @staticmethod
    def vars_for_template(player: Player):
        # text = "How socially acceptable is it to give"
        image = 'baseline/{}.png'.format(player.treatment)
        image = image.replace(" norm", "")
        treatment_type = player.treatment[:3] # Extract the first three characters as treatment type
        print('Generating image path and round number - 1', image, player.round_number - 1)

        return {
            'treatment': player.treatment,
            # 'treatment_text': text,
            'image': image,
            'treatment_type': treatment_type
        }

#page_sequence = [instructionPage, baselinePage, Results]
page_sequence = [instructionPage, DictatorPage, TPPage, DictatorNormPage, TPNormPage]
#page_sequence = [TPPage]
