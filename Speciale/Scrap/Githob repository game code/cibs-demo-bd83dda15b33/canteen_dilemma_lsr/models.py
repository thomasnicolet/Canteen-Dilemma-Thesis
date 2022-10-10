from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import math

author = 'Robin Engelhardt'

doc = """
Thomas Bolanders cooperative Canteen Dilemma with a
logarithmic scoring rule.
"""

class Constants(BaseConstants):
    name_in_url = 'canteen_dilemma_lsr'
    players_per_group = 2
    num_rounds = 10
    endowment = c(10)
    win_canteen = c(0.06)
    win_office = c(0.04)
    instructions_template = 'canteen_dilemma_lsr/Instructions.html'
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


class Group(BaseGroup):
    payoff = models.CurrencyField()
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
        """
        Using the logarithmic scoring rule, calculated as the logarithm
        of the probability estimate for the actual outcome. That is, a
        prediction of 80% that correctly proved true would receive a score
        of ln(0.8) = -0.22. This same prediction also assigns 20%.
        likelihood to the opposite case, and so if the prediction proves
        false, it would receive a score based on the 20%: ln(0.2) = -1.6.
        The goal of a player is to maximize the score (minimize loss) and
        for the score to be as large as possible. Formally, the score can be
        calculated as S_i(p_i,x) = xln(p_i) + (1-x)ln(1-p_i), where x is 1
        or 0 (depending on whether players agree or not) and p is player
        i's propability that x will happen.
        """
        p1, p2 = self.get_players()

        # # end the game if someone goes to the wrong place at the wrong time
        # if (p1.choice is True and p1.arrival_time >= 9.0) or \
        #    (p2.choice is True and p2.arrival_time >= 9.0):
        #     p1.payoff = -10
        #     p2.payoff = -10
        #     self.set_game_lost()
        # elif (p1.choice is False and p1.arrival_time < 9.0) or \
        #      (p2.choice is False and p2.arrival_time < 9.0):
        #     p1.payoff = -10
        #     p2.payoff = -10
        #     self.set_game_lost()
        #
        # # If they agree (x=1) we get S=ln(p)
        # elif p1.choice == p2.choice:
        #     p1.payoff = math.log(p1.certainty)
        #     p2.payoff = math.log(p2.certainty)
        #
        # # if they disagree (x=0) we get S= ln(1-p)
        # else:
        #     p1.payoff = math.log(1 - p1.certainty)
        #     p2.payoff = math.log(1 - p2.certainty)

        # Going to their offices
        if p1.choice == p2.choice is False:
            p1.payoff = 2 * math.log(p1.certainty)
            p2.payoff = 2 * math.log(p2.certainty)

        # Going to the canteen
        elif p1.choice == p2.choice is True and p1.arrival_time < 9.0 and p2.arrival_time < 9.0:
            p1.payoff = math.log(p1.certainty)
            p2.payoff = math.log(p2.certainty)

        # All other configurations result in the game being a loss
        else:
            p1.payoff = 2 * math.log(1 - p1.certainty)
            p2.payoff = 2 * math.log(1 - p2.certainty)

        # if a player has lost all her money the game ends
        if p1.participant.payoff < -10.0 or p2.participant.payoff < -10.0:
            self.set_game_lost()


class Player(BasePlayer):
    arrival_time = models.FloatField()
    choice = models.BooleanField(
        choices=[
                    [True, 'Canteen'],
                    [False, 'Office'],
                ],
        widget=widgets.RadioSelectHorizontal()
    )

    strategy_canteen_dilemma = models.TextField(
        verbose_name="What strategy did you use while playing this game?",
    )

    certainty = models.FloatField(
        verbose_name="How certain are you that your colleague has made the same \
                      choice as you?",
        choices=[
                    [0.5, '50 %'],
                    [0.6, '60 %'],
                    [0.7, '70 %'],
                    [0.8, '80 %'],
                    [0.9, '90 %'],
                    [0.99, '99 %'],
                ],
        blank=True,
        widget=widgets.RadioSelect()
    )

    def get_partner(self):
        return self.get_others_in_group()[0]
