from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

author = 'Robin Engelhardt'

doc = """
Thomas Bolanders cooperative Canteen Dilemma with bonuses
"""

class Constants(BaseConstants):
    name_in_url = 'canteen_dilemma'
    players_per_group = 2
    num_rounds = 10
    endowment = 10
    win_canteen = 0.6
    win_office = 0.4
    instructions_template = 'canteen_dilemma/Instructions.html'
    arrival_times = [8.30, 8.31, 8.32, 8.33, 8.34, 8.35, 8.36, 8.37, 8.38, 8.39, 8.40,
                     8.41, 8.42, 8.43, 8.44, 8.45, 8.46, 8.47, 8.48, 8.49, 8.50,
                     8.51, 8.52, 8.53, 8.54, 8.55, 8.56, 8.57, 8.58, 8.59, 9.00,
                     9.01, 9.02, 9.03, 9.04, 9.05, 9.06, 9.07, 9.08, 9.09, 9.10]
    p_certainty_prompt = 1


class Subsession(BaseSubsession):

    def day(self):
        if (self.round_number - 1) % 5 == 0:
            return 'Monday'
        elif (self.round_number - 1) % 5 == 1:
            return 'Tuesday'
        elif (self.round_number - 1) % 5 == 2:
            return 'Wednesday'
        elif (self.round_number - 1) % 5 == 3:
            return 'Thursday'
        else:
            return 'Friday'

    def creating_session(self):
        if self.round_number == 1:
            for p in self.get_players():
                p.participant.vars.setdefault('total_payoff', 0)


class Group(BaseGroup):
    payoff = models.CurrencyField()             # strange that I need to declare this - thought it already was

    game_lost = models.BooleanField(
        initial=False,
        doc="This will be set to true, when the game has been  \
            lost by players making the wrong choice."
    )

    def set_game_lost(self):
        self.game_lost = True

    def is_game_lost(self):
        return any(s.game_lost for s in self.in_all_rounds())

    def is_game_just_lost(self):
        return self.game_lost

    def is_game_over(self):
        """
        A convenience function to be called by pages that want to
        check whether to forward player(s) to the end of the game,
        when either they are the sole player that has finished the
        game after waiting for a partner, or when they have made
        the wrong choice (with their partner) while playing the game.
        """
        return self.is_game_lost()

    def set_payoffs(self):
        p1, p2 = self.get_players()

        # No need to check arrival time if both players went to their offices
        if p1.choice == p2.choice == 'Office':
            p1.payoff = p2.payoff = Constants.win_office
            p1.participant.vars['total_payoff'] += Constants.win_office
            p2.participant.vars['total_payoff'] += Constants.win_office

        # They both arrive before 9 and agree to go the the canteen
        elif p1.choice == p2.choice == 'Canteen' and p1.arrival_time < 9.0 and p2.arrival_time < 9.0:
            p1.payoff = p2.payoff = Constants.win_canteen
            p1.participant.vars['total_payoff'] += Constants.win_canteen
            p2.participant.vars['total_payoff'] += Constants.win_canteen

        # All other configurations result in the game being a loss
        else:
            p1.payoff = p2.payoff = - p1.participant.vars['total_payoff']
            p1.participant.vars['total_payoff'] = 0
            p2.participant.vars['total_payoff'] = 0
            self.set_game_lost()


class Player(BasePlayer):
    arrival_time = models.FloatField()

    choice = models.StringField(
        choices=['Canteen', 'Office'],
        widget=widgets.RadioSelectHorizontal()
    )

    strategy_canteen_dilemma = models.LongStringField(
        verbose_name="What strategy did you use while playing this game?",
    )

    certainty = models.StringField(
        verbose_name="On a scale from 1=very uncertainy to 6=very certain, how certain are you that your colleague has made the same choice as you?",
        choices=['1', '2', '3',
                 '4', '5', '6'],
        blank=True,
        widget=widgets.RadioSelect()
    )

    def get_partner(self):
        return self.get_others_in_group()[0]
