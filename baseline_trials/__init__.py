from otree.api import *
import random
import logging

from otree.models import player

from itertools import chain

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'baseline_trials'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 53

    import csv

    CURRENT_COUNTRY = 'ch' # CHANGE TO COUNTRY FOR THIS LINK

    with open('_static/global/country_codes.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)  # Create reader object
        next(reader)  # Skip the header
        COUNTRIES = {row[0]: row[1] for row in reader}  # Store column 1 as keys, column 2 as values

    COUNTRY_LIST = list(COUNTRIES.keys())
    #COUNTRY_LIST = ['us', 'ae', 'bl', 'de', 'fr', 'ad'] # test list

    CURRENT_COUNTRYNAME = COUNTRIES.get(CURRENT_COUNTRY)


    # # Load country codes
    # with open('TPP_game/country_codes.txt', 'r') as file:
    #     COUNTRY_LIST = [line.strip() for line in file]

    # Variables for decision scenarios
    total_endowment = 12
    receiver_endowment = 0
    dictator_keeps_everything = total_endowment  # everything
    dictator_keeps_3quarters = int(total_endowment * (3 / 4))  # three quarters
    dictator_keeps_half = int(total_endowment * (1 / 2))  # half (for rewarding
    TP_points = total_endowment # points available for punishment/rewarding
    TP_effectiveness = 1  # multiplier (currently not using a multiplier anymore so set to 1)
    TP_cost = 3 # fraction of a full point the third party pays to punish/reward/compensate (here a third)
    norm_fixed_TP_points = 3 # fixed amount that was removed/rewarded/compensated for norm decisions

    ### Treatments ###

    ## 1) Baseline (13 trials)
    trials_DG = ['0DG give', '0DG give norm']
    trials_3PP_DIC = ['3PP give']
    trials_3PP_TP = ['3PP punish', '3PP punish norm']
    trials_2PP_DIC = ['2PP give']
    trials_2PP_TP = ['2PP punish', '2PP punish norm']
    trials_3PR_DIC = ['3PR give']
    trials_3PR_TP = ['3PR reward', '3PR reward norm']
    trials_3PC_DIC = ['3PC give']
    trials_3PC_TP = ['3PC comp']

    ## 2) Ingroup - outgroup (14 trials)
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
                        '3PC comp OUT OUT']

    ## 3) Country - partner (26 trials: 5 * 5 + 1 universal norm)
    # Define number of trials for each trial type
    number_trials_partner_dic_out = 5 # dictator role
    number_trials_partner_in_out = 5
    number_trials_partner_out_in = 5
    number_trials_partner_out_out_homog = 5
    number_trials_partner_out_out_heterog = 5


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
    country_list_no_current_editable = [item + " 3PP DIC country" for item in country_list_no_current_editable]
    trials_partner_in_out_editable = trials_partner_in_out.copy()
    trials_partner_out_in_editable = trials_partner_out_in.copy()
    trials_partner_out_out_homog_editable = trials_partner_out_out_homog.copy()
    trials_partner_out_out_heterog_editable = trials_partner_out_out_heterog.copy()

    # Make sampling function to sample without replacement
    def sample_trials_partner(pool, num_trials, pool_name):
        # If empty, refill from the original pool
        #print("pool used ", pool)
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
            #print("pool refreshed, pool ", pool)
        # Otherwise, keep sampling without replacement
        trials = random.sample(pool, num_trials)
        #print("trials chosen ", trials)
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

            #trials_partner_in_in_current = [(C.CURRENT_COUNTRY, C.CURRENT_COUNTRY)] # redundant, already in INOUT
            trials_partner_in_out_current, trials_partner_in_out_editable = sample_trials_partner(trials_partner_in_out_editable, C.number_trials_partner_in_out, "trials_partner_in_out")
            trials_partner_out_in_current, trials_partner_out_in_editable = sample_trials_partner(trials_partner_out_in_editable, C.number_trials_partner_out_in, "trials_partner_out_in")
            trials_partner_out_out_homog_current, trials_partner_out_out_homog_editable = sample_trials_partner(trials_partner_out_out_homog_editable, C.number_trials_partner_out_out_homog, "trials_partner_out_out_homog")
            trials_partner_out_out_heterog_current, trials_partner_out_out_heterog_editable = sample_trials_partner(trials_partner_out_out_heterog_editable, C.number_trials_partner_out_out_heterog, "trials_partner_out_out_heterog")

            # c) Merge and randomize order of trials within punisher role

            trials_partner_TP_current = trials_partner_in_out_current + trials_partner_out_in_current + trials_partner_out_out_homog_current + trials_partner_out_out_heterog_current

            # Add 3PP treatment identifier for referring to treatment and flatten list (tuples produce errors)
            trials_partner_TP_current = [
                " ".join(tup) + " 3PP country" if isinstance(tup, tuple) else tup
                for tup in trials_partner_TP_current
            ]

            # Shuffle the merged list
            random.shuffle(trials_partner_TP_current)

            # d) Randomize order of DIC/TP
            treatment_order_partner_no_univ_norm = trials_partner_TP_current + trials_partner_dic_out_current if random.choice(
                [True, False]) else trials_partner_dic_out_current + trials_partner_TP_current

            # e) Randomize order of universal norm: Either first in block or last in block
            trials_partner_universal_norm = ['universal norm']
            participant.treatment_order_partner = treatment_order_partner_no_univ_norm + trials_partner_universal_norm if random.choice(
                [True, False]) else trials_partner_universal_norm + treatment_order_partner_no_univ_norm

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
        player.first_block_2PP_true = "2PP" in player.participant.treatment_order[2]  # Boolean that indicates if instruction page should be shown: Always before the first trial of a new treatment type
        player.role_switch_true = player.treatment in player.participant.role_switch  # Boolean that indicates if instruction page should be shown: Always before the first trial of a new treatment type

