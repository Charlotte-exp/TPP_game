from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'pref_2PP_3PP'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


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
class pref_2PP_3PP_Page(Page):
    form_model = 'player'

    form_fields = ["pref_2PP_3PP"]

    @staticmethod
    def vars_for_template(player: Player):

        text1 = f'You are Person A or Person B. <br> Would you prefer to be in a situation where <b>Person B can remove points from Person A</b> (left) <u>or</u> <b>Person C can remove points from Person A</b> (right) in Stage 2?'
        text2 = f'<b>Person B</b>&nbsp;can remove points.'
        text3 = f'<b>Person C</b>&nbsp;can remove points.'

        image2PP = 'global/treatments/pref2PP.png'
        image3PP = 'global/treatments/pref3PP.png'

        return dict(
            pref_2PP_3PP=player.pref_2PP_3PP,
            text1=text1,
            text2=text2,
            text3=text3,
            image2PP=image2PP,
            image3PP=image3PP,
        )


page_sequence = [pref_2PP_3PP_Page]
