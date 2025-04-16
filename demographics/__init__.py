from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'demographics'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    ## Demographics
    age = models.IntegerField(
        verbose_name='What is your age?',
        min=0, max=100
    )

    gender = models.StringField(
        choices=['Female', 'Male', 'Other'],
        verbose_name='What gender do you identify as?',
        widget=widgets.RadioSelect
    )
    born = models.StringField(
        choices=['Yes', 'No'],
        verbose_name='Were you born in this country?',
        widget=widgets.RadioSelect
    )
    born_parents = models.StringField(
        choices=['Yes', 'No'],
        verbose_name='Were you born in this country?',
        widget=widgets.RadioSelect
    )
    how_long = models.StringField(
        choices=['less than 1 year', '1-5 years', '5-10 years', 'more than 10 years'],
        verbose_name='How long have you lived in this country?',
        widget=widgets.RadioSelect
    )
    income_ladder = models.IntegerField(
        choices=[i for i in range(1, 11)],
        blank=True,
        label="Where would you place yourself on this ladder?"
    )
    education = models.StringField(
        choices=['No formal education', 'Compulsory school', 'Post-secondary education',
                 'Undergraduate degree', 'Postgraduate degree', 'Prefer not to say'],
        verbose_name='What is the highest level of education you have completed?',
        widget=widgets.RadioSelect
    )
    rural = models.StringField(
        choices=["less than 10.000 inhabitants", 'between 10.000 and 250.000 inhabitants',
                 'between 250.000 and 1 million inhabitants', 'More than 1 million inhabitants'],
        verbose_name='How large was the place where grew up?',
        widget=widgets.RadioSelect
    )

    ## Relational Mobility
    q1 = models.StringField(
        choices=[
            [0, 'Strongly disagree'], [1, 'Disagree'], [2, 'Slightly disagree'],
            [3, 'Slightly agree'], [4, 'Agree'], [5, 'Strongly agree'],
        ],
        verbose_name='How large was the place where grew up?',
        widget=widgets.RadioSelect
    )
    q2 = models.StringField(
        choices=[
            [0, 'Strongly disagree'], [1, 'Disagree'], [2, 'Slightly disagree'],
            [3, 'Slightly agree'], [4, 'Agree'], [5, 'Strongly agree'],
        ],
        verbose_name='How large was the place where grew up?',
        widget=widgets.RadioSelect
    )

    ## Self - other circle
    self_other = models.IntegerField()

    comment_box = models.LongStringField(
        verbose_name=''
    )


########### PAGES ############

class Demographics(Page):
    form_model = 'player'
    form_fields = ['age', 'gender','born','born_parents','how_long', 'education', 'rural']

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        #participant.progress += 1

class Ladder(Page):
    form_model = 'player'
    form_fields = ['income_ladder']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            ladder_values=list(range(10, 0, -1)),  # From 10 to 1
        )

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        #participant.progress += 1

class RelationalMobility(Page):
    form_model = 'player'
    form_fields = ['q1', 'q2']

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        #participant.progress += 1

class Circle(Page):
    form_model = 'player'
    form_fields = ['self_other']

    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        #participant.progress += 1


class ResultsWaitPage(WaitPage):
    pass


class Payment(Page):

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    def vars_for_template(player: Player):
        return {
            'participation_fee': player.session.config['participation_fee'],
        }


page_sequence = [Ladder,
                 Circle,
                 RelationalMobility,
                 Demographics,
                 #ResultsWaitPage,
                 Payment]
