from otree.api import *

import random
import logging
import csv
import os

from otree.models import player
from itertools import chain
from translations import get_translation


doc = """
Your app description
"""

def get_country_dict(lang, iso2=None):
    with open('_static/global/country_codes_Toluna_lang.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        if lang not in reader.fieldnames:
            raise ValueError(f"Language '{lang}' not found in CSV columns: {reader.fieldnames}")

        country_dict = {
            row["iso2"]: row[lang]
            for row in reader
            if row.get("iso2") and row.get(lang)
        }

    if iso2:
        return country_dict.get(iso2)
    return country_dict




class C(BaseConstants):
    NAME_IN_URL = 'baseline_trials'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 36
    NUM_DECISIONS_APPROX = 43
    STUDY_TIME = 30
    prolific = False

    COUNTRIES = get_country_dict('en')
    COUNTRY_LIST = list(COUNTRIES.keys())
    NUM_COUNTRIES = len(COUNTRY_LIST)


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
    ratings_extra_points = 8 # extra bonus for (norm) ratings close to country average
    attention_check_rounds = [7, 26]

    ### Treatments ###

    ## 1) Baseline (13 trials)
    trials_DG = ['0DG give', '0DG give norm']
    trials_3PP_DIC = ['3PP give']
    trials_3PP_TP = ['3PP punish', '3PP punish norm']
    trials_2PP_DIC = ['2PP give']
    trials_2PP_TP = ['2PP punish', '2PP punish norm']

    ## 2) Ingroup - outgroup (14 trials)
    trials_3PP_INOUT_DIC = ['3PP give IN', '3PP give OUT']
    trials_3PP_INOUT_TP = ['3PP punish IN OUT', '3PP punish OUT IN', '3PP punish OUT OUT']

    ## 3) Country - partner (26 trials: 5 * 5 + 1 universal norm)
    # Define number of trials for each trial type
    number_trials_partner_dic_out = 1 # just used so as to not deceive
    number_trials_partner_in_out = 5
    number_trials_partner_out_in = 5
    number_trials_partner_out_out_homog = 5
    number_trials_partner_out_out_heterog = 5

class Subsession(BaseSubsession):
    pass

def creating_session(subsession):
    # print('Creating session; round number: {}'.format(subsession.round_number))

    ## Set variables in participant field
    for player in subsession.get_players():
        participant = player.participant

        # PROBLEM: creating_session runs before any participants go through any pages, so no access to language selected
        # SOLUTION: Set countryname in native language later

        # Set language to English if English is the only offered language in that country (in this case participants do not see language selection pages)
        if 'language' not in participant.vars:
            participant.language = 'en'

        # Save current country code once for easier access in trial prep
        current_country = participant.current_country

        # progress bar
        participant.progress = 1

    ## Make immutable variables for partner-country block

    # Make country list without current country
    country_list_no_current = [entry for entry in C.COUNTRY_LIST if entry != current_country]

    # Make all possible combinations
    combinations = [(x, y) for x in C.COUNTRY_LIST for y in C.COUNTRY_LIST]

    # Get IN-IN trial
    trials_partner_in_in = [entry + ('IN IN',) for entry in combinations if entry[0] == entry[1] == current_country]
    #trials_partner_in_in = [entry for entry in combinations if entry[0] == entry[1] == current_country]


    # Remove IN-IN trials, which every participant sees only once
    combinations = [entry for entry in combinations if not entry[0] == entry[1] == current_country]

    # Filter different trial types
    trials_partner_in_out = [entry for entry in combinations if entry[0] == current_country]
    trials_partner_out_in = [entry for entry in combinations if entry[1] == current_country]
    trials_partner_out_out_homog = [entry for entry in combinations if
                                    (entry[0] != current_country and entry[1] != current_country and entry[0] ==
                                     entry[1])]
    trials_partner_out_out_heterog = [entry for entry in combinations if
                                      (entry[0] != current_country and entry[1] != current_country and entry[0] !=
                                       entry[1])]


    # Duplicate original pools of trial types for removing used trials (and later refilling pools once empty)
    country_list_no_current_editable = country_list_no_current.copy()
    country_list_no_current_editable = [item + " 3PP give country" for item in country_list_no_current_editable]
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

            trials_DG_current = random.sample(C.trials_DG, len(C.trials_DG)) # Randomize the order of give, punish, norm per treatment type (DG, 3PP, 2PP)
            # First randomize the TP trials
            trials_3PP_TP_current = random.sample(C.trials_3PP_TP, len(C.trials_3PP_TP))
            trials_2PP_TP_current = random.sample(C.trials_2PP_TP, len(C.trials_2PP_TP))
            # Second, add DIC trial either before or after
            trials_3PP_current = trials_3PP_TP_current + C.trials_3PP_DIC if random.choice([True, False]) else C.trials_3PP_DIC + trials_3PP_TP_current
            trials_2PP_current = trials_2PP_TP_current + C.trials_2PP_DIC if random.choice([True, False]) else C.trials_2PP_DIC + trials_2PP_TP_current
            # FIXED ORDER: DG, 2PP, 3PP
            participant.treatment_order_baseline = trials_DG_current + trials_2PP_current + trials_3PP_current


            ### 2) Country partners (including unknown)

            ## a) Dictator role

            trials_partner_dic_out_current, country_list_no_current_editable = sample_trials_partner(country_list_no_current_editable, C.number_trials_partner_dic_out, "country_list_no_current")

            # Add unknown country trials and randomize order
            trials_partner_dic = trials_partner_dic_out_current + C.trials_3PP_INOUT_DIC
            random.shuffle(trials_partner_dic)

            ## b) Punisher role

            trials_partner_in_out_current, trials_partner_in_out_editable = sample_trials_partner(trials_partner_in_out_editable, C.number_trials_partner_in_out, "trials_partner_in_out")
            trials_partner_out_in_current, trials_partner_out_in_editable = sample_trials_partner(trials_partner_out_in_editable, C.number_trials_partner_out_in, "trials_partner_out_in")
            trials_partner_out_out_homog_current, trials_partner_out_out_homog_editable = sample_trials_partner(trials_partner_out_out_homog_editable, C.number_trials_partner_out_out_homog, "trials_partner_out_out_homog")
            trials_partner_out_out_heterog_current, trials_partner_out_out_heterog_editable = sample_trials_partner(trials_partner_out_out_heterog_editable, C.number_trials_partner_out_out_heterog, "trials_partner_out_out_heterog")

            # Add unknown country trials and randomize order
            trials_partner_in_out = trials_partner_in_out_current + [C.trials_3PP_INOUT_TP[0]]
            trials_partner_out_in = trials_partner_out_in_current + [C.trials_3PP_INOUT_TP[1]]
            # OUT-OUT unknown can go either together with out-out homog or out-out heterog
            if random.choice([True, False]):
                trials_partner_out_out_homog = trials_partner_out_out_homog_current + [C.trials_3PP_INOUT_TP[2]]
                trials_partner_out_out_heterog = trials_partner_out_out_heterog_current
            else:
                trials_partner_out_out_heterog = trials_partner_out_out_heterog_current + [C.trials_3PP_INOUT_TP[2]]
                trials_partner_out_out_homog = trials_partner_out_out_homog_current

            random.shuffle(trials_partner_in_out)
            random.shuffle(trials_partner_out_in)
            random.shuffle(trials_partner_out_out_homog)
            random.shuffle(trials_partner_out_out_heterog)


            ## c) Merge and randomize order of trials within punisher role # UPDATE: Shuffle order of treatments, but not across treatments
            trials_partner_TP_current = [trials_partner_in_in, trials_partner_in_out, trials_partner_out_in, trials_partner_out_out_homog, trials_partner_out_out_heterog]

            # Shuffle the merged list
            random.shuffle(trials_partner_TP_current)

            # Flatten list
            trials_partner_TP_current = [item for sublist in trials_partner_TP_current for item in sublist]  # Flatten the nested lists

            # Add 3PP treatment identifier for referring to treatment and flatten list (tuples produce errors)
            trials_partner_TP_current = [
                " ".join(tup) + " 3PP country" if isinstance(tup, tuple) else tup
                for tup in trials_partner_TP_current
            ]

            ## d) Randomize order of DIC/TP
            treatment_order_partner_no_univ_norm = trials_partner_TP_current + trials_partner_dic if random.choice(
                [True, False]) else trials_partner_dic + trials_partner_TP_current

            ## e) Place universal norm always at the end of block
            trials_partner_universal_norm = ['universal norm']
            participant.treatment_order_partner = treatment_order_partner_no_univ_norm + trials_partner_universal_norm

            ### 4) Put all treatment orders together
            participant.treatment_order = participant.treatment_order_baseline + participant.treatment_order_partner
            #print('set treatment_order to', participant.treatment_order)


            ### 5) Put instruction round and comprehension questions
            # Instructions before trials from new treatment type
            participant.instruction_round = [trials_DG_current[0], trials_3PP_current[0], trials_2PP_current[0],
                                             participant.treatment_order[len(participant.treatment_order_baseline)]]
            # Comprehension questions before first 2PP punishment trial
            round_2PP_or_3PP = next(v for v in participant.treatment_order if "2PP" in v or "3PP" in v)  # Find the first element containing "2PP" or "3PP"
            participant.comprehension = [round_2PP_or_3PP]

    #breakpoint()

    for player in subsession.get_players():
        #player.treatment = player.participant.treatment_order_baseline[player.round_number - 1] # For testing only baseline
        player.treatment = player.participant.treatment_order[player.round_number - 1]
        player.instruction_round_true = player.treatment in player.participant.instruction_round # Boolean that indicates if instruction page should be shown: Always before the first trial of a new treatment type
        player.comprehension_true = player.treatment in player.participant.comprehension
        player.first_block_2PP_true = "2PP" in player.participant.treatment_order[2]  # Boolean that indicates if instruction page should be shown: Always before the first trial of a new treatment type


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    treatment = models.StringField()
    instruction_round_true = models.BooleanField()
    comprehension_true = models.BooleanField()
    first_block_2PP_true = models.BooleanField()
    comp_failed2PP = models.IntegerField()#initial=0)
    att_failed1 = models.IntegerField(initial=0)
    att_failed2 = models.IntegerField(initial=0)

    # Decisions
    dic_decision1 = models.IntegerField(
        initial=999,
        choices=[(i, f'value {i}') for i in range(C.total_endowment + 1)],  # Dynamically generate choices
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, #does not display
    )

    dic_norm_decision1 = models.IntegerField(
        initial=999,
        choices=[(i, f'value {i}') for i in range(C.total_endowment + 1)],
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )

    TP_decision1 = models.IntegerField(
        initial=999,
        choices=[(i, f'value {i}') for i in range(C.total_endowment + 1)],
        widget=widgets.RadioSelect,
    )
    TP_decision2 = models.IntegerField(
        initial=999,
        choices=[(i, f'value {i}') for i in range(C.total_endowment + 1)],
        widget=widgets.RadioSelect,
    )
    TP_decision3 = models.IntegerField(
        initial=999,
        choices=[(i, f'value {i}') for i in range(C.total_endowment + 1)],
        widget=widgets.RadioSelect,
    )

    TP_norm_decision1 = models.IntegerField(
        initial=999,
        choices=[
            [0, f'value 0'], [1, f'value 1'], [2, f'value 2'], [3, f'value 3'], [4, f'value 4'], [5, f'value 5'],
        ],
        widget=widgets.RadioSelect,
    )
    TP_neg_norm_decision1 = models.IntegerField(
        initial=999,
        choices=[
            [0, f'value 0'], [1, f'value 1'], [2, f'value 2'], [3, f'value 3'], [4, f'value 4'], [5, f'value 5'],
        ],
        widget=widgets.RadioSelect,
    )
    slider1 = models.IntegerField(
        min=0, max=50000
    )
    comprehension2PP = models.IntegerField(
        initial=999,
        choices=[
            [0, f'value 0'], [1, f'value 1'], [2, f'value 2'], [3, f'value 3'],
        ],
        widget=widgets.RadioSelect,
    )
    attention1 = models.IntegerField(
        initial=0,
        choices=[
            [0, f'value 0'], [1, f'value 1'], [2, f'value 2'], [3, f'value 3'],
        ],
        widget=widgets.RadioSelect,
    )
    attention2 = models.IntegerField(
        initial=0,
        choices=[
            [0, f'value 0'], [1, f'value 1'], [2, f'value 2'], [3, f'value 3'],
        ],
        widget=widgets.RadioSelect,
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
        participant = player.participant
        lang = participant.language

        return dict(
            consent_title=get_translation('consent_title', lang),
            consent_thank_you=get_translation('consent_thank_you', lang),
            consent_intro_title=get_translation('consent_intro_title', lang),
            consent_intro=get_translation('consent_intro', lang,
                                          decisions_approx=C.NUM_DECISIONS_APPROX,
                                          time=C.STUDY_TIME),
            consent_payment_title=get_translation('consent_payment_title', lang),
            consent_payment_prolific=get_translation('consent_payment_prolific', lang,
                                            participation_fee=player.session.config['participation_fee']),
            consent_payment_toluna=get_translation('consent_payment_toluna', lang,
                                            participation_fee=player.session.config['participation_fee']),
            consent_rights_title= get_translation('consent_rights_title', lang),
            consent_rights=get_translation('consent_rights', lang),
            consent_click=get_translation('consent_click', lang),
            consent_questions=get_translation('consent_questions', lang),
            consent_contact=get_translation('consent_contact', lang),
            button_consent=get_translation('button_consent', lang),
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 1


class Introduction(Page):

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == 1:
            return True
        else:
            return False

    def vars_for_template(player: Player):
        participant = player.participant
        lang = participant.language
        return dict(
            total_pages=player.session.config['total_pages'],
            intro_title=get_translation('intro_title', lang),
            intro_pairing=get_translation('intro_pairing', lang),
            intro_toluna=get_translation('intro_toluna', lang),
            intro_pairing_prolific=get_translation('intro_pairing', lang),
            intro_prolific=get_translation('intro_prolific', lang),
            intro_conversion=get_translation('intro_conversion', lang,
                                             conversion=player.session.config['real_world_currency_per_point']),
            intro_block1_title=get_translation('block_title', lang, block_num=1),
            intro_block1=get_translation('intro_block1', lang),
            intro_block2_title=get_translation('block_title', lang, block_num=2),
            intro_block2=get_translation('intro_block2', lang),
            intro_points_title=get_translation('intro_points_title', lang),
            intro_points=get_translation('intro_points', lang),
            intro_carefully=get_translation('intro_carefully', lang),
            button_start=get_translation('button_start', lang),
        )


class Instructions(Page):
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

        participant = player.participant
        lang = participant.language

        # Load countrynames in selected language
        participant.current_countryname = get_country_dict(lang, participant.current_country)

        if "IN" in player.treatment or "OUT" in player.treatment or "country" in player.treatment or "universal norm" in player.treatment:
            random_partner_country_IN_as_dic = random.choice([True, False])
            random_partner = random.choice(C.COUNTRY_LIST)
            if random_partner_country_IN_as_dic:
                dic_identity = participant.current_country
                recip_identity = random_partner
                dic_identity_country = participant.current_countryname
                recip_identity_country = get_country_dict(lang,random_partner)
            else:
                dic_identity = random_partner
                recip_identity = participant.current_country
                dic_identity_country = get_country_dict(lang,random_partner)
                recip_identity_country = participant.current_countryname
        else:
            dic_identity = "baseline"
            recip_identity = "baseline"
            recip_identity_country = "baseline"
            dic_identity_country = "baseline"

        treatment_type = player.treatment[:3] # Extract the first three characters as treatment type
        first_block_2PP_true = player.first_block_2PP_true
        #block2 = "OUT" in player.treatment or "IN" in player.treatment
        #block3 = "country" in player.treatment or "universal norm" in player.treatment
        block3 = ("country" in player.treatment) or ("universal norm" in player.treatment) or ("OUT" in player.treatment) or ("IN" in player.treatment)
        #print('instructionPage Generating image path and round number - 1', image, player.round_number - 1, player.treatment)

        return dict(
            total_pages=player.session.config['total_pages'],
            treatment=player.treatment,
            cost_per_point=round(1 / C.TP_cost, 2),
            image=image,
            random_trial_numbers=random_trial_numbers,
            random_trial_numbers_diff=random_trial_numbers_diff,
            dic_identity=dic_identity,
            recip_identity= recip_identity,
            dic_identity_country= dic_identity_country,
            recip_identity_country= recip_identity_country,
            first_block_2PP_true = first_block_2PP_true,
            #block2 = block2,
            block3 = block3,
            current_country = participant.current_countryname,
            treatment_type = treatment_type,
            instructions_title=get_translation('instructions_title', lang),
            instru_part1=get_translation('instru_part', lang, part_num=1),
            instru_part2=get_translation('instru_part', lang, part_num=2),
            instru_part3=get_translation('instru_part', lang, part_num=3),
            instru_part4=get_translation('instru_part', lang, part_num=4),
            instru_part5=get_translation('instru_part', lang, part_num=5),
            error1=get_translation('error1', lang),
            you=get_translation('you', lang),
            button_next=get_translation('button_next', lang),
            button_decision=get_translation('button_decision', lang),
            button_block=get_translation('button_block', lang),

            instru_0DG_pairing=get_translation('instru_0DG_pairing', lang),
            instru_0DG_decision=get_translation('instru_0DG_decision', lang),
            instru_0DG_points=get_translation('instru_0DG_points', lang),
            instru_0DG_rules=get_translation('instru_0DG_rules', lang),
            instru_2PP_stages=get_translation('instru_2PP_stages', lang),
            instru_2PP_points=get_translation('instru_2PP_points', lang),
            instru_2PP_stage2=get_translation('instru_2PP_stage2', lang),
            instru_2PP_remove=get_translation('instru_2PP_remove', lang,
                                              cost_per_point=round(1/C.TP_cost, 2)),
            instru_2PP_role=get_translation('instru_2PP_role', lang),
            instru_3PP_change=get_translation('instru_3PP_change', lang),
            instru_3PP_personc=get_translation('instru_3PP_personc', lang),
            instru_3PP_remove=get_translation('instru_3PP_remove', lang),
            instru_3PP_rules=get_translation('instru_3PP_rules', lang,
                                              cost_per_point=round(1/C.TP_cost, 2)),
            instru_INOUT=get_translation('instru_INOUT', lang,
                                         current_country=participant.current_countryname,
                                         number_countries=C.NUM_COUNTRIES,),
            instru_countries_list=get_translation('instru_countries_list', lang),
            instru_countries=get_translation('instru_countries', lang),
            instru_countries_here=get_translation('instru_countries_here', lang),
            instru_countries_example=get_translation('instru_countries_example', lang,
                                                     dic_identity_country=dic_identity_country,
                                                     recip_identity_country=recip_identity_country,),
            instru_countries_personc=get_translation('instru_countries_personc', lang),
            instru_countries_remove=get_translation('instru_countries_remove', lang),
            person_a=get_translation('person_a', lang),
            person_b=get_translation('person_b', lang),
            person_c=get_translation('person_c', lang),
            button_understood=get_translation('button_understood', lang),
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 3


class ComprehensionQuestionPage(Page):
    @staticmethod
    def is_displayed(player: Player):
        # return player.round_number == 1
        return player.instruction_round_true and player.comprehension_true

    form_model = 'player'

    def get_form_fields(player: Player):
        if "2PP" in player.treatment:
            return ['comprehension2PP', 'comp_failed2PP']

    @staticmethod
    def error_message(player: Player, values):
        """
        records the number of time the page was submitted with an error. which specific error is not recorded.
        """

        if "2PP" in player.treatment:
            solutions = dict(comprehension2PP=2)

        errors = {f: 'Error' for f in solutions if values[f] != solutions[f]}
        if errors:
            return errors

    @staticmethod
    def vars_for_template(player: Player):
        image = 'global/treatments/{}.png'.format(player.treatment)
        image = image.replace(" norm", "")
        image = image.replace("2PP", "2PP_2")
        image = image.replace("3PR reward", "3PP punish")
        correct_answers = [2, 3, 1]

        participant = player.participant
        lang = participant.language
        return dict(
            treatment=player.treatment,
            page_name=ComprehensionQuestionPage,
            comprehension2PP=player.comprehension2PP,
            image=image,
            correct_answers=correct_answers,
            total_pages=player.session.config['total_pages'],
            comprehension_title=get_translation('comprehension_title', lang),
            comprehension_error_green=get_translation('attention_error_green', lang),
            comprehension_error_red=get_translation('attention_error_red', lang),
            comprehension_2PP=get_translation('comprehension_2PP', lang),
            comprehension_2PP_answer0=get_translation('comprehension_2PP_answer0', lang,
                                                      points1=3,
                                                      points2=round(1/C.TP_cost, 2)),
            comprehension_2PP_answer1=get_translation('comprehension_2PP_answer0', lang,
                                                      points1=3,
                                                      points2=1),
            comprehension_2PP_answer2=get_translation('comprehension_2PP_answer0', lang,
                                                      points1=1,
                                                      points2=round(1 / C.TP_cost, 2)),
            comprehension_2PP_answer3=get_translation('comprehension_2PP_answer0', lang,
                                                      points1=1,
                                                      points2=1),
            button_next=get_translation('button_next', lang),
            error_incorrect=get_translation('error_incorrect', lang),
            button_decision=get_translation('button_decision', lang),
            button_block=get_translation('button_block', lang),
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 2


class AttentionCheckPage(Page):
    @staticmethod
    def is_displayed(player: Player):
        # return player.round_number == 1
        return player.round_number == C.attention_check_rounds[0] or player.round_number == C.attention_check_rounds[1]

    form_model = 'player'

    def get_form_fields(player: Player):
        if player.round_number == C.attention_check_rounds[0]:
            return ['attention1', 'att_failed1']
        else:
            return ['attention2', 'att_failed2']

    @staticmethod
    def vars_for_template(player: Player):
        image = 'global/treatments/{}.png'.format(player.treatment)
        image = image.replace(" norm", "")
        image = image.replace("2PP", "2PP_2")
        image = image.replace("3PR reward", "3PP punish")
        correct_answers = [2, 1]
        attention_round1 = C.attention_check_rounds[0]

        participant = player.participant
        lang = participant.language

        return dict(
            treatment=player.treatment,
            page_name=AttentionCheckPage,
            image=image,
            correct_answers=correct_answers,
            attention_round1=attention_round1,
            attention1=player.attention1,
            attention2=player.attention2,
            button_next=get_translation('button_next', lang),
            button_decision=get_translation('button_decision', lang),
            button_block=get_translation('button_block', lang),
            error1=get_translation('error1', lang),
            person_a=get_translation('person_a', lang),
            person_b=get_translation('person_b', lang),
            person_c=get_translation('person_c', lang),
            attention_error_green=get_translation('attention_error_green', lang),
            attention_error_red=get_translation('attention_error_red', lang),
            attention_check1=get_translation('attention_check1', lang,
                                                 attention_num=4),
            attention_0points=get_translation('points_button', lang,
                                                 num_points=0),
            attention_2points=get_translation('points_button', lang,
                                                 num_points=2),
            attention_4points=get_translation('points_button', lang,
                                                 num_points=4),
            attention_6points=get_translation('points_button', lang,
                                                 num_points=6),
            attention_check2=get_translation('attention_check1', lang,
                                                 attention_num=2),
            attention_title=get_translation('attention_title', lang),
            total_pages=player.session.config['total_pages'],
        )

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 3


class TPPage(Page):

    @staticmethod
    def is_displayed(player: Player):
        return "punish" in player.treatment or "3PP country" in player.treatment
    form_model = 'player'

    def get_form_fields(player: Player):
        if "norm" in player.treatment:
            if "punish" in player.treatment:
                return ['TP_norm_decision1', 'TP_neg_norm_decision1']
            else:
                return ['TP_norm_decision1']
        else:
            return ['TP_decision1', 'TP_decision2', 'TP_decision3']


    @staticmethod
    def vars_for_template(player: Player):
        participant = player.participant
        lang = participant.language

        if "2PP punish" in player.treatment:
            person = get_translation('person_b_lower', lang)
            #person2 = get_translation('you_lower', lang)
            image = 'global/treatments/2PP punish.png'
            ## dictator_keeps is assigned here so that we can have different multiple decisions per treatment.
            ## at the moment they are all the same so it is redundant (could be done straight in the dict).
            ## but like this we can switch easily
            dictator_keeps_1 = C.dictator_keeps_everything
            dictator_keeps_2 = C.dictator_keeps_3quarters
            dictator_keeps_3 = C.dictator_keeps_half
        if "3PP punish" in player.treatment or "3PP country" in player.treatment:
            person = get_translation('person_c_lower', lang)
            #person2 = get_translation('person_b_lower', lang)
            image = 'global/treatments/3PP punish.png'
            dictator_keeps_1 = C.dictator_keeps_everything
            dictator_keeps_2 = C.dictator_keeps_3quarters
            dictator_keeps_3 = C.dictator_keeps_half

        # For unknown country trials, check identity of dictator and recipient
        if "IN IN" in player.treatment:
            dic_identity = participant.current_country
            recip_identity = participant.current_country
            dic_identity_country = participant.current_countryname
            recip_identity_country = participant.current_countryname
        if "IN OUT" in player.treatment:
            dic_identity = participant.current_country
            recip_identity = "out"
            dic_identity_country = participant.current_countryname
            recip_identity_country = get_translation('unknown_country', lang, num_countries=C.NUM_COUNTRIES)
        if "OUT IN" in player.treatment:
            dic_identity = "out"
            recip_identity = participant.current_country
            dic_identity_country = get_translation('unknown_country', lang, num_countries=C.NUM_COUNTRIES)
            recip_identity_country = participant.current_countryname
        if "OUT OUT" in player.treatment:
            dic_identity = "out"
            recip_identity = "out"
            dic_identity_country = get_translation('unknown_country', lang, num_countries=C.NUM_COUNTRIES)
            recip_identity_country = get_translation('unknown_country', lang, num_countries=C.NUM_COUNTRIES)
        if "OUT" not in player.treatment and "IN" not in player.treatment:
            dic_identity = "baseline"
            recip_identity = "baseline"
            recip_identity_country = "baseline"
            dic_identity_country = "baseline"

        # For (known) partner country trials, extract countries of dictator and recipient
        if "3PP country" in player.treatment:
            dic_identity = player.treatment[:2]
            recip_identity = player.treatment[3:5]
            dic_identity_country = get_country_dict(lang,dic_identity)
            recip_identity_country = get_country_dict(lang,recip_identity)
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
                    #TP_neg_norm_decision=player.TP_neg_norm_decision1,
                    **({"TP_neg_norm_decision": player.TP_neg_norm_decision1} if "reward" or "punish" in player.treatment else {}),
                    dictator_keeps=dictator_keeps_1,
                    receiver=C.total_endowment - dictator_keeps_1,
                ),
            ],
            TP_points=range(0, int(C.TP_points) + 1),
            treatment=player.treatment,
            page_name=TPPage,
            dic_identity=dic_identity,
            recip_identity=recip_identity,
            dic_identity_country=dic_identity_country,
            recip_identity_country=recip_identity_country,
            image=image,
            current_country=participant.current_countryname,
            button_decision=get_translation('button_decision', lang),
            person_a=get_translation('person_a', lang),
            person_b=get_translation('person_b', lang),
            person_c=get_translation('person_c', lang),
            you=get_translation('you', lang),
            person=person,
            #person2=person2,
            tpp_2PP_norm_instru=get_translation('norm_instru', lang,
                                                   person=person),
            tpp_2PP_norm_incentive=get_translation('dict_norm_incentive', lang,
                                                   ratings_extra_points=C.ratings_extra_points,
                                                   current_country=participant.current_countryname),
            tpp_3PP_norm_instru=get_translation('norm_instru', lang,
                                                   person=get_translation('person_c_lower', lang)),
            tpp_dict_action=get_translation('tpp_dict_action', lang),
            tpp_norm_question=get_translation('tpp_norm_question', lang,
                                              person=person),
            tpp_norm_neg_question=get_translation('tpp_norm_neg_question', lang,
                                                  person=person),
            tpp_decision_strategy=get_translation('tpp_decision_strategy', lang),
            tpp_decision_you=get_translation('tpp_decision_you', lang,
                                             person=person),
            tpp_decision_question=get_translation('tpp_decision_question', lang,
                                                  person=person),
            tpp_decision_cost=get_translation('tpp_decision_cost', lang),
            tpp_countries=get_translation('decision_countries_origin', lang,
                                                 dic_identity_country=dic_identity_country,
                                                 recip_identity_country=recip_identity_country),
            very_inappropriate=get_translation('very_inappropriate', lang),
            inappropriate=get_translation('inappropriate', lang),
            slightly_inappropriate=get_translation('slightly_inappropriate', lang),
            slightly_appropriate=get_translation('slightly_appropriate', lang),
            appropriate=get_translation('appropriate', lang),
            very_appropriate=get_translation('very_appropriate', lang),
            button_next=get_translation('button_next', lang),
            button_block=get_translation('button_block', lang),
            error3=get_translation('error3', lang),
            total_pages=player.session.config['total_pages'],
        )

        return result

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 8


class DictatorPage(Page):

    @staticmethod
    def is_displayed(player: Player):
        return "give" in player.treatment

    form_model = 'player'

    def get_form_fields(player: Player):
        if "norm" in player.treatment:
            return ['dic_norm_decision1']
        else:
            return ['dic_decision1']

    @staticmethod
    def vars_for_template(player: Player):
        participant = player.participant
        lang = participant.language

        image = 'global/treatments/{}.png'.format(player.treatment)
        image = image.replace(" IN", "")
        image = image.replace(" OUT", "")
        image = image.replace(" norm", "")
        image = image.replace("2PP", "2PP_2")

        dictator_keeps_1 = C.dictator_keeps_everything
        dictator_keeps_2 = C.dictator_keeps_3quarters

        # For baseline trials, add condition text for "Keep in mind" text
        if "2PP" in player.treatment:
            person = get_translation('person_b_lower', lang)
        elif "3PP" in player.treatment:
            person = get_translation('person_c_lower', lang)
        else:
            person = "TEST"

        # For INOUT trials, check identity of recipient
        if player.treatment[-3:] == "OUT":
            recip_identity = "out"
            dic_identity = participant.current_country  # In give trials, participant is the dictator --> identity of dictator is current country
            recip_identity_country = get_translation('unknown_country', lang, num_countries=C.NUM_COUNTRIES)
            dic_identity_country = participant.current_countryname
        if player.treatment[-3:] == " IN":
            recip_identity = participant.current_country
            dic_identity = participant.current_country
            recip_identity_country = participant.current_countryname
            dic_identity_country = participant.current_countryname
        if "OUT" not in player.treatment and "IN" not in player.treatment:
            dic_identity = "baseline"
            recip_identity = "baseline"
            recip_identity_country = "baseline"
            dic_identity_country = "baseline"

        # For partner country trials, extract countries of recipient (dictator is participant from current country
        if "3PP give country" in player.treatment:
            dic_identity = participant.current_country
            recip_identity = player.treatment.replace(" 3PP give country", "")
            dic_identity_country = participant.current_countryname
            recip_identity_country = get_country_dict(lang,recip_identity)
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
            page_name=DictatorPage,
            endowments=range(0, int(C.total_endowment) + 1),
            dic_identity=dic_identity,
            recip_identity=recip_identity,
            dic_decision1=player.dic_decision1,
            image=image,
            button_decision=get_translation('button_decision', lang),
            dict_norm_instru=get_translation('norm_instru', lang,
                                             person = get_translation('person_a_lower', lang)),
            dict_norm_incentive=get_translation('dict_norm_incentive', lang,
                                                ratings_extra_points=C.ratings_extra_points,
                                                current_country=participant.current_countryname),
            dict_norm_summary=get_translation('dict_norm_summary', lang,
                                              total_endowment=C.total_endowment),
            dict_norm_question=get_translation('dict_norm_question', lang),
            very_inappropriate=get_translation('very_inappropriate', lang),
            inappropriate=get_translation('inappropriate', lang),
            slightly_inappropriate=get_translation('slightly_inappropriate', lang),
            slightly_appropriate=get_translation('slightly_appropriate', lang),
            appropriate=get_translation('appropriate', lang),
            very_appropriate=get_translation('very_appropriate', lang),
            dict_decision_endowment=get_translation('dict_decision_endowment', lang,
                                              total_endowment=C.total_endowment),
            dict_decision_countries=get_translation('decision_countries_origin_dic', lang,
                                                 dic_identity_country=dic_identity_country,
                                                 recip_identity_country=recip_identity_country),
            dict_decision_question=get_translation('dict_decision_question', lang),
            person = person,
            dict_decision_mind=get_translation('dict_decision_mind', lang,
                                               person=person),
            dict_decision_hover=get_translation('dict_decision_hover', lang),
            you=get_translation('you', lang),
            person_a=get_translation('person_a', lang),
            person_b=get_translation('person_b', lang),
            person_c=get_translation('person_c', lang),
            button_next=get_translation('button_next', lang),
            button_block=get_translation('button_block', lang),
            error1=get_translation('error1', lang),
            total_pages=player.session.config['total_pages'],
            )

    def before_next_page(player: Player, timeout_happened):
        player.payoff = C.total_endowment - player.dic_decision1
        participant = player.participant
        participant.progress += 8


class UniversalNormPage(Page):

    @staticmethod
    def is_displayed(player: Player):
        return "universal norm" in player.treatment

    form_model = 'player'

    def get_form_fields(player: Player):
        return ['slider1']

    @staticmethod
    def vars_for_template(player: Player):
        image = 'global/treatments/0DG give.png'
        dictator_keeps_1 = C.dictator_keeps_everything
        receiver_gets = C.total_endowment - dictator_keeps_1

        participant = player.participant
        lang = participant.language

        return dict(
            treatment=player.treatment,

            univ_norm_instru= get_translation('univ_norm_instru', lang, dictator_keeps_1 = dictator_keeps_1, receiver_gets = receiver_gets, num_people_asked=50000),
            univ_norm_question= get_translation('univ_norm_question', lang, receiver_gets = receiver_gets),
            univ_norm_incentive = get_translation('block2_norm_incentive', lang,
                                                 ratings_extra_points=C.ratings_extra_points),
            error_1slider=get_translation('error_1slider', lang),
            person_a =get_translation('person_a', lang),
            person_b =get_translation('person_b', lang),
            button_next = get_translation('button_next', lang),
            button_decision=get_translation('button_decision', lang),
            button_block=get_translation('button_block', lang),
            num_countries=list(range(0, C.NUM_COUNTRIES+1)),
            endowments=range(0, int(C.total_endowment) + 1),
            image=image,
            total_pages=player.session.config['total_pages'],
            )

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 1
        # record the last Decision title number and adds 1 ready for the next app title
        participant.decision_page_number = player.round_number +1


page_sequence = [Consent,
                 Introduction,
                 AttentionCheckPage,
                 Instructions,
                 ComprehensionQuestionPage,
                 DictatorPage,
                 TPPage,
                 UniversalNormPage
                 ]
