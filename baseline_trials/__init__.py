from otree.api import *
import random
import logging

from otree.models import player

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'baseline_trials'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 44 #14

    CURRENT_COUNTRY = 'us' # CHANGE TO COUNTRY FOR THIS LINK

    COUNTRY_LIST = ['us', 'ae', 'bl', 'de', 'fr', 'ad'] # test list

    # # Load country codes
    # with open('TPP_game/country_codes.txt', 'r') as file:
    #     COUNTRY_LIST = [line.strip() for line in file]

    total_endowment = 12
    dictator_keeps_1 = total_endowment  # everything
    dictator_keeps_2 = total_endowment * (3 / 4)  # three quarters
    dictator_keeps_3 = total_endowment * (2 / 3)  # two thirds
    dictator_keeps_4 = total_endowment * (1 / 2)  # half
    punishment_points = total_endowment * (1 / 3)

    receiver_endowment = 0
    TP_points = 4
    TP_effectiveness = 3
    dictator_keeps = 8  # Should eventually be list: [30, 25, 20, 15]
    norm_strategy_dic_gives = 2  # Should eventually be list: [0, 5, 10, 15] : different levels of dictator giving
    norm_strategy_dic_gives_binary = 3  # Should eventually be list: ??? [0, 10]? Selfish or less selfish dictator
    norm_strategy_punish_norm = 1  # Should eventually be list with 3-4 scenarios: ??? [0, 3, 7, 10]?

    ### Treatments

    ## 1) Baseline

    trials_DG = ['0DG give', '0DG give norm']
    trials_3PP_DIC = ['3PP give']
    trials_3PP_TP = ['3PP punish', '3PP punish norm']
    trials_2PP_DIC = ['2PP give']
    trials_2PP_TP = ['2PP punish', '2PP punish norm']
    trials_3PR_DIC = ['3PR give']
    trials_3PR_TP = ['3PR reward', '3PR reward norm']
    trials_3PC_DIC = ['3PC give']
    trials_3PC_TP = ['3PC comp', '3PC comp norm']

    ## 2) Ingroup - outgroup

    trials_3PP_INOUT_DIC = ['3PP give IN', '3PP give OUT']
    trials_3PP_INOUT_TP = ['3PP punish IN IN', '3PP punish IN OUT', '3PP punish OUT IN',
                        '3PP punish OUT OUT',
                        '3PP punish norm IN IN', '3PP punish norm OUT OUT']
    # trials_3PR_INOUT = ['3PR give IN', '3PR give OUT',
    #                     '3PR reward IN IN', '3PR reward IN OUT', '3PR reward OUT IN',
    #                     '3PR reward OUT OUT',
    #                     '3PR reward norm IN IN', '3PR reward norm OUT OUT']
    trials_3PC_INOUT_DIC = ['3PC give IN', '3PC give OUT']
    trials_3PC_INOUT_TP = ['3PC comp IN IN', '3PC comp IN OUT', '3PC comp OUT IN',
                        '3PC comp OUT OUT',
                        '3PC comp norm IN IN', '3PC comp norm OUT OUT']

    ## 3) Country - partner

    # Define number of trials for each trial type
    number_trials_partner_dic_out = 2 # dictator role
    number_trials_partner_in_out = 3
    number_trials_partner_out_in = 3
    number_trials_partner_out_out_homog = 3
    number_trials_partner_out_out_heterog = 3





class Subsession(BaseSubsession):
    pass