class Group(BaseGroup):
    pass


class Player(BasePlayer):

    treatment = models.StringField()
    instruction_round_true = models.BooleanField()
    first_block_2PP_true = models.BooleanField()
    role_switch_true = models.BooleanField()


    dic_decision1 = models.IntegerField(
        initial=0,
        choices=[(i, f'value {i}') for i in range(C.total_endowment + 1)],  # Dynamically generate choices
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )

    dic_norm_decision1 = models.IntegerField(
        initial=0,
        choices=[(i, f'value {i}') for i in range(C.total_endowment + 1)],
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )

    punish_or_compensate1 = models.IntegerField(
        initial=3,
        choices=[[0, f'punish'], [1, f'compensate'],],
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )
    punish_or_compensate2 = models.IntegerField(
        initial=3,
        choices=[[0, f'punish'], [1, f'compensate'], ],
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )
    punish_or_compensate3 = models.IntegerField(
        initial=3,
        choices=[[0, f'punish'], [1, f'compensate'], ],
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )

    TP_decision1 = models.IntegerField(
        initial=0,
        choices=[(i, f'value {i}') for i in range(C.total_endowment + 1)],
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )
    TP_decision2 = models.IntegerField(
        initial=0,
        choices=[(i, f'value {i}') for i in range(C.total_endowment + 1)],
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )
    TP_decision3 = models.IntegerField(
        initial=0,
        choices=[(i, f'value {i}') for i in range(C.total_endowment + 1)],
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )

    TP_norm_decision1 = models.IntegerField(
        initial=0,
        choices=[
            [0, f'value 0'], [1, f'value 1'], [2, f'value 2'], [3, f'value 3'], [4, f'value 4'], [5, f'value 5'],
        ],
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )
    universal_norm_decision1 = models.IntegerField(
        initial=0,
        choices=[(i, f'value {i}') for i in range(len(C.COUNTRY_LIST) + 1)],
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )
    universal_norm_decision2 = models.IntegerField(
        initial=0,
        choices=[
            [0, f'value 0'], [1, f'value 1'], [2, f'value 2'], [3, f'value 3'], [4, f'value 4'], [5, f'value 5'],
        ],
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )


