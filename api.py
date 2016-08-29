import endpoints
import utils

from protorpc import messages
from protorpc import message_types
from protorpc import remote

from models import (
    User, UserForm, StringMessage,
    WarGameForm, WarGameForms, WarGame, NewWarGameForm, ScoreWar,
    ScoreWarForms, MoveHistory, MoveHistoryForms,
    UserRankingForm, UserRankingForms, WarGameMoveStatus
)


GET_GAME_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1),)

MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1),)

USER_REQUEST = endpoints.ResourceContainer(
    user_name=messages.StringField(1),)

USER_GAME_REQUEST = endpoints.ResourceContainer(
    user_name=messages.StringField(1),
    urlsafe_game_key=messages.StringField(2),)


@endpoints.api(name='warcards', version='v1')
class WarcardsApi(remote.Service):

    # ---------User Information-----------

    @endpoints.method(request_message=UserForm,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.name).get():
            raise endpoints.ConflictException(
                'A User with that namealready exists!')
        user = User(name=request.name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(request.name))


# ---------Game Information-----------

    @endpoints.method(request_message=NewWarGameForm,
                      response_message=WarGameForm,
                      path='gamewar',
                      name='new_war_game',
                      http_method='POST')
    def new_war_game(self, request):
        """Create a new War Game"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')
        try:
            game = WarGame.new_game(user.key, request.cards_to_play)

        except ValueError:
            raise endpoints.BadRequestException('Error!')
        return game.to_form('Good luck playing War game')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=WarGameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_war_game(self, request):
        """Return the current game state."""
        game = utils.get_by_urlsafe(request.urlsafe_game_key, WarGame)
        if game:
            return game.to_form('Time to play!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    def _getScore(self, p_deck, p_winDeck):
        """ Return score per user per deck """
        score = 0
        if len(p_deck) > 0:
            for deck in p_deck:
                score += int(deck.rank)
        if len(p_winDeck) > 0:
            for winDeck in p_winDeck:
                score += int(winDeck.rank)
        return score

    def _refillDeck(self, p_deck, p_winDeck):
        """Refill deck with win cards if the principal deck is empty """
        if len(p_deck) == 0 and len(p_winDeck) > 0:
            deck = p_winDeck
            winDeck = []
            return deck, winDeck
        deck = p_deck
        winDeck = p_winDeck
        return deck, winDeck

    def _getWinner(self, p_deck1, p_player1, p_deck2):
        """Return Winner """
        if len(p_deck1) > len(p_deck2):
            return p_player1
        else:
            return "Computer"

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=WarGameMoveStatus,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_war_move(self, request):
        """Makes a move. Returns a game state with message"""
        game = utils.get_by_urlsafe(request.urlsafe_game_key, WarGame)
        user = User.query(User.key == game.user).get()
        warGameMoveStatus = WarGameMoveStatus()

        if game.game_over:
            return WarGameMoveStatus(game_over=True,
                                     message="Game is over!!!")

        score = ScoreWar.query(ScoreWar.game == game.key).get()

        # Verify if deck has carts. If not verify if each player
        # has win cards to move to the principal deck

        if len(game.deck_player_1) == 0:
            game.deck_player_1 = game.deck_win_player_1
            game.deck_win_player_1 = []

        if len(game.deck_player_2) == 0:
            game.deck_player_2 = game.deck_win_player_2
            game.deck_win_player_2 = []

        # get cards for play
        card1 = game.deck_player_1.pop(0)
        card2 = game.deck_player_2.pop(0)

        # Evaluated if the player register card is higher than computer card
        if int(card1.rank) > int(card2.rank):
            game.deck_win_player_1.append(card1)
            game.deck_win_player_1.append(card2)

            # Evaluated if exists cards in tie deck
            if len(game.deck_tie) > 0:
                for tie_card in game.deck_tie:
                    game.deck_win_player_1.append(tie_card)
                game.deck_tie = []

            # Save history game
            history = MoveHistory()
            history.player = 'Player: {} - Card: {}'.format(
                user.name,
                card1.rank)
            history.computer = 'Computer - Card: {}'.format(card2.rank)
            history.winner = 'Winner: {} - {}'.format(user.name, card1.rank)
            game.game_history.append(history)

            # Save score game
            score.score_user = self._getScore(game.deck_player_1,
                                              game.deck_win_player_1)
            score.score_player_ia = self._getScore(game.deck_player_2,
                                                   game.deck_win_player_2)

            warGameMoveStatus.urlsafe_key = request.urlsafe_game_key
            warGameMoveStatus.player1 = user.name
            warGameMoveStatus.valuePlayedPlayer1 = card1.rank
            warGameMoveStatus.player2 = 'Computer'
            warGameMoveStatus.valuePlayedPlayer2 = card2.rank
            warGameMoveStatus.winnerMove = user.name

        # Evaluated if the computer card is higher than
        # the player register card
        elif int(card1.rank) < int(card2.rank):
            game.deck_win_player_2.append(card1)
            game.deck_win_player_2.append(card2)

            # Evaluated if exists cards in tie deck
            if len(game.deck_tie) > 0:
                for tie_card in game.deck_tie:
                    game.deck_win_player_2.append(tie_card)
                game.deck_tie = []

            # Save history game
            history = MoveHistory()
            history.player = 'Player: {} - Card: {}'.format(
                user.name, card1.rank)
            history.computer = 'Computer - Card: {}'.format(card2.rank)
            history.winner = 'Winner: Computer - {}'.format(card2.rank)
            game.game_history.append(history)

            # Save score game
            score.score_user = self._getScore(game.deck_player_1,
                                              game.deck_win_player_1)
            score.score_player_ia = self._getScore(game.deck_player_2,
                                                   game.deck_win_player_2)

            warGameMoveStatus.urlsafe_key = request.urlsafe_game_key
            warGameMoveStatus.player1 = user.name
            warGameMoveStatus.valuePlayedPlayer1 = card1.rank
            warGameMoveStatus.player2 = 'Computer'
            warGameMoveStatus.valuePlayedPlayer2 = card2.rank
            warGameMoveStatus.winnerMove = 'Computer'

        else:
            # add cards to deck_tie for the next move
            game.deck_tie.append(card1)
            game.deck_tie.append(card2)

            # Refill decks if they are not have cards
            deck_player_1, deck_win_player_1 = self._refillDeck(
                game.deck_player_1,
                game.deck_win_player_1)

            deck_player_2, deck_win_player_2 = self._refillDeck(
                game.deck_player_2,
                game.deck_win_player_2)

            # Take one card for each player to add the
            # deck_tie for the next move
            if len(deck_player_1) > 0 and len(deck_player_2) > 0:
                game.deck_tie.append(deck_player_1.pop(0))
                game.deck_tie.append(deck_player_2.pop(0))

            # Update player decks
            game.deck_player_1 = deck_player_1
            game.deck_win_player_1 = deck_win_player_1
            game.deck_player_2 = deck_player_2
            game.deck_win_player_2 = deck_win_player_2

            # Save history game
            history = MoveHistory()
            history.player = 'Player: {} - Card: {}'.format(
                user.name,
                card1.rank)
            history.computer = 'Computer - Card: {}'.format(card2.rank)
            history.winner = 'Tie'
            game.game_history.append(history)

            warGameMoveStatus.urlsafe_key = request.urlsafe_game_key
            warGameMoveStatus.player1 = user.name
            warGameMoveStatus.valuePlayedPlayer1 = card1.rank
            warGameMoveStatus.player2 = 'Computer'
            warGameMoveStatus.valuePlayedPlayer2 = card2.rank
            warGameMoveStatus.winnerMove = 'Tie'

        # Save the winner and change the status of the game
        if len(game.deck_player_1) + len(game.deck_win_player_1) == 0 or len(game.deck_player_2) + len(game.deck_win_player_2) == 0:
            game.winner = self._getWinner(
                game.deck_player_1,
                user.name,
                game.deck_win_player_2)
            game.game_over = True
            # Save values to show in response when the game is not over

        # Save values to show in response when the game is not over
        warGameMoveStatus.game_over = False
        warGameMoveStatus.message = "Keep playing!!!"

        # save score and game
        score.put()
        game.put()

        return warGameMoveStatus

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=WarGameForms,
                      path='games/user/{user_name}',
                      name='get_user_war_games',
                      http_method='GET')
    def get_user_war_games(self, request):
        """Returns all of a User's active games"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')
        games = WarGame.query(WarGame.user == user.key,
                              WarGame.game_over == False)
        games.order(WarGame.date)
        return WarGameForms(items=[game.to_form("Activate Game")
                                   for game in games])

    @endpoints.method(request_message=USER_GAME_REQUEST,
                      response_message=StringMessage,
                      path='games/user/delete/{user_name}',
                      name='cancel_war_game',
                      http_method='DELETE')
    def cancel_war_game(self, request):
        """Cancel war games"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')

        game = utils.get_by_urlsafe(request.urlsafe_game_key, WarGame)

        if not game:
            raise endpoints.NotFoundException(
                'A Game with that key does not exist!')

        if game.game_over is False:

            score = ScoreWar.query(ScoreWar.game == game.key).get()
            score.key.delete()

            game.key.delete()
            msg = "Game {} deleted".format(request.urlsafe_game_key)
            return StringMessage(message=msg)

        msg = "This game {} could not be deleted".format(
            request.urlsafe_game_key)
        return StringMessage(message=msg)

# ---------Score Information-----------

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreWarForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_war_user_scores(self, request):
        """Returns all of an individual User's scores"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')
        scores = ScoreWar.query(ScoreWar.user == user.key)
        scores = scores.order(-ScoreWar.date)
        return ScoreWarForms(items=[score.to_form() for score in scores])

    @endpoints.method(request_message=USER_GAME_REQUEST,
                      response_message=ScoreWarForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_war_scores(self, request):
        """Return war game scores by user"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')
        game = utils.get_by_urlsafe(request.urlsafe_game_key, WarGame)

        if game.game_over:
            return game.to_form('Game already over!')

        scores = ScoreWar.query(ScoreWar.user == user.key,
                                ScoreWar.game == game.key)
        scores = scores.order(-ScoreWar.date)
        return ScoreWarForms(items=[score.to_form() for score in scores])

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=MoveHistoryForms,
                      path='history/scores',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Users see a 'history' of moves for each game"""
        game = utils.get_by_urlsafe(request.urlsafe_game_key, WarGame)
        if not game:
            raise endpoints.NotFoundException('Game not found!')

        return MoveHistoryForms(winner=game.winner, items=[history.to_form()
                                for history in game.game_history])

    def _getMatches(self, p_user):
        """Return the number of matches by user """
        if p_user == 'Computer':
            matches = WarGame.query().fetch()
        else:
            user = User.query(User.name == p_user).get()
            if user:
                matches = WarGame.query(WarGame.user == user.key).fetch()
            else:
                return 0
        return len(matches)

    def _getWinners(self, p_user):
        """Return the match winners by user """
        matches = WarGame.query(WarGame.winner == p_user).fetch()
        return len(matches)

    @endpoints.method(request_message=message_types.VoidMessage,
                      response_message=UserRankingForms,
                      path='rankings',
                      name='get_user_ranking',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Returns all players ranked by performance"""

        game = WarGame.query(projection=[WarGame.winner], distinct=True)

        if not game:
            raise endpoints.NotFoundException('There are not finish games')

        rankings = []
        for user in game:
            if user.winner:
                userRanking = UserRankingForm()
                userRanking.player = user.winner
                if int(self._getMatches(user.winner)) == 0:
                    userRanking.ranking = '0'
                else:
                    userRanking.ranking = str(round(
                        float(self._getWinners(user.winner)) /
                        float(self._getMatches(user.winner)), 4))
                rankings.append(userRanking)

        return UserRankingForms(items=[ranking for ranking in rankings])


app = endpoints.api_server([WarcardsApi])
