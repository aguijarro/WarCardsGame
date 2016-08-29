#War Game


## Game API Project Overview:

- In the Developing Scalable Apps with Python course you learned how to write platform-agnostic apps using Google App Engine backed by Google Datastore.

- In this project you will use these skills to develop your own game! You will write an API with endpoints that will allow anyone to develop a front-end for your game. Since you aren't required to write a front-end you can use API explorer to test your API.Let's get started!

## API URL:

- http://warcards-1331.appspot.com/_ah/api/explorer

## Game Description:
- Reference: https://en.wikipedia.org/wiki/War_(card_game)

- The objective of the game is to win all cards.

- The deck is divided evenly among the players, giving each a down stack. In unison, each player reveals the top card of their deck – this is a "battle" – and the player with the higher card takes both of the cards played and moves them to their stack.

- If the two cards played are of equal value, then there is a "war". Both players place the next card of their pile face down, depending on the variant, and then another card face-up. The owner of the higher face-up card wins the war and adds all six (or ten) cards on the table to the bottom of their deck. If the face-up cards are again equal then the battle repeats with another set of face-down/up cards. This repeats until one player's face-up card is higher than their opponent's.

- Many different War games can be played by many different Users at any
given time. Each game can be retrieved or played by using the path parameter
`urlsafe_game_key`.

- In this version of the game, you always play  against computer gamer.

## Score-keeping: 

- Score is based on the cards you win after each move. For example, if your card is 7 and computer card is 6, because you have the higher card you will be earn 13 points. When in a move exists a tie, both cards and one aditionally card for each deck  will be kept for the next hand where apply the rule explain before.

## Game Instructions:

1) Register a user (create_user).
2) Created a game (new_war_game). When you create a new game you need to register the number of cards which you want to play. This value must be higher than 10 and smaller than 26. When you write a odd number, this number is replace with the following even number.
3) Make a move until the game is finish (make_move).




##Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - Design.txt: Reflect on Your Design.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - settings.py: Define environment for the app: test, production. (This variable allow to uses a set of cards define for test, or create a deck randomly).
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will
   raise a ConflictException if a User with that user_name already exists.

 - **new_war_game**
    - Path: 'gamewar'
    - Method: POST
    - Parameters: user_name, cards_to_play (This paramer allows to define the number of the deck. For example if write 10. The deck will have 10 cards. 5 for one player and 5 for other. If you write an uneven number, the app transform in pair number)
    - Returns: WarGameForm with initial game state
    - Description: Creates a new Game. user_name provided must correspond to an
    existing user - will raise a NotFoundException if not.

 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: WarGameForm with current game state.
    - Description: Returns the current state of a game.

 - **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key
    - Returns: WarGameForm with new game state.
    - Description: Returns the updated state of the game.
    If this causes a game to end, a corresponding Score entity will be created.


 - **get_user_war_games**
    - Path: 'games/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: WarGameForms.
    - Description: Returns all of a User's active games.

 - **cancel_war_game**
    - Path: 'games/user/delete/{user_name}'
    - Method: DELETE
    - Parameters: user_name, urlsafe_game_key
    - Returns: StringMessage.
    - Description: Delete a game and scores if the game is not finish.    

 - **get_user_scores**
    - Path: 'scores/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreWarForms.
    - Description: Returns all Scores recorded by the provided player order by date.
     Will raise a NotFoundException if the User does not exist.

- **get_scores**
    - Path: 'scores'
    - Method: GET
    - Parameters: user_name, urlsafe_game_key
    - Returns: ScoreWarForms.
    - Description: Return war game scores by user.     

 - **get_game_history**
    - Path: 'history/scores'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: MovieHistoryForms
    - Description: Return a 'history' of moves for each game.

 - **get_user_rankings**
    - Path: 'rankings'
    - Method: GET
    - Parameters: None
    - Returns: UserRankingForms
    - Description: Returns all players ranked by performance.    

##Models Included:

 - **User**
    - Stores unique user_name and (optional) email address.

 - **WarCard**
    - Uses to store a array of cards in WarGame Model.

 - **MoveHistory**
    - Uses to store a array of history movements in WarGame Model.

 - **WarGame**
    - Stores unique game states. Associated with User model via KeyProperty.

 - **WarGame**
    - Stores unique game states. Associated with User model via KeyProperty.

 - **ScoreWar**
    - Records completed games. Associated with Users model via KeyProperty.

 - **ScoreWar**
    - Records completed games. Associated with Users model via KeyProperty, and WarGame model via KeyProperty.  


##Forms Included:

- **UserForm**
   - Representation of a User's state (name, email).

 - **NewWarGameForm**
    - Used to create a new game (user_name, cards_to_play).

 - **WarGameForm**
    - WarGameForm for outbound game state information (urlsafe_key, name, date, game_over, message, user_name)

 - **WarGameForms**
    - Return multiple WarGameForm (WarGameForm).

 - **ScoreWarForm**
    - ScoreWarForm for outbound Score information (user_name, user_game, date, score_user, score_player_ia, won).

 - **ScoreWarForms**
    - Return multiple ScoreWarForms (ScoreWarForm).

 - **MovieHistoryForm**
    - MovieHistoryForm for outbound Score information (player, computer, winner).    

 - **MovieHistoryForms**
    - Return multiple MovieHistoryForm (MovieHistoryForm).

 - **UserRankingForm**
    - UserRankingForm for outbound Ranking information (player, ranking).    

 - **UserRankingForms**
    - Return multiple UserRankingForm (UserRankingForm).     

 - **StringMessage**
    - General purpose String container.
