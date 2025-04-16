from otree.api import *

import random
import itertools

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
    #
    # if subsession.round_number == 1:
    #     for player in subsession.get_players():
    #         participant = player.participant
    #         # Set treatment for later tasks (incentive/crowding_out; conditional_coop)
    #         participant.treatment_incentive = random.choice(
    #             [True, False])  # Crowding out task; true indicates incentive is offered
    #         participant.treatment_cond_coop = random.choice(
    #             [True, False])  # Crowding out task; true indicates incentive is offered
    #
    #         print('set incentive treatment to', participant.treatment_incentive)
    #         print('set cond coop treatment to', participant.treatment_cond_coop)

    participants = subsession.session.get_participants()

    combinations = list(itertools.product([True, False], [True, False]))  # (incentive, cond_coop)

    num_participants = len(participants)
    full_list = combinations * (num_participants // 4)
    remainder = combinations[:(num_participants % 4)]
    treatment_list = full_list + remainder

    random.shuffle(treatment_list)

    for p, (incentive, cond_coop) in zip(participants, treatment_list):
        p.treatment_incentive = incentive
        p.treatment_cond_coop = cond_coop

        print('set incentive treatment to', p.treatment_incentive)
        print('set cond coop treatment to', p.treatment_cond_coop)




class Group(BaseGroup):
    pass


class Player(BasePlayer):

    charity_select = models.StringField(
        # choices=["Unicef", "Red Cross", "Doctors Without Borders", "Save the Children", "other"],
        blank=True  # Optional: allow it to be empty if no donation is made
    )
    crowding_decision = models.IntegerField(
        initial=3,
        choices=[[0, f'keep'], [4, f'give'], ],
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )
    crowding_norm_decision1 = models.IntegerField(
        initial=0,
        choices=[(i, f'value {i}') for i in range(12 + 1)],
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )
    crowding_norm_decision2 = models.IntegerField(
        initial=0,
        choices=[(i, f'value {i}') for i in range(12 + 1)],
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )
    descr_norm = models.IntegerField(
        initial=0,
        choices=[(i, f'value {i}') for i in range(100)],
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )
    cond_coop = models.IntegerField(
        initial=0,
        choices=[(i, f'value {i}') for i in range(1000)],
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )
    cond_coop_control = models.IntegerField(
        initial=0,
        choices=[(i, f'value {i}') for i in range(1000)],
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )


# PAGES
class CrowdingInOutPage(Page):

    # @staticmethod
    # def is_displayed(player: Player):
    #     return "give" in player.treatment

    form_model = 'player'

    form_fields = ["charity_select", "crowding_decision", "crowding_norm_decision1", "crowding_norm_decision2"]

    @staticmethod
    def vars_for_template(player: Player):

        charities = ["Unicef", "Red Cross", "Doctors Without Borders", "Save the Children", "other"]

        current_country = "Switzerland" # Plug in correct country
        # current_country = C.CURRENT_COUNTRYNAME

        total_endowment = 4
        receiver_endowment = 0
        incentive = 2

        treatment_incentive = player.participant.treatment_incentive #incentive: true or false
        print("treatment_incentive", treatment_incentive)

        text2 = '<br> If you donate, we will convert the points into money and transfer it to the charity.'
        text4 = f'<b>Important:</b> If your response is the same as the most common response in {current_country}, you will receive 2 extra points.'
        text5 = 'Do you give <b> 4 points </b> to charity?'

        if treatment_incentive:
            image = 'global/treatments/crowding_incentive.png'
            text1 = 'Now, you decide if you want to <b style="color: green;">give</b> <b>4 of your bonus points to charity</b>. <br> <b>Important</b>: You receive additional <b>2 points</b> for yourself if you give <b>4 points</b> to charity.'
            text3 = f'<b>How is someone perceived in {current_country} </b> <br> if they <b>gave 4 points</b> to charity and <b>received 2 points</b> for themselves?'
        else:
            image = 'global/treatments/crowding.png'
            text1 = 'Now, you decide if you want to <b style="color: green;">give</b> <b>4 of your bonus points to charity</b>.'
            text3 = f'<b>How is someone perceived in {current_country} </b> if they <b>gave 4 points</b> to charity?'

        return dict(
            crowding_decision=player.crowding_decision,
            charity_select = player.field_maybe_none('charity_select'),
            crowding_norm_decision1=player.crowding_norm_decision1,
            crowding_norm_decision2=player.crowding_norm_decision2,
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
            charities = charities,
            current_country=current_country,
        )

class DescriptiveNormPage(Page):

    form_model = 'player'

    form_fields = ["descr_norm"]

    @staticmethod
    def vars_for_template(player: Player):

        current_country = "Switzerland" # Plug in correct country

        total_endowment = 4
        receiver_endowment = 0
        incentive = 2

        treatment_incentive = player.participant.treatment_incentive #incentive: true or false

        text1 = f'<br>  <b>Out of 100 people in {current_country}, <br> how many do you think gave 4 points to charity? '
        text2 = f'Important:</b> If your response is close to the correct number (plus or minus 5), you will receive 2 extra points.'

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
            current_country=current_country,
        )