######## PAGES ########

class Consent(Page):

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == 1:
            return True
        else:
            return False

    def vars_for_template(player: Player):
        return {
            'participation_fee': player.session.config['participation_fee'],
        }

class Introduction(Page):

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == 1:
            return True
        else:
            return False

    def vars_for_template(player: Player):
        return {
            'participation_fee': player.session.config['participation_fee'],
        }

class instructionPage(Page):
    # print('player.participant.instruction_round', player.participant.instruction_round)
    @staticmethod
    def is_displayed(player: Player):
        # return player.round_number == 1
        return player.instruction_round_true

    @staticmethod
    def vars_for_template(player: Player):
        image = 'global/treatments/{}.png'.format(player.treatment)
        image = image.replace(" norm", "")
        image = image.replace("universal norm", "0DG give")
        image = image.replace("2PP", "2PP_2")
        image = image.replace("3PR reward", "3PP punish")
        random_trial_numbers = random.choices(range(7), k=5) # Randomize numbers that are displayed in trial rounds
        random_trial_numbers_diff = [12-value for value in random_trial_numbers]

        if "IN" in player.treatment or "OUT" in player.treatment:
            random_INOUT_IN_as_dic = random.choice([True, False])
            if random_INOUT_IN_as_dic:
                dic_identity = C.CURRENT_COUNTRY
                recip_identity = "out"
                dic_identity_country = C.CURRENT_COUNTRYNAME
                recip_identity_country = "one of 40 countries which also participate in this study"
            else:
                dic_identity = "out"
                recip_identity = C.CURRENT_COUNTRY
                dic_identity_country = "one of 40 countries which also participate in this study"
                recip_identity_country = C.CURRENT_COUNTRYNAME
        elif "country" in player.treatment or "universal norm" in player.treatment:
            random_partner_country_IN_as_dic = random.choice([True, False])
            random_partner = random.choice(C.COUNTRY_LIST)
            if random_partner_country_IN_as_dic:
                dic_identity = C.CURRENT_COUNTRY
                recip_identity = random_partner
                dic_identity_country = C.CURRENT_COUNTRYNAME
                recip_identity_country = C.COUNTRIES.get(random_partner)
            else:
                dic_identity = random_partner
                recip_identity = C.CURRENT_COUNTRY
                dic_identity_country = C.COUNTRIES.get(random_partner)
                recip_identity_country = C.CURRENT_COUNTRYNAME
        else:
            dic_identity = "baseline"
            recip_identity = "baseline"
            recip_identity_country = "baseline"
            dic_identity_country = "baseline"

        treatment_type = player.treatment[:3] # Extract the first three characters as treatment type
        first_block_2PP_true = player.first_block_2PP_true
        block2 = "OUT" in player.treatment or "IN" in player.treatment
        block3 = "country" in player.treatment or "universal norm" in player.treatment
        current_country = C.CURRENT_COUNTRYNAME
        #print('instructionPage Generating image path and round number - 1', image, player.round_number - 1, player.treatment)

        return {
            'treatment': player.treatment,
            # 'treatment_text': text,
            'image': image,
            'random_trial_numbers': random_trial_numbers,
            'random_trial_numbers_diff': random_trial_numbers_diff,
            'dic_identity':dic_identity,
            'recip_identity':recip_identity,
            'dic_identity_country':dic_identity_country,
            'recip_identity_country':recip_identity_country,
            'first_block_2PP_true': first_block_2PP_true,
            'block2': block2,
            'block3': block3,
            'current_country': current_country,
            'treatment_type': treatment_type
        }

