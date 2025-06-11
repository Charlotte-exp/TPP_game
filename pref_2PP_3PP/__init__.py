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
        participant.language = 'en'

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

class Filler(Page):

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            total_pages=player.session.config['total_pages'],
        )

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 1


class pref_2PP_3PP_Page(Page):
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
            person_a=get_translation("person_a", lang),
            person_b=get_translation("person_b", lang),
            person_c=get_translation("person_c", lang),
            pref_2PP_first=get_translation("pref_2PP_first", lang),
            pref_3PP_first=get_translation("pref_3PP_first", lang),
            pref_2PP=get_translation("pref_2PP", lang),
            pref_3PP=get_translation("pref_3PP", lang),
            button_next=get_translation("button_next", lang),
            total_pages=player.session.config['total_pages'],
        )

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 1
        participant.decision_page_number += 1


class Filler_end_block1(Page):

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            total_pages=player.session.config['total_pages'],
        )

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 1



page_sequence = [Filler,
                 pref_2PP_3PP_Page,
                 Filler_end_block1]
