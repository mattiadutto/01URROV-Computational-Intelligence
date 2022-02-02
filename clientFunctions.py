import numpy as np

from random import randint

def generateCards():
    """
    It generate all 50 cards of the game and it return it as a list
    """
    cards = list()
    for colour in range(5):
        cards.append([1, colour])
        cards.append([1, colour])
        cards.append([1, colour])
        cards.append([2, colour])
        cards.append([2, colour])
        cards.append([3, colour])
        cards.append([3, colour])
        cards.append([4, colour])
        cards.append([4, colour])
        cards.append([5, colour])
    return cards

def possibleCards(userTables, myTable, discardPile, table):
    """
    from all possible cards (allCards) it remove the already present in other player 
    @userTables, I also remove the all hinted card from the @myTable

    return: all valid cards as an array

    """
    allCards = generateCards()
    userCards = list([c[0:2] for u in userTables for c in u])

    for c in userCards:
        allCards.remove(c)

    for c in list([c[0:2] for c in myTable]):
        if -1 not in c:
            allCards.remove(c)

    for c in discardPile:
        allCards.remove(c)

    for index, v in enumerate(table):
        for c in range(v):
            allCards.remove([c, index]) # I remove the card with value = c and color = index

    #allCards = np.array(allCards)
    usedFlag = -np.ones((len(allCards), 1))
    allCards = np.hstack((allCards, usedFlag))
    return allCards

def addHalfCard(cards, completeCards, card, flagColorValue):
    """
    cards: list of all cards that are not used
    completeCards: valid cards
    card: card that I have to complete
    flagColorValue: 0 -> I have to find a valid value
                    1 -> I have to find a valid color
    """
    while card[flagColorValue] == -1:
        card[flagColorValue] = randint(0, 4)
        if card in np.array([c[0:2] for c in cards]):
            # We have to mark the card used
            for c in cards:
                if np.array_equal(c[0:2], card):
                    if c[2] == -1:
                        c[2] = 1
                        completeCards.append(card)
                        break
                    else:
                        card[flagColorValue] = -1
                else:
                    continue

def addCard(cards, completeCards):
    """
    cards: all possible cards
    completeCards: valid cards for the mtcs
    """
    # I select a not used card
    cardIndex = randint(0, len(cards) - 1)
    print(cardIndex)
    while cards[cardIndex][2] != -1:
        cardIndex = randint(0, len(cards) - 1)
    cards[cardIndex][2] = 1
    completeCards.append(cards[cardIndex][0:2]) # I append a valid card

def completeHand(userTables, myTable, discardPile, table):
    """
    userTables: table of cards of all users except local player
    myTable: table of cards of local player

    return: Completed hand as an array
    """
    cards = possibleCards(userTables, myTable, discardPile, table)
    completeCards = list()

    # Before I manage all cards for one I only know the color, after the one that I know the value and finally I manage cards that I don't know both value and color
    for c in myTable:
        tmp = c[0:2]
        if -1 not in tmp:
            completeCards.append(tmp)
        elif tmp[0] == -1 and tmp[1] != -1:
            # we have to select a value
            addHalfCard(cards, completeCards, tmp, 0)

    for c in myTable:  
        tmp = c[0:2]     
        if tmp[1] == -1 and tmp[0] != -1:
            # we have to select a color
            addHalfCard(cards, completeCards, tmp, 1)

    for c in myTable:
        if np.array_equal(c[0:2], [-1, -1]):
            # we have to select a card
            addCard(cards, completeCards)
   
    # print(cards)
    # print(myTable)
    # print(np.array(completeCards))
    return np.array(completeCards)
