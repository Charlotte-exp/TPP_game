from otree.api import *
import random

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


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pref_2PP_3PP = models.IntegerField(
        initial=99,
        choices=[[0, f'2PP'], [1, f'3PP'], ],
        widget=widgets.RadioSelect,
        # error_messages={'required': 'You must select an option before continuing.'}, # does not display
    )


# PAGES

class Filler(Page):

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
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
        )

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        #participant.progress += 1


class pref_2PP_3PP_Page(Page):
    form_model = 'player'

    form_fields = ["pref_2PP_3PP"]

    @staticmethod
    def vars_for_template(player: Player):

        pref_2PP_3PP_button_pos = player.participant.pref_2PP_3PP_button_pos

        if pref_2PP_3PP_button_pos:
            text1 = f'You are either Person A or Person B, but you do not know which one. <br> Would you prefer to be in a situation where <b>Person B can remove points from Person A</b> (left) <u>or</u> <b>Person C can remove points from Person A</b> (right) in Stage 2?'
        else:
            text1 = f'You are either Person A or Person B, but you do not know which one. <br> Would you prefer to be in a situation where <b>Person C can remove points from Person A</b> (left) <u>or</u> <b>Person B can remove points from Person A</b> (right) in Stage 2?'

        text2PP = f'<b>Person B</b>&nbsp;can remove points.'
        text3PP = f'<b>Person C</b>&nbsp;can remove points.'

        image2PP = 'global/treatments/pref2PP.png'
        image3PP = 'global/treatments/pref3PP.png'

        return dict(
            pref_2PP_3PP=player.pref_2PP_3PP,
            pref_2PP_3PP_button_pos = pref_2PP_3PP_button_pos,
            text1=text1,
            text2PP=text2PP,
            text3PP=text3PP,
            image2PP=image2PP,
            image3PP=image3PP,
            total_pages=player.session.config['total_pages'],
        )

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 1
        participant.decision_page_number += 1



page_sequence = [Filler,
                 pref_2PP_3PP_Page,
                 Filler_end_block1]
