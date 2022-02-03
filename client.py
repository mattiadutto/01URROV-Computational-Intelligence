#!/usr/bin/env python3

from copy import deepcopy
from sys import argv, stdout
import GameData
import socket
from constants import *
import os

import numpy as np

if len(argv) < 4:
    print("You need the player name to start the game.")
    playerName = "Test"  # For debug
    playerName = "p2"  # add by me
    ip = HOST
    port = PORT
else:
    playerName = argv[3]
    ip = argv[1]
    port = int(argv[2])

run = True

statuses = ["Lobby", "Game", "GameHint"]

status = statuses[0]

hintState = ("", "")


def manageInput():
    global run
    global status
    global command

    global myCardValues
    global playerNames
    global usedNoteTokens

    invalidCommand = True
    while run and invalidCommand:
        command = input()
        # Choose data to send
        if command == "exit":
            run = False
            os._exit(0)
        elif command == "ready" and status == statuses[0]:
            s.send(GameData.ClientPlayerStartRequest(playerName).serialize())
            # My code
            invalidCommand = False
        elif command == "show" and status == statuses[1]:
            s.send(GameData.ClientGetGameStateRequest(playerName).serialize())

            invalidCommand = False
        elif command == "":
            print("[" + playerName + " - " + status + "]: ", end="")
            invalidCommand = True
        else:
            print("Unknown command: " + command)
            continue
        stdout.flush()


numPlayer = -1
playerNames = []
userTables = np.zeros(
    4 * 5 * 4, dtype=np.int8
)  # 4 users, 5 cards per users, 4 value per card: Hint value, Hint color, Value,  color
userTables = np.reshape(userTables, (4, 5, 4))
oldUserTables = deepcopy(userTables)
table = np.zeros(
    5, dtype=np.int8
)  # Table value, 5 places, 1 value [value] if value = 0 no card
# 5 cards, 2 value per card: value, color
myCardValues = np.zeros(5 * 2, dtype=np.int8)
myCardValues = np.reshape(myCardValues, (5, 2)) - 1
discardPile = None
usedNoteTokens = None
numberOfCards = None


def colorToValue(color):
    """From color to numerical value: base on the order of the tableCards inside data"""
    if color == None:
        return -1
    if color == "red":
        return 0
    if color == "yellow":
        return 1
    if color == "green":
        return 2
    if color == "blue":
        return 3
    return 4


def valueToColor(value):
    """From numerical value to color: base on the order of the tableCards inside data"""
    if value == -1:
        return None
    if value == 0:
        return "red"
    if value == 1:
        return "yellow"
    if value == 2:
        return "green"
    if value == 3:
        return "blue"
    return "white"


def discardCard(s, cardNumber):
    global myCardValues
    global usedNoteTokens
    global playerName
    global status

    try:
        s.send(
            GameData.ClientPlayerDiscardCardRequest(playerName,
                                                    cardNumber).serialize())
        # I remove the card from the set of cards. Same procedure of the case when we play a card
        if myCardValues[cardNumber][0] > 0 or myCardValues[cardNumber][1] != -1:
            myCardValues = list(myCardValues)
            myCardValues.pop(cardNumber)  # remove the played card
            # inserted an invalid cart
            #myCardValues.insert(len(myCardValues), [-1, -1])
            myCardValues.append([-1, -1])
            # convert the list into an array
            myCardValues = np.array(myCardValues)

        if usedNoteTokens is None:
            usedNoteTokens = 1
        else:
            usedNoteTokens -= 1  # I decrease the # of used token
        return True
    except:
        print("[" + playerName + " - " + status + "]: ", end="")
        print("Maybe you wanted to type 'discard <num>'?")
        return False


def playCard(s, cardNumber):
    global myCardValues
    global playerName
    global status

    try:
        # Remove the current card from the set, I lose the information about that card
        if myCardValues[cardNumber][0] != -1 or myCardValues[cardNumber][
                1] != -1:
            myCardValues = list(myCardValues)
            myCardValues.pop(cardNumber)  # remove the played card
            # inserted an invalid cart
            #myCardValues.insert(len(myCardValues), [-1, -1])
            myCardValues.append([-1, -1])
            # convert the list into an array
            myCardValues = np.array(myCardValues)

        s.send(
            GameData.ClientPlayerPlayCardRequest(playerName,
                                                 cardNumber).serialize())
        return True
    except Exception as e:
        print(e)
        print("[" + playerName + " - " + status + "]: ", end="")
        print("Maybe you wanted to type 'play <num> '?")
        return False