class TPPage(Page):

    @staticmethod
    def is_displayed(player: Player):
        # return player.treatment == "3PP punish" or player.treatment == "2PP punish" or player.treatment == '3PR reward' or player.treatment == '3PC comp'
        return "punish" in player.treatment or "reward" in player.treatment or "comp" in player.treatment or "3PP country" in player.treatment #and "norm" not in player.treatment
    form_model = 'player'

    def get_form_fields(player: Player):
        if "norm" in player.treatment:
            return ['TP_norm_decision1']
        else:
            if "comp" in player.treatment:
                return ['TP_decision1', 'TP_decision2', 'TP_decision3',
                        'punish_or_compensate1', 'punish_or_compensate2', 'punish_or_compensate3']
            else:
                return ['TP_decision1', 'TP_decision2', 'TP_decision3']


    @staticmethod
    def vars_for_template(player: Player):
        if "2PP punish" in player.treatment:
            text_action = "remove"
            text_action_person = "for Person B"
            text_receiver = "from Person A"
            image = 'global/treatments/2PP punish.png'
            ## dictator_keeps is assigned here so that we can have different multiple decisions per treatment.
            ## at the moment they are all the same so it is redundant (could be done straight in the dict).
            ## but like this we can switch easily
            dictator_keeps_1 = C.dictator_keeps_everything
            dictator_keeps_2 = C.dictator_keeps_3quarters
            dictator_keeps_3 = C.dictator_keeps_half
        if "3PP punish" in player.treatment or "3PP country" in player.treatment:
            text_action = "remove"
            text_action_person = "for Person C"
            text_receiver = "from Person A"
            image = 'global/treatments/3PP punish.png'
            dictator_keeps_1 = C.dictator_keeps_everything
            dictator_keeps_2 = C.dictator_keeps_3quarters
            dictator_keeps_3 = C.dictator_keeps_half
        if "reward" in player.treatment:
            text_action = "give"
            text_action_person = "for Person C"
            text_receiver = "to Person A"
            image = 'global/treatments/3PP punish.png'
            dictator_keeps_1 = C.dictator_keeps_everything
            dictator_keeps_2 = C.dictator_keeps_3quarters
            dictator_keeps_3 = C.dictator_keeps_half
        if "comp" in player.treatment:
            text_action = "remove"
            text_action_person = "for Person C"
            text_receiver = "from Person A"
            text_action_comp = "give"
            text_action_person_comp = "for Person C"
            text_receiver_comp = "to Person B"
            image = 'global/treatments/3PC comp.png'
            dictator_keeps_1 = C.dictator_keeps_everything
            dictator_keeps_2 = C.dictator_keeps_3quarters
            dictator_keeps_3 = C.dictator_keeps_half
        if "3PR reward norm" in player.treatment:
            text_action = "give"
            text_action_person = "for Person C"
            text_receiver = "to Person A"
            image = 'global/treatments/3PP punish.png'
            dictator_keeps_1 = C.dictator_keeps_half

        # For INOUT trials, check identity of dictator and recipient
        if "IN IN" in player.treatment:
            dic_identity = C.CURRENT_COUNTRY
            recip_identity = C.CURRENT_COUNTRY
            dic_identity_country = C.CURRENT_COUNTRYNAME
            recip_identity_country = C.CURRENT_COUNTRYNAME
        if "IN OUT" in player.treatment:
            dic_identity = C.CURRENT_COUNTRY
            recip_identity = "out"
            dic_identity_country = C.CURRENT_COUNTRYNAME
            recip_identity_country = "one of 40 countries"
        if "OUT IN" in player.treatment:
            dic_identity = "out"
            recip_identity = C.CURRENT_COUNTRY
            dic_identity_country = "one of 40 countries"
            recip_identity_country = C.CURRENT_COUNTRYNAME
        if "OUT OUT" in player.treatment:
            dic_identity = "out"
            recip_identity = "out"
            dic_identity_country = "one of 40 countries"
            recip_identity_country = "one of 40 countries"
        if "OUT" not in player.treatment and "IN" not in player.treatment:
            dic_identity = "baseline"
            recip_identity = "baseline"
            recip_identity_country = "baseline"
            dic_identity_country = "baseline"
            
        # For partner country trials, extract countries of dictator and recipient
        if "3PP country" in player.treatment:
            dic_identity = player.treatment[:2]
            recip_identity = player.treatment[3:5]
            dic_identity_country = C.COUNTRIES.get(dic_identity)
            recip_identity_country = C.COUNTRIES.get(recip_identity)
            dictator_keeps_1 = C.dictator_keeps_everything
            dictator_keeps_2 = C.dictator_keeps_3quarters
            dictator_keeps_3 = C.dictator_keeps_half

        image = image.replace("2PP", "2PP_2")

        #print('TPPAGE Generating image path and round number - 1', image, player.round_number - 1)

        result = dict(
            TP_decisions=[
                dict(
                    index=1,
                    TP_decision=player.TP_decision1,
                    dictator_keeps=dictator_keeps_1,
                    receiver=C.total_endowment - dictator_keeps_1,
                    **({"pun_or_comp": player.punish_or_compensate1} if "comp" in player.treatment else {}),
                ),
                dict(
                    index=2,
                    TP_decision=player.TP_decision2,
                    dictator_keeps=dictator_keeps_2,
                    receiver=C.total_endowment - dictator_keeps_2,
                    **({"pun_or_comp": player.punish_or_compensate2} if "comp" in player.treatment else {}),
                ),
                dict(
                    index=3,
                    TP_decision=player.TP_decision3,
                    dictator_keeps=dictator_keeps_3,
                    receiver=C.total_endowment - dictator_keeps_3,
                    **({"pun_or_comp": player.punish_or_compensate3} if "comp" in player.treatment else {}),
                ),
            ],
            TP_norm_decisions=[
                dict(
                    index=1,
                    TP_norm_decision=player.TP_norm_decision1,
                    dictator_keeps=dictator_keeps_1,
                    receiver=C.total_endowment - dictator_keeps_1,
                ),
            ],
            TP_points=range(0, int(C.TP_points) + 1),
            treatment=player.treatment,
            dic_identity=dic_identity,
            recip_identity=recip_identity,
            dic_identity_country=dic_identity_country,
            recip_identity_country=recip_identity_country,
            treatment_text_action=text_action,
            treatment_text_action_person=text_action_person,
            treatment_text_receiver=text_receiver,
            image=image,
            role_switch_true=player.role_switch_true,
        )
        # Conditionally add the extra variable
        if "comp" in player.treatment:
            result["treatment_text_action_comp"] = text_action_comp
            result["treatment_text_action_person_comp"] = text_action_person_comp
            result["treatment_text_receiver_comp"] = text_receiver_comp

        return result

    def before_next_page(player: Player, timeout_happened):
        player.payoff = C.TP_points - player.TP_decision1


