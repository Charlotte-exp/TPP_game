from otree.api import *

import random
import itertools
import csv
import os

from translations import get_translation

doc = """
Your app description
"""

def get_country_dict(lang, iso2=None):
    with open('_static/global/country_codes_Toluna_lang.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
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
    NAME_IN_URL = 'crowding_out'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    ratings_extra_points_block2 = 4  # extra bonus for (norm) ratings close to country average: lower in block 2, where there are lower payoffs


class Subsession(BaseSubsession):
    pass



def creating_session(subsession): # Just for testing on its own

    for player in subsession.get_players():
        participant = player.participant
        
        # Set variables in case of testing app on its own
        # Set language to English if English is the only offered language in that country (in this case participants do not see language selection pages)
        if 'language' not in participant.vars:
            participant.language = 'en'

        if 'progress' not in participant.vars:
            participant.progress = 1
            participant.decision_page_number = 0
            participant.current_countryname = get_country_dict(participant.language, participant.current_country)

        if 'treatment_incentive' not in participant.vars:
            participant.treatment_incentive = random.choice([True, False])
            participant.crowding_out_button_pos = random.choice([True, False])
            print("random treatment incentive for testing", participant.treatment_incentive)

        if 'current_countryname' not in participant.vars:
            participant.current_countryname = get_country_dict(participant.language, participant.current_country)
            print("current_countryname", participant.current_countryname)


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
    cond_coop_interdep = models.IntegerField(
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
    cond_coop_slider = models.IntegerField(
        min=0,
        max=101,
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

        participant = player.participant
        lang = participant.language

        treatment_incentive = participant.treatment_incentive
        print("treatment_incentive", treatment_incentive)

        current_countryname = player.participant.current_countryname
        # print('player.participant.current_countryname', player.participant.current_countryname)

        local_red_cross, image_red_cross_local = get_local_red_cross_info(current_countryname)
        # print("current_countryname, local_red_cross", current_countryname, local_red_cross, image_red_cross_local)

        total_endowment = 4
        receiver_endowment = 0
        incentive = 2

        crowding_out_button_pos = player.participant.crowding_out_button_pos

        choice_give = 4
        choice_keep = 0

        # print("crowding_out_button_pos", crowding_out_button_pos)

        treatment_incentive = player.participant.treatment_incentive #incentive: true or false
        # print("treatment_incentive", treatment_incentive)

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
            crowding_norm_incentive =get_translation('crowding_norm_incentive', lang, in_current_countryname=current_countryname),
            crowding_norm=get_translation('crowding_norm', lang, in_current_countryname=current_countryname),
            crowding_norm_bonus=get_translation('crowding_norm_bonus', lang, in_current_countryname=current_countryname, ratings_extra_points_block2=C.ratings_extra_points_block2),
            crowding_decision_give=get_translation('crowding_decision', lang, choice=choice_give),
            crowding_decision_keep=get_translation('crowding_decision_keep', lang, choice=choice_give),
            error_all_sliders =get_translation('error_all_sliders', lang),
            crowding_altruistic=get_translation('crowding_altruistic', lang),
            crowding_likable=get_translation('crowding_likable', lang),
            not_at_all_altruistic=get_translation('not_at_all_altruistic', lang),
            selfish=get_translation('selfish', lang),
            slightly_selfish=get_translation('slightly_selfish', lang),
            slightly_altruistic=get_translation('slightly_altruistic', lang),
            altruistic=get_translation('altruistic', lang),
            very_altruistic=get_translation('very_altruistic', lang),
            not_at_all_likable=get_translation('not_at_all_likable', lang),
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
            descr_question=get_translation('descr_question', lang, in_current_countryname=current_countryname),
            descr_incentive=get_translation('block2_norm_incentive', lang,
                                                 ratings_extra_points=C.ratings_extra_points_block2),
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

    form_model = 'player'

    def get_form_fields(player: Player):
        return ['cond_coop']

    @staticmethod
    def vars_for_template(player: Player):

        participant = player.participant
        lang = participant.language

        # non_donor = player.crowding_decision == 0

        current_countryname = player.participant.current_countryname

        total_endowment = 4
        receiver_endowment = 0
        incentive = 2

        treatment_incentive = player.participant.treatment_incentive #incentive: true or false

        if treatment_incentive:
            image = 'global/treatments/crowding_incentive.png'
        else:
            image = 'global/treatments/crowding.png'

        # if non_donor:
        unconditional_keep = get_translation('kept_unconditionally', lang)
        cond_coop_info = get_translation('cond_coop_indiv_kept', lang)
        cond_coop_incentive = get_translation('cond_coop_incentive_kept', lang)
        cond_coop_completion = get_translation('cond_coop_completion_kept', lang)
        cond_coop_action = get_translation('cond_coop_donated', lang)
        unconditional_give = get_translation('gave_unconditionally', lang)

# else:
        #     unconditional = get_translation('gave_unconditionally', lang)
        #     cond_coop_info = get_translation('cond_coop_indiv_gave', lang)
        #     cond_coop_incentive = get_translation('cond_coop_incentive_gave', lang)
        #     cond_coop_completion = get_translation('cond_coop_completion_gave', lang)
        #     cond_coop_action = get_translation('cond_coop_kept', lang)


        return dict(
            current_country=current_countryname,
            # non_donor = non_donor,
            cond_coop=player.cond_coop,
            charity_select = player.field_maybe_none('charity_select'),
            treatment_incentive=treatment_incentive,
            total_endowment = total_endowment,
            incentive = incentive,
            receiver_endowment = receiver_endowment,
            image=image,
            cond_coop_70=get_translation('cond_coop_70', lang),
            cond_coop_60=get_translation('cond_coop_60', lang),
            cond_coop_50=get_translation('cond_coop_50', lang),
            cond_coop_40=get_translation('cond_coop_40', lang),
            cond_coop_30=get_translation('cond_coop_30', lang),
            cond_coop_completion=cond_coop_completion,
            cond_coop_info = cond_coop_info,
            cond_coop_question=get_translation('cond_coop_question_independent', lang, in_current_countryname=current_countryname),
            cond_coop_action=cond_coop_action,
            cond_coop_incentive = cond_coop_incentive,
            unconditional_keep = unconditional_keep,
            unconditional_give = unconditional_give,
            cond_coop_new_decision=get_translation('cond_coop_new_decision', lang),
            cond_coop_question_donor_nondonor_indep=get_translation('cond_coop_question_donor_nondonor_indep', lang, in_current_countryname=current_countryname),
            error1=get_translation('error1', lang),
            person_a=get_translation('person_a', lang),
            button_charity=get_translation('button_charity', lang),
            you=get_translation('you', lang),
            button_next=get_translation('button_next', lang),
            button_decision=get_translation('button_decision', lang),
            button_block=get_translation('button_block', lang),
            total_pages=player.session.config['total_pages'],
        )

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 1
        participant.decision_page_number += 1


class ConditionalCoopInterdepPage(Page):

    form_model = 'player'

    def get_form_fields(player: Player):
        return ['cond_coop_interdep']

    @staticmethod
    def vars_for_template(player: Player):

        participant = player.participant
        lang = participant.language

        # non_donor = player.crowding_decision == 0

        current_countryname = player.participant.current_countryname

        total_endowment = 4
        receiver_endowment = 0
        incentive = 2

        treatment_incentive = player.participant.treatment_incentive #incentive: true or false

        if treatment_incentive:
            image = 'global/treatments/crowding_incentive.png'
        else:
            image = 'global/treatments/crowding.png'

        # if non_donor:
        unconditional_keep = get_translation('kept_unconditionally', lang)
        cond_coop_info = get_translation('cond_coop_indiv_kept', lang)
        cond_coop_incentive = get_translation('cond_coop_incentive_kept', lang)
        cond_coop_completion = get_translation('cond_coop_completion_kept', lang)
        cond_coop_action = get_translation('cond_coop_donate_if', lang)
        unconditional_give = get_translation('gave_unconditionally', lang)
            # cond_coop_interdependent_explanation2= get_translation('cond_coop_interdependent_explanation2', lang)
            # action_consequence = get_translation('cond_coop_donate', lang)
            # action = get_translation('cond_coop_start_donating', lang)
            # action_if = get_translation('cond_coop_donate_if', lang)
            # anti_action = get_translation('cond_coop_keep', lang)
            # cond_coop_slide1 = get_translation('cond_coop_slide1', lang, action=action_consequence)
            # cond_coop_slide2 = get_translation('cond_coop_slide2', lang, action=action)
            # cond_coop_slide3 = get_translation('cond_coop_slide3', lang, action1=action, action2=action_if, num_condition = 40)
            # cond_coop_slide4 = get_translation('cond_coop_slide4', lang, action=action_consequence)
            # cond_coop_slide5 = get_translation('cond_coop_slide5', lang, action=action)
            # cond_coop_slide6 = get_translation('cond_coop_slide6', lang, action1=action, action2=action_if, num_condition = 80)
            # cond_coop_slide7 = get_translation('cond_coop_slide7', lang, action=anti_action)
            # cond_coop_slide8 = get_translation('cond_coop_slide1', lang, action=anti_action)
            # cond_coop_slide8 = cond_coop_slide8.replace("color: red;", "color: grey;")
            # cond_coop_slide9 = get_translation('cond_coop_slide9', lang, action=action_consequence)
            # slide1 = 'global/slides/slide1.jpg'
            # slide2 = 'global/slides/slide2.jpg'
            # slide3 = 'global/slides/slide3.jpg'
            # slide4 = 'global/slides/slide4.jpg'
            # slide5 = 'global/slides/slide5.jpg'
            # slide6 = 'global/slides/slide6.jpg'
            # slide7 = 'global/slides/slide7.jpg'
            # slide8 = 'global/slides/slide8.jpg'
            # slide9 = 'global/slides/slide9.jpg'

        # else:
        #     unconditional = get_translation('gave_unconditionally', lang)
        #     cond_coop_info = get_translation('cond_coop_indiv_gave', lang)
        #     cond_coop_incentive = get_translation('cond_coop_incentive_gave', lang)
        #     cond_coop_completion = get_translation('cond_coop_completion_gave', lang)
        #     cond_coop_action = get_translation('cond_coop_keep_if', lang)
        #     # action_consequence = get_translation('cond_coop_keep', lang)
        #     # action = get_translation('cond_coop_stop_donating', lang)
        #     # action_if = get_translation('cond_coop_keep_if', lang)
        #     # anti_action = get_translation('cond_coop_donate', lang)
        #     # cond_coop_interdependent_explanation2 = get_translation('cond_coop_interdependent_explanation2b', lang)
        #     # cond_coop_slide2 = get_translation('cond_coop_slide2', lang, action=action)
        #     # cond_coop_slide3 = get_translation('cond_coop_slide3', lang, action1=action, action2=action_consequence, num_condition = 30)
        #     # cond_coop_slide4 = get_translation('cond_coop_slide4', lang, action=action_consequence)
        #     # cond_coop_slide5 = get_translation('cond_coop_slide5', lang, action=action)
        #     # cond_coop_slide6 = get_translation('cond_coop_slide6', lang, action1=action, action2=action_consequence, num_condition = 60)
        #     # cond_coop_slide7 = get_translation('cond_coop_slide7', lang, action=anti_action)
        #     # cond_coop_slide9 = get_translation('cond_coop_slide9', lang, action=action_consequence)
        #     # cond_coop_slide8 = get_translation('cond_coop_slide1', lang, action=anti_action)
        #     # cond_coop_slide1 = get_translation('cond_coop_slide1', lang, action=action_consequence)
        #     # cond_coop_slide1 = cond_coop_slide1.replace("color: red;", "color: grey;")
        #     # slide1 = 'global/slides/slide1b.jpg'
        #     # slide2 = 'global/slides/slide2b.jpg'
        #     # slide3 = 'global/slides/slide3b.jpg'
        #     # slide4 = 'global/slides/slide4b.jpg'
        #     # slide5 = 'global/slides/slide5b.jpg'
        #     # slide6 = 'global/slides/slide6b.jpg'
        #     # slide7 = 'global/slides/slide7b.jpg'
        #     # slide8 = 'global/slides/slide8b.jpg'
        #     # slide9 = 'global/slides/slide9b.jpg'

        return dict(
            current_country=current_countryname,
            # non_donor = non_donor,
            cond_coop_interdep=player.cond_coop_interdep,
            charity_select = player.field_maybe_none('charity_select'),
            treatment_incentive=treatment_incentive,
            total_endowment = total_endowment,
            incentive = incentive,
            receiver_endowment = receiver_endowment,
            image=image,
            cond_coop_interdependent_explanation1=get_translation('cond_coop_interdependent_explanation1', lang),
            cond_coop_interdependent_explanation2=get_translation('cond_coop_interdependent_explanation2', lang),
            cond_coop_interdependent_explanation3=get_translation('cond_coop_interdependent_explanation3_V2', lang),
            cond_coop_70=get_translation('cond_coop_70', lang),
            cond_coop_60=get_translation('cond_coop_60', lang),
            cond_coop_50=get_translation('cond_coop_50', lang),
            cond_coop_40=get_translation('cond_coop_40', lang),
            cond_coop_30=get_translation('cond_coop_30', lang),
            cond_coop_group=get_translation('cond_coop_group_interdependent_V2', lang, in_current_countryname=current_countryname),
            cond_coop_interdependent_explanation=get_translation('cond_coop_interdependent_explanation', lang),
            cond_coop_completion=cond_coop_completion,
            cond_coop_info = cond_coop_info,
            cond_coop_question=get_translation('cond_coop_question_interdependent', lang),
            cond_coop_action=cond_coop_action,
            cond_coop_incentive = cond_coop_incentive,
            unconditional_keep=unconditional_keep,
            unconditional_give=unconditional_give,
            cond_coop_new_decision=get_translation('cond_coop_new_decision', lang),
            cond_coop_question_donor_nondonor_interdep=get_translation('cond_coop_question_donor_nondonor_interdep', lang,
                                                                    in_current_countryname=current_countryname),
            cond_coop_example_title=get_translation('cond_coop_example_title', lang),
            # slide1=slide1,
            # slide2=slide2,
            # slide3=slide3,
            # slide4=slide4,
            # slide5=slide5,
            # slide6=slide6,
            # slide7=slide7,
            # slide8=slide8,
            # slide9=slide9,
            # cond_coop_slide1=cond_coop_slide1,
            # cond_coop_slide2=cond_coop_slide2,
            # cond_coop_slide3=cond_coop_slide3,
            # cond_coop_slide4=cond_coop_slide4,
            # cond_coop_slide5=cond_coop_slide5,
            # cond_coop_slide6=cond_coop_slide6,
            # cond_coop_slide7=cond_coop_slide7,
            # cond_coop_slide8=cond_coop_slide8,
            # cond_coop_slide9=cond_coop_slide9,
            # button_back=get_translation('button_back', lang),
            error1=get_translation('error1', lang),
            person_a=get_translation('person_a', lang),
            button_charity=get_translation('button_charity', lang),
            you=get_translation('you', lang),
            button_next=get_translation('button_next', lang),
            button_decision=get_translation('button_decision', lang),
            button_block=get_translation('button_block', lang),
            total_pages=player.session.config['total_pages'],
        )

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 1
        participant.decision_page_number += 1



page_sequence = [CrowdingInOutPage,
                 DescriptiveNormPage,
                 ConditionalCoopPage,
                 ConditionalCoopInterdepPage,
                 ]