def hintCards(s, t, destinationIndex, value, places=None):
    global userTables
    global usedNoteTokens
    global playerNames
    global playerName
    global status
    try:
        if t != "colour" and t != "color" and t != "value":
            print("[" + playerName + " - " + status + "]: ", end="")
            print("Error: type can be 'color' or 'value'")
            return False

        if places is None:
            places = []

        if t == "value":
            # Value
            if (playerNames.index(playerName) < destinationIndex
                    or playerNames.index(playerName) == 0):
                destinationIndex += 1
            print("[" + playerName + " - " + status + "]: ", end="")
            print(
                f"hint value {playerNames[destinationIndex]} {value} {places}")

        else:
            # Color
            for i in range(5):
                if userTables[destinationIndex][i][3] == colorToValue(value):
                    places.append(i)

            if (playerNames.index(playerName) < destinationIndex
                    or playerNames.index(playerName) == 0):
                destinationIndex += 1
            print("[" + playerName + " - " + status + "]: ", end="")
            print(
                f"hint color {playerNames[destinationIndex]} {value} {places}"
            )  # I can send a 0 and I will obtain the correct positions.

        if t == "value":
            value = int(value)
            if int(value) > 5 or int(value) < 1:
                print("[" + playerName + " - " + status + "]: ", end="")
                print("Error: card values can range from 1 to 5")
                return False
        else:
            if value not in ["green", "red", "blue", "yellow", "white"]:
                print("[" + playerName + " - " + status + "]: ", end="")
                print(
                    "Error: card color can only be green, red, blue, yellow or white"
                )
                return False
        s.send(
            GameData.ClientHintData(playerName, playerNames[destinationIndex],
                                    t, value).serialize())
        playerIndex = destinationIndex  # playerNames.index(destination)
        if (playerNames.index(playerName) < playerIndex
                or playerNames.index(playerName) == 0):
            playerIndex -= 1
        if t == "value":
            # hint value user value posOfValues
            for i in range(len(places)):
                # [player][card][hintValue]
                userTables[playerIndex][int(places[i])][0] = 1
        else:
            # hint color user color posOfColor
            for i in range(len(places)):
                # [player][card][hintColor]
                userTables[playerIndex][int(places[i])][1] = 1
        if usedNoteTokens is None:
            usedNoteTokens = 1
        else:
            usedNoteTokens += 1  # I increase the # of used token
        return True
    except:
        print("[" + playerName + " - " + status + "]: ", end="")
        print(
            "Maybe you wanted to type 'hint <type> <destinatary> <value> <pile position>'?"
        )
        return False


