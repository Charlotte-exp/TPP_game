from otree.api import *
import random

from translations import get_translation

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'pref_2PP_3PP'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass

def creating_session(subsession): # Just for testing treatment allocation, will eventually me moved to create-session in baseline trials

    for player in subsession.get_players():
        participant = player.participant
        participant.pref_2PP_3PP_button_pos = random.choice([True, False])

        ''' ONLY WHEN TESTING APP ON ITS OWN'''
        participant.progress = 1
        participant.language = 'de'

class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pref_2PP_3PP = models.IntegerField(
        initial=999,
        choices=[[0, f'2PP'], [1, f'3PP'], ],
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )


#############  PAGES  ###############

class FillerEndBlock1(Page):

    @staticmethod
    def vars_for_template(player: Player):
        participant = player.participant
        lang = participant.language

        return dict(
            filler1_title=get_translation("filler1_title", lang),
            filler1_completed=get_translation("filler1_completed", lang),
            filler1_next_page=get_translation("filler1_next_page", lang),
            button_next=get_translation("button_next", lang),
            total_pages=player.session.config['total_pages'],
        )

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 1


class Pref_2PP_3PP(Page):
    form_model = 'player'
    form_fields = ["pref_2PP_3PP"]

    @staticmethod
    def vars_for_template(player: Player):
        participant = player.participant
        lang = participant.language

        image2PP = 'global/treatments/pref2PP.png'
        image3PP = 'global/treatments/pref3PP.png'
        return dict(
            pref_2PP_3PP=player.pref_2PP_3PP,
            pref_2PP_3PP_button_pos = player.participant.pref_2PP_3PP_button_pos,
            image2PP=image2PP,
            image3PP=image3PP,
            button_decision=get_translation("button_decision", lang),
            person_a=get_translation("person_a", lang),
            person_b=get_translation("person_b", lang),
            person_c=get_translation("person_c", lang),
            pref_2PP_first=get_translation("pref_2PP_first", lang),
            pref_3PP_first=get_translation("pref_3PP_first", lang),
            pref_2PP=get_translation("pref_2PP", lang),
            pref_3PP=get_translation("pref_3PP", lang),
            or_button=get_translation("or_button", lang),
            button_next=get_translation("button_next", lang),
            button_block=get_translation("button_block", lang),
            error3=get_translation("error3", lang),
            total_pages=player.session.config['total_pages'],
        )

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 1
        participant.decision_page_number += 1


class FillerStartBlock2(Page):

    @staticmethod
    def vars_for_template(player: Player):
        participant = player.participant
        lang = participant.language

        return dict(
            filler2a_title=get_translation("filler2a_title", lang),
            filler2a_beginning=get_translation("filler2a_beginning", lang),
            filler2_selected=get_translation("filler2_selected", lang),
            filler2a_different=get_translation("filler2a_different", lang),
            button_next=get_translation("button_next", lang),
            total_pages=player.session.config['total_pages'],
        )

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 1



page_sequence = [FillerEndBlock1,
                 Pref_2PP_3PP,
                 FillerStartBlock2]
