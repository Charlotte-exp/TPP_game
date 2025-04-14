from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'demographics'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    # Demographics
    age = models.IntegerField(
        verbose_name='What is your age?',
        min=18, max=100)

    gender = models.StringField(
        choices=['Female', 'Male', 'Other'],
        verbose_name='What gender do you identify as?',
        widget=widgets.RadioSelect)

    born = models.StringField(
        choices=['Yes', 'No'],
        verbose_name='Were you born in this country?',
        widget=widgets.RadioSelect)

    born_parents = models.StringField(
        choices=['Yes', 'No'],
        verbose_name='Were you born in this country?',
        widget=widgets.RadioSelect)

    how_long = models.StringField(
        choices=['less than 1 year', '1-5 years', '5-10 years', 'more than 10 years'],
        verbose_name='How long have you lived in this country?',
        widget=widgets.RadioSelect)

    income_ladder = models.StringField(
        verbose_name='What is the total combined income of your household?',
        min=1, max=100,
        widget=widgets.RadioSelect)

    education = models.StringField(
        choices=['No formal education', 'Compulsory school', 'Post-secondary education',
                 'Undergraduate degree', 'Postgraduate degree', 'Prefer not to say'],
        verbose_name='What is the highest level of education you have completed?',
        widget=widgets.RadioSelect)

    rural = models.StringField(
        choices=["less than 10.000 inhabitants", 'between 10.000 and 250.000 inhabitants', 'between 250.000 and 1 million inhabitants',
                 'More than 1 million inhabitants'],
        verbose_name='What is your ethnicity?',
        widget=widgets.RadioSelect)

    comment_box = models.LongStringField(
        verbose_name=''
    )


########### PAGES ############
class Demographics(Page):
    form_model = 'player'
    form_fields = ['age', 'gender','born','born_parents','how_long', 'income_ladder', 'education', 'rural']


    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.progress += 1


class Payment(Page):
    pass


page_sequence = [Demographics,
                 Payment]