def suggestedMove(s):
    global numberOfCards
    global playerName
    global table
    global oldUserTables
    global userTables
    global usedNoteTokens
    global status
    # it basically do a show
    s.send(GameData.ClientGetGameStateRequest(playerName).serialize())
    data = s.recv(DATASIZE)
    data = GameData.GameData.deserialize(data)

    if not data.currentPlayer == playerName:
        return

    usedNoteTokens = data.usedNoteTokens

    numberOfCards = data.handSize

    numPlayer = len(data.players)
    if playerNames == []:
        for p in data.players:
            playerNames.append(p.name)

    oldUserTables = deepcopy(userTables)

    pi = 0  # player index
    for p in data.players:
        if p.name != playerName:
            edit = False
            for ci, c in enumerate(p.hand):
                userTables[pi][ci][2] = c.value
                userTables[pi][ci][3] = colorToValue(c.color)
                if (edit == False and any(oldUserTables[pi].flatten() > 0) and
                    (oldUserTables[pi][ci][2] != c.value
                     or oldUserTables[pi][ci][3] != colorToValue(c.color))):
                    userTables[pi] = np.concatenate((
                        userTables[pi][:ci][:],
                        userTables[pi][ci + 1:][:],
                        np.reshape([-1, -1, -1, -1], (1, 4)),
                    ))
                    if ci == 4:
                        userTables[pi][ci][2] = c.value
                        userTables[pi][ci][3] = colorToValue(c.color)
                    edit = True
            pi += 1

    # I fill also the table
    for i, (_, v) in enumerate(data.tableCards.items()):
        table[i] = len(v)

    # I fill also the discarded cards
    discardPile = None
    for _, dc in enumerate(data.discardPile):
        if discardPile is None:
            discardPile = np.reshape(
                np.array([colorToValue(dc.color), dc.value]), (1, 2))
        else:
            discardPile = np.concatenate(
                (discardPile, [[colorToValue(dc.color), dc.value]]))

    stop = False
    # If a card is already present I can discard it. I can only produce one fire per color.
    if usedNoteTokens > 0:
        for i in range(NUMBER_OF_CARD):
            # print(f"VALUE: {myCardValues[i][0]} - COLOR: {myCardValues[i][1]} - {valueToColor(myCardValues[i][1])}")
            if (myCardValues[i][0] > -1 and myCardValues[i][1] > -1
                    and myCardValues[i][0] <= table[myCardValues[i][1]]):
                print("[" + playerName + " - " + status + "]: ", end="")
                print(f"discard {i} because already present")
                if not discardCard(s, i):
                    continue
                stop = True
        # case I have 2 cards with same value of same color
        if not stop:
            for i in range(NUMBER_OF_CARD):
                for j in range(NUMBER_OF_CARD):
                    if i != j and (all(myCardValues[i] > -1) and
                                   all(myCardValues[i] == myCardValues[j])):
                        print("[" + playerName + " - " + status + "]: ",
                              end="")
                        print(
                            f"discard {i} because already present in the cards set"
                        )
                        if not discardCard(s, i):
                            continue
                        stop = True
        # add discard case in case that all cards of a value are played
        if not stop:
            for i in range(NUMBER_OF_CARD):  # I iterate over possible values
                if all(table > i):
                    for j in range(NUMBER_OF_CARD):  # I iterate over my cards
                        if myCardValues[j][0] == i:
                            print("[" + playerName + " - " + status + "]: ",
                                  end="")
                            print(
                                f"discard {i} because already present in the table set"
                            )
                            if not discardCard(s, i):
                                continue
                            stop = True
                        if stop:
                            break
                if stop:
                    break
        # discard a card because is impossible to play it
        if not stop:
            for i in range(NUMBER_OF_CARD):
                if all(myCardValues[i] > 0):
                    if (table[myCardValues[i][1]] >=
                            myCardValues[i][0]):  # case card already played
                        print("[" + playerName + " - " + status + "]: ",
                              end="")
                        print(f"discard {i} because not need any more")
                        if not discardCard(s, i):
                            continue
                        stop = True
                    # case card impossible to play
                    if stop == False and discardPile is not None:
                        checkVector = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
                        for j in range(table[myCardValues[i][1]]):
                            checkVector[j] += 1
                        for j in range(len(discardPile)):
                            if discardPile[j][0] == myCardValues[i][
                                    1] and discardPile[j][1] < myCardValues[i][
                                        0]:  # same color and value before my card
                                checkVector[discardPile[j][1]] += 1
                        if myCardValues[i][0] == 1 and checkVector[0] == 3:
                            print("[" + playerName + " - " + status + "]: ",
                                  end="")
                            print(f"discard {i} because you can't play it")
                            if not discardCard(s, i):
                                continue
                            stop = True
                        if (myCardValues[i][0] == 2 and checkVector[0] == 3
                                and checkVector[1] == 2):
                            print("[" + playerName + " - " + status + "]: ",
                                  end="")
                            print(f"discard {i} because you can't play it")
                            if not discardCard(s, i):
                                continue
                            stop = True
                        if (myCardValues[i][0] == 3 and checkVector[0] == 3
                                and checkVector[1] == 2
                                and checkVector[2] == 2):
                            print("[" + playerName + " - " + status + "]: ",
                                  end="")
                            print(f"discard {i} because you can't play it")
                            if not discardCard(s, i):
                                continue
                            stop = True
                        if (myCardValues[i][0] == 4 and checkVector[0] == 3
                                and checkVector[1] == 2 and checkVector[2] == 2
                                and checkVector[2] == 3):
                            print("[" + playerName + " - " + status + "]: ",
                                  end="")
                            print(f"discard {i} because you can't play it")
                            if not discardCard(s, i):
                                continue
                            stop = True
                if stop:
                    break
    # Play suggestion
    if stop == False:
        for i in range(NUMBER_OF_CARD):
            if sum(table) == 0 and myCardValues[i][0] == 1:
                print("[" + playerName + " - " + status + "]: ", end="")
                print(f"play {i}")
                stop = True
            elif myCardValues[i][1] != -1 and (
                (myCardValues[i][0] == 1 and table[myCardValues[i][1]] == 0) or
                (myCardValues[i][0] == (table[myCardValues[i][1]] + 1)
                 and table[myCardValues[i][1]] <= 4)):
                print("[" + playerName + " - " + status + "]: ", end="")
                print(f"play {i}")
                stop = True
            if stop:
                if not playCard(s, i):
                    continue
                break

    suggestPlayer = None
    valuePerColor = np.zeros(
        numPlayer *
        NUMBER_OF_CARD)  # NUMBER_OF_CARD in this case is NUMBER_OF_COLORS
    valuePerColor = np.reshape(valuePerColor, (numPlayer, NUMBER_OF_CARD))

    if (BLUE_TOKEN - usedNoteTokens >
            0):  # I have to check that I have 1 token available for do a Hint.
        if stop == False:
            # Hint suggestion
            # Value part
            suggestValue = None

            for i in range(numPlayer - 1):
                for v in range(NUMBER_OF_CARD):
                    for ci in range(NUMBER_OF_CARD):
                        card = userTables[i][ci]
                        if card[2] == v and card[2] > table[
                                card[3]] and card[0] != 1:
                            suggestPlayer = i
                            suggestValue = v
                        if suggestPlayer is not None:
                            break
                    if suggestPlayer is not None:
                        break
                if suggestPlayer is not None:
                    break

            suggestHintValues = []
            for i in range(5):
                if (suggestPlayer is not None and suggestValue is not None
                        and userTables[suggestPlayer][i][2] == suggestValue):
                    suggestHintValues.append(i)

            # Color part
            for pi in range(numPlayer - 1):  # for each player
                for ci in range(NUMBER_OF_CARD):  # for each card
                    # we count the # of card of that colour.
                    if (
                            userTables[pi][ci][1] != 1
                    ):  # if the card color is already hinted we don't add to the sum.
                        valuePerColor[pi][userTables[pi][ci][3]] += 1
            hintPlayers, hintColorValues = np.where(
                valuePerColor == np.max(valuePerColor))
            hintPlayer, hintColor = (
                hintPlayers[0],
                hintColorValues[0],
            )  # I have to take only the first case

            if suggestPlayer is not None and hintPlayer is not None:
                if np.count_nonzero(
                        userTables[hintPlayer][:, 2] ==
                        suggestValue) >= np.count_nonzero(
                            userTables[suggestPlayer][:, 3] == hintColor):
                    # hint value
                    hintCards(s, "value", hintPlayer, suggestValue,
                              suggestHintValues)
                    stop = True
                else:
                    # hint color
                    hintCards(s, "color", suggestPlayer,
                              valueToColor(hintColor))
                    stop = True
            else:
                if (
                        stop == False and
                        valuePerColor[hintPlayer, hintColor] > table[hintColor]
                        and np.max(valuePerColor) != 0
                ):  # I suggest the color if # of color of that color is grater then the # of card in the table
                    if hintPlayer is not None:
                        hintCards(s, "color", hintPlayer,
                                  valueToColor(hintColor))
                        stop = True
                elif stop == False:
                    if suggestPlayer is not None:
                        hintCards(s, "value", suggestPlayer, suggestValue,
                                  suggestHintValues)
                        stop = True
    # Discard part
    if (usedNoteTokens > 0 and stop == False and suggestPlayer is None
            and np.max(valuePerColor) == 0):
        cardsValue = myCardValues[:, 0]
        min = None
        minI = None
        for i in range(NUMBER_OF_CARD):
            if min is None or (cardsValue[i] < min and cardsValue[i] > 0):
                min = cardsValue[i]
                minI = i
        if minI is not None:
            print("[" + playerName + " - " + status + "]: ", end="")
            print(f"discard {minI}")
            discardCard(s, minI)