def creating_session(subsession):
    print('Creating session; round number: {}'.format(subsession.round_number))

    ## Make immutable variables for partner-country block

    # Make country list without current country
    country_list_no_current = [entry for entry in C.COUNTRY_LIST if entry != C.CURRENT_COUNTRY]

    # Make all possible combinations
    combinations = [(x, y) for x in C.COUNTRY_LIST for y in C.COUNTRY_LIST]

    # Filter IN-IN trials, because every participant needs to see one IN-IN trial as punisher
    combinations = [entry for entry in combinations if not entry[0] == entry[1] == C.CURRENT_COUNTRY]

    # Filter different trial types
    trials_partner_in_out = [entry for entry in combinations if entry[0] == C.CURRENT_COUNTRY]
    trials_partner_out_in = [entry for entry in combinations if entry[1] == C.CURRENT_COUNTRY]
    trials_partner_out_out_homog = [entry for entry in combinations if
                                    (entry[0] != C.CURRENT_COUNTRY and entry[1] != C.CURRENT_COUNTRY and entry[0] ==
                                     entry[1])]
    trials_partner_out_out_heterog = [entry for entry in combinations if
                                      (entry[0] != C.CURRENT_COUNTRY and entry[1] != C.CURRENT_COUNTRY and entry[0] !=
                                       entry[1])]


    # Duplicate original pools of trial types for removing used trials (and later refilling pools once empty)
    country_list_no_current_editable = country_list_no_current.copy()
    trials_partner_in_out_editable = trials_partner_in_out.copy()
    trials_partner_out_in_editable = trials_partner_out_in.copy()
    trials_partner_out_out_homog_editable = trials_partner_out_out_homog.copy()
    trials_partner_out_out_heterog_editable = trials_partner_out_out_heterog.copy()

    # Make sampling function to sample without replacement
    def sample_trials_partner(pool, num_trials, pool_name):
        # If empty, refill from the original pool
        print("pool used ", pool)
        # There are problems with eval(poolname), therefore assign original pool manually
        if pool_name == 'country_list_no_current': pool_original = country_list_no_current
        if pool_name == 'trials_partner_out_in': pool_original = trials_partner_out_in
        if pool_name == 'trials_partner_in_out': pool_original = trials_partner_in_out
        if pool_name == 'trials_partner_out_out_homog': pool_original = trials_partner_out_out_homog
        if pool_name == 'trials_partner_out_out_heterog': pool_original = trials_partner_out_out_heterog
        # If pool is depleted, refresh
        if len(pool) < num_trials:
            # print("country_list_no_current ", country_list_no_current)
            pool = pool_original.copy()
            #pool = eval(pool_name).copy()
            print("pool refreshed, pool ", pool)
        # Otherwise, keep sampling without replacement
        trials = random.sample(pool, num_trials)
        print("trials chosen ", trials)
        for trial in trials:
            pool.remove(trial)
        return trials, pool

    ### Loop through participants to create randomization

    if subsession.round_number == 1:
        for player in subsession.get_players():
            participant = player.participant

            ### RANDOMIZATION

            ## 1) Baseline trials

            trials_DG_current = random.sample(C.trials_DG, len(C.trials_DG)) # Randomize the order of give, punish, norm per treatment type (DG, 3PP, 2PP, 3PR, 3PC)
            # First randomize the TP trials
            trials_3PP_TP_current = random.sample(C.trials_3PP_TP, len(C.trials_3PP_TP))
            trials_2PP_TP_current = random.sample(C.trials_2PP_TP, len(C.trials_2PP_TP))
            trials_3PR_TP_current = random.sample(C.trials_3PR_TP, len(C.trials_3PR_TP))
            trials_3PC_TP_current = random.sample(C.trials_3PC_TP, len(C.trials_3PC_TP))
            # Second, add DIC trial either before or after
            trials_3PP_current = trials_3PP_TP_current + C.trials_3PP_DIC if random.choice([True, False]) else C.trials_3PP_DIC + trials_3PP_TP_current
            trials_2PP_current = trials_2PP_TP_current + C.trials_2PP_DIC if random.choice([True, False]) else C.trials_2PP_DIC + trials_2PP_TP_current
            trials_3PR_current = trials_3PR_TP_current + C.trials_3PR_DIC if random.choice([True, False]) else C.trials_3PR_DIC + trials_3PR_TP_current
            trials_3PC_current = trials_3PC_TP_current + C.trials_3PC_DIC if random.choice([True, False]) else C.trials_3PC_DIC + trials_3PC_TP_current
            # Third, randomize order of treatments (3PP, 2PP, 3PR, 3PC)
            order_baseline = random.sample([trials_3PP_current, trials_2PP_current, trials_3PR_current, trials_3PC_current], 4)
            order_baseline_flat = [item for sublist in order_baseline for item in sublist]  # Flatten the nested lists
            # Complete randomized list (DG always first)
            participant.treatment_order_baseline  = trials_DG_current + order_baseline_flat


            ## 2) Ingroup - outgroup trials

            # First, randomize the DIC trials
            trials_3PP_INOUT_DIC_current = random.sample(C.trials_3PP_INOUT_DIC, len(C.trials_3PP_INOUT_DIC))
            trials_3PC_INOUT_DIC_current = random.sample(C.trials_3PC_INOUT_DIC, len(C.trials_3PC_INOUT_DIC))
            # Second, randomize the TP trials
            trials_3PP_INOUT_TP_current = random.sample(C.trials_3PP_INOUT_TP, len(C.trials_3PP_INOUT_TP))
            trials_3PC_INOUT_TP_current = random.sample(C.trials_3PC_INOUT_TP, len(C.trials_3PC_INOUT_TP))
            # Third, randomize order of DIC/TP
            trials_3PP_INOUT_current = trials_3PP_INOUT_TP_current + trials_3PP_INOUT_DIC_current if random.choice(
                [True, False]) else trials_3PP_INOUT_DIC_current + trials_3PP_INOUT_TP_current
            trials_3PC_INOUT_current = trials_3PC_INOUT_TP_current + trials_3PC_INOUT_DIC_current if random.choice(
                [True, False]) else trials_3PC_INOUT_DIC_current + trials_3PC_INOUT_TP_current
            # Fourth, randomize order of treatments (3PP, 2PP, 3PR, 3PC)
            order_INOUT = random.sample(
                [trials_3PP_INOUT_current, trials_3PC_INOUT_current], 2)
            order_INOUT_flat = [item for sublist in order_INOUT for item in sublist]  # Flatten the nested lists
            participant.treatment_order_INOUT = order_INOUT_flat


            ## 3) Country partners

            # a) Dictator role

            trials_partner_dic_out_current, country_list_no_current_editable = sample_trials_partner(country_list_no_current_editable, C.number_trials_partner_dic_out, "country_list_no_current")

            # b) Punisher role

            trials_partner_in_in_current = [(C.CURRENT_COUNTRY, C.CURRENT_COUNTRY)]
            trials_partner_in_out_current, trials_partner_in_out_editable = sample_trials_partner(trials_partner_in_out_editable, C.number_trials_partner_in_out, "trials_partner_in_out")
            trials_partner_out_in_current, trials_partner_out_in_editable = sample_trials_partner(trials_partner_out_in_editable, C.number_trials_partner_out_in, "trials_partner_out_in")
            trials_partner_out_out_homog_current, trials_partner_out_out_homog_editable = sample_trials_partner(trials_partner_out_out_homog_editable, C.number_trials_partner_out_out_homog, "trials_partner_out_out_homog")
            trials_partner_out_out_heterog_current, trials_partner_out_out_heterog_editable = sample_trials_partner(trials_partner_out_out_heterog_editable, C.number_trials_partner_out_out_heterog, "trials_partner_out_out_heterog")

            # c) Merge and randomize order of trials within punisher role

            trials_partner_TP_current = trials_partner_in_in_current + trials_partner_in_out_current + trials_partner_out_in_current + trials_partner_out_out_homog_current + trials_partner_out_out_heterog_current

            # Add 3PP treatment identifier for referring to treatment and flatten list (tuples produce errors)
            trials_partner_TP_current = [
                " ".join(tup) + " 3PP country" if isinstance(tup, tuple) else tup
                for tup in trials_partner_TP_current
            ]

            # Shuffle the merged list
            random.shuffle(trials_partner_TP_current)

            # d) Randomize order of DIC/TP
            participant.treatment_order_partner = trials_partner_TP_current + trials_partner_dic_out_current if random.choice(
                [True, False]) else trials_partner_dic_out_current + trials_partner_TP_current

            ## 4) Put all treatment orders together
            participant.treatment_order = participant.treatment_order_baseline + participant.treatment_order_INOUT + participant.treatment_order_partner
            print('set treatment_order to', participant.treatment_order)

            # Check where role switches take place for announcements
            participant.role_switch = [
                participant.treatment_order[i]
                for i in range(1, len(participant.treatment_order))
                if ("give" in participant.treatment_order[i] and "give" not in participant.treatment_order[i - 1]) or
                   ("give" not in participant.treatment_order[i] and "give" in participant.treatment_order[i - 1])
            ]


            ## 5) Put instruction round before trials from new treatment type
            participant.instruction_round = [trials_DG_current[0], trials_3PP_current[0], trials_2PP_current[0],
                                             trials_3PR_current[0], trials_3PC_current[0],
                                             trials_3PP_INOUT_current[0], trials_3PC_INOUT_current[0],
                                             participant.treatment_order[len(participant.treatment_order_baseline + participant.treatment_order_INOUT)]]


    #breakpoint()

    for player in subsession.get_players():
        #player.treatment = player.participant.treatment_order_baseline[player.round_number - 1] # For testing only baseline
        #player.treatment = player.participant.treatment_order_INOUT[player.round_number - 1] # For testing only INOUT
        player.treatment = player.participant.treatment_order[player.round_number - 1]
        player.instruction_round_true = player.treatment in player.participant.instruction_round # Boolean that indicates if instruction page should be shown: Always before the first trial of a new treatment type
        player.role_switch_true = player.treatment in player.participant.role_switch  # Boolean that indicates if instruction page should be shown: Always before the first trial of a new treatment type
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
    role_switch_true = models.BooleanField()
    #dictator_country = models.StringField()
    #receiver_country = models.StringField()