class ConditionalCoopPage(Page):

    @staticmethod
    def is_displayed(player: Player):
        return player.crowding_decision == 0

    form_model = 'player'

    def get_form_fields(player: Player):
        if player.participant.treatment_cond_coop:
            return ['cond_coop']
        else:
            return ['cond_coop_control']

    # form_fields = ["cond_coop"]

    @staticmethod
    def vars_for_template(player: Player):

        charities = ["Unicef", "Red Cross", "Doctors Without Borders", "Save the Children", "other"]

        current_country = "Switzerland" # Plug in correct country
        # current_country = C.CURRENT_COUNTRYNAME

        total_endowment = 4
        receiver_endowment = 0
        incentive = 2

        treatment_incentive = player.participant.treatment_incentive #incentive: true or false

        treatment_cond_coop = player.participant.treatment_cond_coop  # conditional cooperation: true (treatment) or false (reminder control)

        text1 = 'You decided that you do not want to give 4 points to charity. <br>'

        if treatment_cond_coop:
            text3 = '<b>Yes, I <u>am</u> </b> willing, <b>IF</b>'
            text4 = f'out of 100 people in {current_country} also contribute.'
            text5 = '<b>No, I am <u>not</u> </b> willing, (regardless of what others do)'
            text6 = f'<br> <b>Important:</b> If the condition is fulfilled, 4 of your bonus points will be converted into money and transferred to the charity. <br>'
        else:
            text3 = '<b>Yes, I <u>am</u> </b> willing. Give <b>4 points</b> to charity.'
            text4 = ''
            text5 = '<b>No, I am <u>not</u> </b> willing. Give <b>0 points</b> to charity.'
            text6 = f'<br> <b>Important:</b> If you decide to donate, 4 of your bonus points will be converted into money and transferred to the charity. <br>'


        if treatment_incentive:
            image = 'global/treatments/crowding_incentive.png'
            if treatment_cond_coop:
                text2 = f'<b style="color: red;">If others in {current_country} donate</b>, are you willing to <b>give 4 points</b> to charity and <b> receive 2 points</b> for yourself?'
            else:
                text2 = f'<b style="color: red;">If you think about it again</b>, are you willing to <b>give 4 points</b> to charity and <b> receive 2 points</b> for yourself?'
        else:
            image = 'global/treatments/crowding.png'
            if treatment_cond_coop:
                text2 = f'<b style="color: red;">If others in {current_country} donate</b>, are you willing to <b>give 4 points</b> to charity?'
            else:
                text2 = f'<b style="color: red;">If you think about it again</b>, are you willing to <b>give 4 points</b> to charity?'


        return dict(
            cond_coop=player.cond_coop,
            cond_coop_control = player.cond_coop_control,
            charity_select = player.field_maybe_none('charity_select'),
            treatment_incentive=treatment_incentive,
            treatment_cond_coop = treatment_cond_coop,
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
            charities = charities,
            current_country=current_country,
        )


page_sequence = [CrowdingInOutPage,
                 DescriptiveNormPage,
                 ConditionalCoopPage,
                 ]