def computeScore(table):
    return np.sum(table)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    request = GameData.ClientPlayerAddData(playerName)
    s.connect((HOST, PORT))
    s.send(request.serialize())
    data = s.recv(DATASIZE)
    data = GameData.GameData.deserialize(data)
    if type(data) is GameData.ServerPlayerConnectionOk:
        print("Connection accepted by the server. Welcome " + playerName)
    print("[" + playerName + " - " + status + "]: ", end="")
    first = True
    firstIteration = True
    while run:
        dataOk = False
        if first:
            manageInput()
            first = False
            data = None
            continue
        data = s.recv(DATASIZE)
        if not data:
            continue
        data = GameData.GameData.deserialize(data)

        if type(data) is GameData.ServerPlayerStartRequestAccepted:
            dataOk = True

            numPlayer = data.connectedPlayers - 1  # I don't consider my self a player

            print("Ready: " + str(data.acceptedStartRequests) + "/" +
                  str(data.connectedPlayers) + " players")
            data = s.recv(DATASIZE)
            data = GameData.GameData.deserialize(data)
        if type(data) is GameData.ServerStartGameData:
            dataOk = True

            for pn in data.players:
                if pn not in playerNames:
                    playerNames.append(pn)

            print("Game start!")
            s.send(GameData.ClientPlayerReadyData(playerName).serialize())
            status = statuses[1]

            if data.players[0] == playerName:
                suggestedMove(s)

        if type(data) is GameData.ServerGameStateData:
            dataOk = True
            print("Current player: " + data.currentPlayer)
            print("Player hands: ")
            for p in data.players:
                print(p.toClientString())
            print("Cards in your hand: " + str(data.handSize))
            print("Table cards: ")
            for pos in data.tableCards:
                print(pos + ": [ ")
                for c in data.tableCards[pos]:
                    print(c.toClientString() + " ")
                print("]")
            print("Discard pile: ")
            for c in data.discardPile:
                print("\t" + c.toClientString())
            print("Note tokens used: " + str(data.usedNoteTokens) + "/8")
            print("Storm tokens used: " + str(data.usedStormTokens) + "/3")

            if data.currentPlayer == playerName:
                suggestedMove(s)
                print("[" + playerName + " - " + status + "]: ", end="")

        if type(data) is GameData.ServerActionInvalid:
            dataOk = True
            print("Invalid action performed. Reason:")
            print(data.message)
        if type(data) is GameData.ServerActionValid:
            dataOk = True
            print("Action valid!")
            print("Current player: " + data.player)

            if playerName == data.player:
                suggestedMove(s)
                print("[" + playerName + " - " + status + "]: ", end="")

        if type(data) is GameData.ServerPlayerMoveOk:
            dataOk = True
            print("Nice move!")
            print("Current player: " + data.player)

            if playerName == data.player:
                suggestedMove(s)
                print("[" + playerName + " - " + status + "]: ", end="")

        if type(data) is GameData.ServerPlayerThunderStrike:
            dataOk = True
            print("OH NO! The Gods are unhappy with you!")

            if playerName == data.player:
                suggestedMove(s)
                print("[" + playerName + " - " + status + "]: ", end="")

        if type(data) is GameData.ServerHintData:
            dataOk = True
            print("Hint type: " + data.type)
            print("Player " + data.destination + " cards with value " +
                  str(data.value) + " are:")
            for i in data.positions:
                print("\t" + str(i))
            # Add info to my table about my cards
            if playerName == data.destination:
                for i in data.positions:
                    if data.type == "value":
                        # case value
                        myCardValues[i][0] = data.value
                    else:
                        # case color
                        myCardValues[i][1] = colorToValue(str(data.value))
                # After a hint is good to have a suggestion
                suggestedMove(s)
                print("[" + playerName + " - " + status + "]: ", end="")
            else:
                posPlayer = playerNames.index(data.destination)
                if playerNames.index(playerName) < posPlayer:
                    posPlayer -= 1

                for i in data.positions:
                    if data.type == "value":
                        userTables[posPlayer][i][0] = 1
                    else:
                        userTables[posPlayer][i][1] = 1
                if data.player == playerName:
                    suggestedMove(s)

        if type(data) is GameData.ServerInvalidDataReceived:
            dataOk = True
            print(data.data)
        if type(data) is GameData.ServerGameOver:
            dataOk = True
            print(data.message)
            print(data.score)
            print(data.scoreMessage)
            stdout.flush()
            run = False
            print("Ready for a new game!")

        if not dataOk:
            print("Unknown or unimplemented data type: " + str(type(data)))
