from otree.api import *

import random
import itertools
import csv
import os

from translations import get_translation

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'crowding_out'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass



def creating_session(subsession): # Just for testing treatment allocation, will eventually me moved to create-session in baseline trials
    # print('Creating session; round number: {}'.format(subsession.round_number))

    participants = subsession.session.get_participants()

    combinations = list(itertools.product([True, False], [True, False]))  # (incentive, cond_coop)

    num_participants = len(participants)
    full_list = combinations * (num_participants // 4)
    remainder = combinations[:(num_participants % 4)]
    treatment_list = full_list + remainder

    random.shuffle(treatment_list)

    for p, (incentive, cond_coop) in zip(participants, treatment_list):
        p.treatment_incentive = incentive
        #p.treatment_cond_coop = cond_coop

        print('set incentive treatment to', p.treatment_incentive)
        #print('set cond coop treatment to', p.treatment_cond_coop)

    for player in subsession.get_players():
        participant = player.participant

        # Only necessary if not using participant field from baseline_trials
        participant.current_country = "gb"
        participant.current_countryname = "the United Kingdom"

        # translation
        participant.language = 'en'
        
        participant.crowding_out_button_pos = random.choice([True, False])

        # ''' ONLY WHEN TESTING APP ON ITS OWN'''
        # participant.progress = 1
        # participant.decision_page_number = 0 # For testing only crowding
        #
        # print('set crowding_out_button_pos', participant.crowding_out_button_pos)


def get_local_red_cross_info(country_name):
    filepath = os.path.join(os.path.dirname(__file__), '../_static/global/country_codes_red_cross.csv')
    with open(filepath, encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["countryname"] == country_name:
                red_cross_local = row["red_cross_local"]
                iso2_code = row["iso2"]
                # Construct the image path
                # image_path = f"../_static/global/charities/local_red_cross/iso2_{iso2_code}_fitted.png"
                image_path = f"global/charities/local_red_cross/iso2_{iso2_code}.png"
                return red_cross_local, image_path
    return " ", "../_static/global/charities/unknown_charity.png"  # default if not found



class Group(BaseGroup):
    pass


class Player(BasePlayer):

    charity_select = models.StringField(
        # choices=["Unicef", "Red Cross", "Doctors Without Borders", "Save the Children", "other"],
        blank=True  # Optional: allow it to be empty if no donation is made
    )
    crowding_decision = models.IntegerField(
        initial=999,
        choices=[[0, f'keep'], [4, f'give'], ],
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )
    # crowding_norm_decision1 = models.IntegerField(
    #     initial=0,
    #     choices=[(i, f'value {i}') for i in range(12 + 1)],
    #     widget=widgets.RadioSelect,
    #     # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    # )
    # crowding_norm_decision2 = models.IntegerField(
    #     initial=0,
    #     choices=[(i, f'value {i}') for i in range(12 + 1)],
    #     widget=widgets.RadioSelect,
    #     # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    # )
    crowding_norm_decision1 = models.IntegerField(
        min=0,
        max=100,
        blank=True
    )
    crowding_norm_decision2 = models.IntegerField(
        min=0,
        max=100,
        blank=True
    )
    slider1 = models.IntegerField(
        min=0, max=100
    )

    slider2 = models.IntegerField(
        min=0, max=100
    )

    slider3 = models.IntegerField(
        min=0, max=100
    )
    descr_norm = models.IntegerField(
        initial=999,
        choices=[(i, f'value {i}') for i in range(101)],
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )
    cond_coop = models.IntegerField(
        initial=999,
        choices=[(i, f'value {i}') for i in range(1000)],
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )
    # cond_coop_control = models.IntegerField(
    #     initial=999,
    #     choices=[(i, f'value {i}') for i in range(1000)],
    #     widget=widgets.RadioSelect,
    #     # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    # )


# PAGES
class CrowdingInOutPage(Page):

    # @staticmethod
    # def is_displayed(player: Player):
    #     return "give" in player.treatment

    form_model = 'player'

    form_fields = ["charity_select", "crowding_decision", "crowding_norm_decision1", "crowding_norm_decision2"]

    @staticmethod
    def vars_for_template(player: Player):

        participant = player.participant
        lang = participant.language

        current_countryname = player.participant.current_countryname
        print('player.participant.current_countryname', player.participant.current_countryname)

        local_red_cross, image_red_cross_local = get_local_red_cross_info(current_countryname)
        print("current_countryname, local_red_cross", current_countryname, local_red_cross, image_red_cross_local)

        total_endowment = 4
        receiver_endowment = 0
        incentive = 2

        crowding_out_button_pos = player.participant.crowding_out_button_pos

        choice_give = 4
        choice_keep = 0

        print("crowding_out_button_pos", crowding_out_button_pos)

        treatment_incentive = player.participant.treatment_incentive #incentive: true or false
        print("treatment_incentive", treatment_incentive)

        if treatment_incentive:
            image = 'global/treatments/crowding_incentive.png'
        else:
            image = 'global/treatments/crowding.png'

        return dict(
            crowding_decision=player.crowding_decision,
            charity_select = player.field_maybe_none('charity_select'),
            # crowding_norm_decision1=player.field_maybe_none('crowding_norm_decision1'),
            # crowding_norm_decision2=player.field_maybe_none('crowding_norm_decision2'),
            treatment_incentive=treatment_incentive,
            crowding_out_button_pos = crowding_out_button_pos,
            total_endowment = total_endowment,
            incentive = incentive,
            receiver_endowment = receiver_endowment,
            image=image,
            crowding_intro=get_translation('crowding_intro', lang),
            crowding_incentive=get_translation('crowding_incentive', lang),
            crowding_intro2=get_translation('crowding_intro2', lang),
            crowding_norm_incentive =get_translation('crowding_norm_incentive', lang, current_countryname=current_countryname),
            crowding_norm=get_translation('crowding_norm', lang, current_countryname=current_countryname),
            crowding_norm_bonus=get_translation('crowding_norm_bonus', lang, current_countryname=current_countryname),
            crowding_decision_give=get_translation('crowding_decision_give', lang, choice_give=choice_give),
            crowding_decision_keep=get_translation('crowding_decision_keep', lang, choice_keep=choice_keep),
            error_all_sliders =get_translation('error_all_sliders', lang),
            crowding_altruistic=get_translation('crowding_altruistic', lang),
            crowding_likable=get_translation('crowding_likable', lang),
            very_selfish=get_translation('very_selfish', lang),
            selfish=get_translation('selfish', lang),
            slightly_selfish=get_translation('slightly_selfish', lang),
            slightly_altruistic=get_translation('slightly_altruistic', lang),
            altruistic=get_translation('altruistic', lang),
            very_altruistic=get_translation('very_altruistic', lang),
            very_unlikable=get_translation('very_unlikable', lang),
            unlikable=get_translation('unlikable', lang),
            slightly_unlikable=get_translation('slightly_unlikable', lang),
            slightly_likable=get_translation('slightly_likable', lang),
            likable=get_translation('likable', lang),
            very_likable=get_translation('very_likable', lang),
            error3=get_translation('error3', lang),
            person_a=get_translation('person_a', lang),
            button_charity=get_translation('button_charity', lang),
            you=get_translation('you', lang),
            button_next=get_translation('button_next', lang),
            button_decision=get_translation('button_decision', lang),
            button_block=get_translation('button_block', lang),
            # charities = charities,
            local_red_cross = local_red_cross,
            image_red_cross_local = image_red_cross_local,
            current_country=current_countryname,
            total_pages=player.session.config['total_pages'],
        )

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 1
        participant.decision_page_number += 1


class DescriptiveNormPage(Page):

    form_model = 'player'

    form_fields = ["descr_norm"]

    @staticmethod
    def vars_for_template(player: Player):

        participant = player.participant
        lang = participant.language

        current_countryname = player.participant.current_countryname

        total_endowment = 4
        receiver_endowment = 0
        incentive = 2

        treatment_incentive = player.participant.treatment_incentive #incentive: true or false

        if treatment_incentive:
            image = 'global/treatments/crowding_incentive.png'
        else:
            image = 'global/treatments/crowding.png'

        return dict(
            descr_norm=player.descr_norm,
            treatment_incentive=treatment_incentive,
            total_endowment = total_endowment,
            incentive = incentive,
            receiver_endowment = receiver_endowment,
            image=image,
            descr_question=get_translation('descr_question', lang, current_countryname=current_countryname),
            descr_incentive=get_translation('descr_incentive', lang),
            error1=get_translation('error1', lang),
            person_a=get_translation('person_a', lang),
            button_charity=get_translation('button_charity', lang),
            you=get_translation('you', lang),
            button_next=get_translation('button_next', lang),
            button_decision=get_translation('button_decision', lang),
            button_block=get_translation('button_block', lang),
            current_country=current_countryname,
            total_pages=player.session.config['total_pages'],
        )

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 1
        participant.decision_page_number += 1

class ConditionalCoopPage(Page):

    # @staticmethod
    # def is_displayed(player: Player):
    #     return player.crowding_decision == 0

    form_model = 'player'

    def get_form_fields(player: Player):
        return ['cond_coop']

    # form_fields = ["cond_coop"]

    @staticmethod
    def vars_for_template(player: Player):

        participant = player.participant
        lang = participant.language

        non_donor = player.crowding_decision == 0

        current_countryname = player.participant.current_countryname

        local_red_cross, image_red_cross_local = get_local_red_cross_info(current_countryname)
        print("current_countryname, local_red_cross", current_countryname, local_red_cross, image_red_cross_local)

        total_endowment = 4
        receiver_endowment = 0
        incentive = 2

        treatment_incentive = player.participant.treatment_incentive #incentive: true or false

        ## Make buttons for different of proportions

        # 1. Create proportions and empty lists to hold buttons
        proportions_list = [80, 60, 40, 20]
        cond_coop_decision_kept_buttons = []
        cond_coop_decision_gave_buttons = []

        # 2. Loop through the proportions to build the buttons
        for proportion in proportions_list:
            cond_coop_decision_kept_buttons.append({
                'value': proportion,
                'text': get_translation('cond_coop_decision_kept', lang, proportion=proportion)
            })
            cond_coop_decision_gave_buttons.append({
                'value': proportion,
                'text': get_translation('cond_coop_decision_gave', lang, proportion=proportion)
            })

        if treatment_incentive:
            image = 'global/treatments/crowding_incentive.png'
        else:
            image = 'global/treatments/crowding.png'


        return dict(
            non_donor = non_donor,
            cond_coop=player.cond_coop,
            charity_select = player.field_maybe_none('charity_select'),
            treatment_incentive=treatment_incentive,
            total_endowment = total_endowment,
            incentive = incentive,
            receiver_endowment = receiver_endowment,
            image=image,
            cond_coop_kept=get_translation('cond_coop_kept', lang),
            cond_coop_gave=get_translation('cond_coop_gave', lang),
            cond_coop_question=get_translation('cond_coop_question', lang, current_countryname=current_countryname),
            cond_coop_incentive_gave=get_translation('cond_coop_incentive_gave', lang),
            cond_coop_incentive_kept=get_translation('cond_coop_incentive_kept', lang),
            gave_unconditionally=get_translation('gave_unconditionally', lang),
            kept_unconditionally=get_translation('kept_unconditionally', lang),
            cond_coop_decision_kept_buttons=cond_coop_decision_kept_buttons,
            cond_coop_decision_gave_buttons=cond_coop_decision_gave_buttons,
            error1=get_translation('error1', lang),
            person_a=get_translation('person_a', lang),
            button_charity=get_translation('button_charity', lang),
            you=get_translation('you', lang),
            button_next=get_translation('button_next', lang),
            button_decision=get_translation('button_decision', lang),
            button_block=get_translation('button_block', lang),
            local_red_cross=local_red_cross,
            image_red_cross_local=image_red_cross_local,
            current_country=current_countryname,
            total_pages=player.session.config['total_pages'],
        )

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 1
        participant.decision_page_number += 1


page_sequence = [CrowdingInOutPage,
                 DescriptiveNormPage,
                 ConditionalCoopPage,
                 ]