# PAGES
class TPPage(Page):
    @staticmethod
    def is_displayed(player: Player):
        # return player.treatment == "3PP punish" or player.treatment == "2PP punish" or player.treatment == '3PR reward' or player.treatment == '3PC comp'
        return ("punish" in player.treatment or "reward" in player.treatment or "comp" in player.treatment or "3PP country" in player.treatment) and "norm" not in player.treatment
    form_model = 'player'
    form_fields = ['TP_decision1', 'TP_decision2', 'TP_decision3', 'TP_decision4']
    @staticmethod
    def vars_for_template(player: Player):
        if "2PP punish" in player.treatment:
            text_action = "take away"
            text_receiver = "from Person A"
            image = 'global/treatments/2PP punish.png'
        if "3PP punish" in player.treatment or "3PP country" in player.treatment:
            text_action = "take away"
            text_receiver = "from Person A"
            image = 'global/treatments/3PP punish.png'
        if "reward" in player.treatment:
            text_action = "give"
            text_receiver = "to Person A"
            image = 'global/treatments/3PP punish.png'
        if "comp" in player.treatment:
            text_action = "give"
            text_receiver = "to Person B"
            image = 'global/treatments/3PC comp.png'

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
            
        # For partner country trials, extract countries of dictator and recipient
        if "3PP country" in player.treatment:
            dic_identity = player.treatment[:2]
            recip_identity = player.treatment[3:5]

        print('Generating image path and round number - 1', image, player.round_number - 1)

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
            role_switch_true = player.role_switch_true,
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
            image = 'global/treatments/2PP punish.png'
        if "3PP punish" in player.treatment:
            text_action = "take away"
            text_receiver = "from Person A"
            image = 'global/treatments/3PP punish.png'
        if "reward" in player.treatment:
            text_action = "give"
            text_receiver = "to Person A"
            image = 'global/treatments/3PP punish.png'
        if "comp" in player.treatment:
            text_action = "give"
            text_receiver = "to Person B"
            image = 'global/treatments/3PC comp.png'

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
        return ("give" in player.treatment or player.treatment in C.COUNTRY_LIST) #and "norm" not in player.treatment

    form_model = 'player'

    def get_form_fields(player: Player):
        if "norm" in player.treatment:
            return ['dic_norm_decision1']
        else:
            return ['dic_decision1']

    @staticmethod
    def vars_for_template(player: Player):
        # text = "How much do you give to Person B?"
        image = 'global/treatments/{}.png'.format(player.treatment)
        image = image.replace(" IN", "")
        image = image.replace(" OUT", "")
        image = image.replace(" norm", "")

        # 3PR trials get same image as 3PP
        if "3PR" in player.treatment:
            image = 'global/treatments/3PP give.png'

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

        # For partner country trials, extract countries of recipient (dictator is participant from current country
        if player.treatment in C.COUNTRY_LIST:
            dic_identity = C.CURRENT_COUNTRY
            recip_identity = player.treatment
            image = 'global/treatments/3PP give.png'

        print('Generating image path and round number - 1', image, player.round_number - 1)

        return {
                'treatment': player.treatment,
                'dic_identity': dic_identity,
                'recip_identity': recip_identity,
                'image': image,
                'dic_decision1': player.dic_decision1,
                'dic_norm_decision1': player.dic_norm_decision1,
                'role_switch_true': player.role_switch_true,
            }

    def before_next_page(player: Player, timeout_happened):
        player.payoff = C.total_endowment - player.dic_decision1


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
        image = 'global/treatments/{}.png'.format(player.treatment)
        image = image.replace(" norm", "")
        treatment_type = player.treatment[:3] # Extract the first three characters as treatment type
        print('Generating image path and round number - 1', image, player.round_number - 1)

        return {
            'treatment': player.treatment,
            # 'treatment_text': text,
            'image': image,
            'treatment_type': treatment_type
        }

page_sequence = [instructionPage, DictatorPage, TPPage, TPNormPage]
#page_sequence = [DictatorPage, TPPage]
#page_sequence = [TPPage]
