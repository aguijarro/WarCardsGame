import datetime
from protorpc import messages
from google.appengine.ext import ndb
from utils import Deck, Hand

# --------User Information--------- #


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)


class UserForm(messages.Message):
    """UserForm -- User outbound form message"""
    name = messages.StringField(1, required=True)
    email = messages.StringField(2, required=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)

# --------Game Information---------- #


class WarCard(ndb.Model):
    """Card object"""
    suit = ndb.StringProperty()
    rank = ndb.StringProperty()
    name = ndb.StringProperty()


class MoveHistory(ndb.Model):
    """Move History object"""
    player = ndb.StringProperty()
    computer = ndb.StringProperty()
    winner = ndb.StringProperty()

    def to_form(self):
        return MoveHistoryForm(player=self.player,
                               computer=self.computer,
                               winner=self.winner)


def _initDeck(cards_to_play):
    """ Init Deck for play"""
    deck = Deck()
    deck.shuffle()
    deck_to_play = Hand()
    deck.deal_cards(0, deck_to_play, cards_to_play)

    deck_player1 = Hand()
    deck_to_play.deal_cards(1, deck_player1, cards_to_play / 2)

    deck_player2 = Hand()
    deck_to_play.deal_cards(1, deck_player2, cards_to_play / 2)

    return deck_player1, deck_player2


class WarGame(ndb.Model):
    """Game object
        This game saved data for each player (player connected and computer)
    """
    name = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now=True, default=datetime.datetime.now())
    # Save cards which can be used to play
    deck_player_1 = ndb.StructuredProperty(WarCard, repeated=True)
    deck_player_2 = ndb.StructuredProperty(WarCard, repeated=True)
    # Save cards which were win by user during the game
    deck_win_player_1 = ndb.StructuredProperty(WarCard, repeated=True)
    deck_win_player_2 = ndb.StructuredProperty(WarCard, repeated=True)
    # Save cards when players tie
    deck_tie = ndb.StructuredProperty(WarCard, repeated=True)
    # Save history game
    game_history = ndb.StructuredProperty(MoveHistory, repeated=True)
    winner = ndb.StringProperty()
    game_over = ndb.BooleanProperty(required=True, default=False)
    user = ndb.KeyProperty(required=True, kind='User')

    @classmethod
    def new_game(cls, user, cards_to_play):
        """Creates and returns a new game"""
        if cards_to_play <= 0 and cards_to_play >= 26:
            raise ValueError('Number of cards must be between 10 and 26')

        deck_player1, deck_player2 = _initDeck(cards_to_play)

        war_deck_player1 = []
        for card in deck_player1.cards:
            x = WarCard()
            x.suit = str(card.suit)
            x.rank = str(card.rank)
            x.name = card.__str__()
            war_deck_player1.append(x)

        war_deck_player2 = []
        for cardTwo in deck_player2.cards:
            y = WarCard()
            y.suit = str(cardTwo.suit)
            y.rank = str(cardTwo.rank)
            y.name = cardTwo.__str__()
            war_deck_player2.append(y)

        game = WarGame(user=user,
                       deck_player_1=war_deck_player1,
                       deck_player_2=war_deck_player2,
                       name="Game_" + str(datetime.datetime.now()),
                       game_over=False)

        game.put()

        score = ScoreWar(user=user,
                         game=game.key,
                         score_user=0,
                         score_player_ia=0)
        score.put()
        return game

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = WarGameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.name = self.name
        form.date = str(self.date)
        form.user_name = self.user.get().name
        form.game_over = self.game_over
        form.message = message
        return form


class NewWarGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)
    cards_to_play = messages.IntegerField(2, default=10)


class WarGameForm(messages.Message):
    """WarGameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    name = messages.StringField(2, required=True)
    date = messages.StringField(3, required=True)
    game_over = messages.BooleanField(4, required=True)
    message = messages.StringField(5, required=True)
    user_name = messages.StringField(6, required=True)


class WarGameForms(messages.Message):
    """Return multiple WarGameForm"""
    items = messages.MessageField(WarGameForm, 1, repeated=True)


class WarGameMoveStatus(messages.Message):
    """Return status after each move"""
    urlsafe_key = messages.StringField(1)
    player1 = messages.StringField(2)
    valuePlayedPlayer1 = messages.StringField(3)
    player2 = messages.StringField(4)
    valuePlayedPlayer2 = messages.StringField(5)
    winnerMove = messages.StringField(6)
    game_over = messages.BooleanField(7, required=True)
    message = messages.StringField(8, required=True)

# -- Score Information -- #


class ScoreWar(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    game = ndb.KeyProperty(required=True, kind='WarGame')
    date = ndb.DateTimeProperty(auto_now=True, default=datetime.datetime.now())
    score_user = ndb.IntegerProperty(required=True)
    score_player_ia = ndb.IntegerProperty(required=True)
    won = ndb.StringProperty()

    def to_form(self):
        return ScoreWarForm(user_name=self.user.get().name,
                            user_game=str(self.game.get().key),
                            won=self.won, date=str(self.date),
                            score_user=self.score_user,
                            score_player_ia=self.score_player_ia)


class ScoreWarForm(messages.Message):
    """ScoreWarForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    user_game = messages.StringField(2, required=True)
    date = messages.StringField(3, required=True)
    score_user = messages.IntegerField(4, required=True)
    score_player_ia = messages.IntegerField(5, required=True)
    won = messages.StringField(6)


class ScoreWarForms(messages.Message):
    """Return multiple ScoreWarForms"""
    items = messages.MessageField(ScoreWarForm, 1, repeated=True)


class MoveHistoryForm(messages.Message):
    """MovieHistoryForm for outbound Score information"""
    player = messages.StringField(1, required=True)
    computer = messages.StringField(2, required=True)
    winner = messages.StringField(3, required=True)


class MoveHistoryForms(messages.Message):
    """Return multiple MovieHistoryForm"""
    winner = messages.StringField(1)
    items = messages.MessageField(MoveHistoryForm, 2, repeated=True)


class UserRankingForm(messages.Message):
    """UserRankingForm for outbound Ranking information"""
    player = messages.StringField(1)
    ranking = messages.StringField(2)


class UserRankingForms(messages.Message):
    """Return multiple UserRankingForm"""
    items = messages.MessageField(UserRankingForm, 1, repeated=True)