class DictatorPage(Page):

    @staticmethod
    def is_displayed(player: Player):
        return ("give" in player.treatment or "3PP DIC country" in player.treatment) #and "norm" not in player.treatment

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
        image = image.replace("2PP", "2PP_2")

        # 3PR trials get same image as 3PP
        if "3PR" in player.treatment:
            image = 'global/treatments/3PP give.png'
            dictator_keeps_1 = C.dictator_keeps_3quarters
            dictator_keeps_2 = C.dictator_keeps_half
        else:
            dictator_keeps_1 = C.dictator_keeps_everything
            dictator_keeps_2 = C.dictator_keeps_3quarters

        # For baseline trials, add condition text for "Keep in mind" text
        if "2PP" in player.treatment:
            text_action = "Person B can remove points from you"
        elif "3PP" in player.treatment:
            text_action = "Person C can remove points from you"
        elif "3PR" in player.treatment:
            text_action = "Person C can give points to you"
        elif "3PC" in player.treatment:
            text_action = "Person C can remove points from you or give points to Person B"
        else:
            text_action = "TEST"

        # For INOUT trials, check identity of recipient
        if player.treatment[-3:] == "OUT":
            recip_identity = "out"
            dic_identity = C.CURRENT_COUNTRY  # In give trials, participant is the dicatator --> identity of dictator is current country
            recip_identity_country = "one of 40 countries"
            dic_identity_country = C.CURRENT_COUNTRYNAME
        if player.treatment[-3:] == " IN":
            recip_identity = C.CURRENT_COUNTRY
            dic_identity = C.CURRENT_COUNTRY
            recip_identity_country = C.CURRENT_COUNTRYNAME
            dic_identity_country = C.CURRENT_COUNTRYNAME
        if "OUT" not in player.treatment and "IN" not in player.treatment:
            dic_identity = "baseline"
            recip_identity = "baseline"
            recip_identity_country = "baseline"
            dic_identity_country = "baseline"

        # For partner country trials, extract countries of recipient (dictator is participant from current country
        if "3PP DIC country" in player.treatment:
            dic_identity = C.CURRENT_COUNTRY
            recip_identity = player.treatment.replace(" 3PP DIC country", "")
            dic_identity_country = C.CURRENT_COUNTRYNAME
            recip_identity_country = C.COUNTRIES.get(recip_identity)
            image = 'global/treatments/3PP give.png'

        # print('Generating image path and round number - 1', image, player.round_number - 1)

        return dict(
            dic_norm_decisions=[ # keep the dict for now in case we decide we need more than 1
                dict(
                    index=1,
                    dic_norm_decision=player.dic_norm_decision1,
                    dictator_keeps=dictator_keeps_1,
                    receiver_gets=int(C.total_endowment - dictator_keeps_1),
                ),
            ],
            treatment=player.treatment,
            endowments=range(0, int(C.total_endowment) + 1),
            dic_identity=dic_identity,
            recip_identity=recip_identity,
            dic_identity_country=dic_identity_country,
            recip_identity_country=recip_identity_country,
            dic_decision1=player.dic_decision1,
            image=image,
            treatment_text_action=text_action,
            role_switch_true = player.role_switch_true,
            )

    def before_next_page(player: Player, timeout_happened):
        player.payoff = C.total_endowment - player.dic_decision1



