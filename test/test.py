def initDataPlayer(z, z1, z2, z3, z4, war_deck_player1):
    """ Define static data for any register user. This data is just for test"""
    z.suit = '1'
    z.rank = '6'
    z.name = '6 of Diamonds'

    z1.suit = '2'
    z1.rank = '11'
    z1.name = 'Jack of Hearts'

    z2.suit = '1'
    z2.rank = '9'
    z2.name = '9 of Diamonds'

    z3.suit = '1'
    z3.rank = '12'
    z3.name = '12 of Diamonds'

    z4.suit = '1'
    z4.rank = '7'
    z4.name = '7 of Diamonds'

    war_deck_player1.append(z)
    war_deck_player1.append(z1)
    war_deck_player1.append(z2)
    war_deck_player1.append(z3)
    war_deck_player1.append(z4)

    return war_deck_player1


def initDataPlayerIA(u, u1, u2, u3, u4, war_deck_player2):
    """ Define static data for computer user. This data is just for test"""
    u.suit = '1'
    u.rank = '5'
    u.name = '5 of Diamonds'

    u1.suit = '1'
    u1.rank = '3'
    u1.name = '3 of Hearts'

    u2.suit = '1'
    u2.rank = '9'
    u2.name = '9 of Diamonds'

    u3.suit = '1'
    u3.rank = '11'
    u3.name = '11 of Diamonds'

    u4.suit = '1'
    u4.rank = '9'
    u4.name = '9 of Diamonds'

    war_deck_player2.append(u)
    war_deck_player2.append(u1)
    war_deck_player2.append(u2)
    war_deck_player2.append(u3)
    war_deck_player2.append(u4)

    return war_deck_player2

#        if settings.ENVIRONMENT == 'Test':
#
#            z = WarCard()
#            z1 = WarCard()
#            z2 = WarCard()
#            z3 = WarCard()
#            z4 = WarCard()
#            war_deck_player1 = []

#            u = WarCard()
#            u1 = WarCard()
#            u2 = WarCard()
#            u3 = WarCard()
#            u4 = WarCard()
#            war_deck_player2 = []

#            war_deck_player1 = initDataPlayer(z, z1, z2, z3,
#                                              z4, war_deck_player1)
#            war_deck_player2 = initDataPlayerIA(u, u1, u2,
#                                                u3, u4, war_deck_player2)
#        else:
