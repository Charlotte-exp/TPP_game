from otree.api import *

import random
import itertools
import csv
import os

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
                image_path = f"/local_red_cross/iso2_{iso2_code}.png"
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

        current_countryname = player.participant.current_countryname
        print('player.participant.current_countryname', player.participant.current_countryname)

        local_red_cross, image_red_cross_local = get_local_red_cross_info(current_countryname)
        print("current_countryname, local_red_cross", current_countryname, local_red_cross, image_red_cross_local)

        total_endowment = 4
        receiver_endowment = 0
        incentive = 2

        crowding_out_button_pos = player.participant.crowding_out_button_pos

        print("crowding_out_button_pos", crowding_out_button_pos)

        treatment_incentive = player.participant.treatment_incentive #incentive: true or false
        print("treatment_incentive", treatment_incentive)

        text2 = '<br> If you donate, we will convert the points into money and transfer it to the charity.'
        text4 = f'<b>Important:</b> If your response is close to the average rating in {current_countryname}, you receive 8 points.'
        text5 = 'Make your decision:'

        if treatment_incentive:
            image = 'global/treatments/crowding_incentive.png'
            text1 = 'Now, you decide if you want to <b style="color: green;">give</b> <b>4 of your bonus points to charity</b>. <br> <b>Important</b>: You receive additional <b>2 points</b> for yourself if you give <b>4 points</b> to charity.'
            text3 = f'<b>How is someone perceived in {current_countryname} </b> <br> if they <b>give 4 points</b> to charity and <b>received 2 points</b> for themselves?'
        else:
            image = 'global/treatments/crowding.png'
            text1 = 'Now, you decide if you want to <b style="color: green;">give</b> <b>4 of your bonus points to charity</b>.'
            text3 = f'<b>How is someone perceived in {current_countryname} </b> if they <b>give 4 points</b> to charity?'

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
            text1 = text1,
            text2 = text2,
            text3 = text3,
            text4 = text4,
            text5 = text5,
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

        current_countryname = player.participant.current_countryname

        total_endowment = 4
        receiver_endowment = 0
        incentive = 2

        treatment_incentive = player.participant.treatment_incentive #incentive: true or false

        text1 = f'<br> <b>Out of 100 people in {current_countryname}</b>, <br> how many do you think <b>gave 4 points to charity</b> in the previous decision? '
        text2 = f'<b>Important</b>:</b> If your response is close to the correct number, you will receive 8 points.'

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
            text1 = text1,
            text2 = text2,
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

        non_donor = player.crowding_decision == 0

        current_countryname = player.participant.current_countryname

        local_red_cross, image_red_cross_local = get_local_red_cross_info(current_countryname)
        print("current_countryname, local_red_cross", current_countryname, local_red_cross, image_red_cross_local)

        total_endowment = 4
        receiver_endowment = 0
        incentive = 2

        treatment_incentive = player.participant.treatment_incentive #incentive: true or false

        if treatment_incentive:
            image = 'global/treatments/crowding_incentive.png'
        else:
            image = 'global/treatments/crowding.png'

        text2 = f'<b style="color: red;">Depending on what others in {current_countryname} do,<br></b> <b> would you change your decision?</b>'
        text3 = 'Out of 100 people, if'

        if non_donor:
            text1 = 'You decided not to give 4 points to charity.'
            text4 = f'or more <u>did give</u>, I also want to give my points to charity.'
            text5 = 'Regardless of the choices of others, I do not want to give my points to charity. '
            text6 = f'<b>Important:</b> If the condition in your answer is met, your bonus points will be transferred to the charity.'
        else:
            text1 = 'You decided to give 4 points to charity.'
            text4 = f'or more <u>did not give</u>, I also do not want to give my points to charity.'
            text5 = 'Regardless of the choices of others, I want to give my points to charity. '
            text6 = f'<b>Important:</b> If the condition in your answer is met, your bonus points will not be transferred to the charity.'



        return dict(
            non_donor = non_donor,
            cond_coop=player.cond_coop,
            charity_select = player.field_maybe_none('charity_select'),
            treatment_incentive=treatment_incentive,
            total_endowment = total_endowment,
            incentive = incentive,
            receiver_endowment = receiver_endowment,
            image=image,
            text1 = text1,
            text2 = text2,
            text3 = text3,
            text4 = text4,
            text5 = text5,
            text6 = text6,
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