class UniversalNormPage(Page):

    @staticmethod
    def is_displayed(player: Player):
        return "universal norm" in player.treatment

    form_model = 'player'

    def get_form_fields(player: Player):
        return ['universal_norm_decision1', 'universal_norm_decision2']

    @staticmethod
    def vars_for_template(player: Player):
        image = 'global/treatments/0DG give.png'
        dictator_keeps_1 = C.dictator_keeps_everything
        recorded_norm_num = max([p.dic_norm_decision1 for p in player.in_rounds(1, 2)])
        norm_ratings = ['very socially unacceptable', 'socially unacceptable', 'slightly socially unacceptable', 'slightly socially acceptable', 'socially acceptable', 'very socially acceptable']
        recorded_norm = norm_ratings[recorded_norm_num]

        #print('univnormpage Generating image path and round number - 1', image, player.round_number - 1)

        return dict(
            universal_norm_decisions=[ # keep the dict for now in case we decide we need more than 1
                dict(
                    index=1,
                    universal_norm_decision=player.universal_norm_decision1,
                    dictator_keeps=dictator_keeps_1,
                    receiver_gets=int(C.total_endowment - dictator_keeps_1),
                ),
            ],
            treatment=player.treatment,
            endowments=range(0, int(C.total_endowment) + 1),
            universal_norm_decision1=player.universal_norm_decision1,
            universal_norm_decision2=player.universal_norm_decision2,
            image=image,
            recorded_norm_num=recorded_norm_num,
            recorded_norm=recorded_norm,
            )


class Results(Page):
    pass



page_sequence = [Consent,
                 Introduction,
                 instructionPage,
                 UniversalNormPage,
                 DictatorPage,
                 TPPage
                 ]
