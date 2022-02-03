#!/usr/bin/env python3

from copy import deepcopy
from glob import glob
from sys import argv, stdout
from threading import Thread
import GameData
import socket
from constants import *
import os

# My code
import numpy as np

import clientFunctions as cf

if len(argv) < 4:
    print("You need the player name to start the game.")
    #exit(-1)
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

    # My code
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
            # My code
            invalidCommand = False
        elif command == "":
            print("[" + playerName + " - " + status + "]: ", end="")
            invalidCommand = True
        else:
            print("Unknown command: " + command)
            continue
        stdout.flush()
        """
        elif command.split(" ")[0] == "discard" and status == statuses[1]:
            try:
                cardStr = command.split(" ")
                cardOrder = int(cardStr[1])
                s.send(GameData.ClientPlayerDiscardCardRequest(playerName, cardOrder).serialize())
                # My code
                # I remove the card from the set of cards. Same procedure of the case when we play a card
                if myCardValues[cardOrder][0] != -1 or myCardValues[cardOrder][1] != -1:
                    myCardValues = list(myCardValues)
                    myCardValues.pop(cardOrder) #remove the played card
                    myCardValues.insert(len(myCardValues), [-1, -1]) # inserted an invalid cart
                    myCardValues = np.array(myCardValues) # convert the list into an array

                usedNoteTokens -= 1 # I decrease the # of used token

                invalidCommand = False
            except:
                print("Maybe you wanted to type 'discard <num>'?")
                continue
        elif command.split(" ")[0] == "play" and status == statuses[1]:
            try:
                cardStr = command.split(" ")
                cardOrder = int(cardStr[1])
                
                # My code: remove the current card from the set, I lose the information about that card
                if myCardValues[cardOrder][0] != -1 or myCardValues[cardOrder][1] != -1:
                    myCardValues = list(myCardValues)
                    myCardValues.pop(cardOrder) #remove the played card
                    myCardValues.insert(len(myCardValues), [-1, -1]) # inserted an invalid cart
                    myCardValues = np.array(myCardValues) # convert the list into an array

                s.send(GameData.ClientPlayerPlayCardRequest(playerName, cardOrder).serialize())
                # My code
                invalidCommand = False
            except Exception as e:
                print(e)
                print("Maybe you wanted to type 'play <num> '?")
                continue
        elif command.split(" ")[0] == "hint" and status == statuses[1]:
            try:
                destination = command.split(" ")[2]
                t = command.split(" ")[1].lower()
                if t != "colour" and t != "color" and t != "value":
                    print("Error: type can be 'color' or 'value'")
                    continue
                value = command.split(" ")[3].lower()
                if t == "value":
                    value = int(value)
                    if int(value) > 5 or int(value) < 1:
                        print("Error: card values can range from 1 to 5")
                        continue
                else:
                    if value not in ["green", "red", "blue", "yellow", "white"]:
                        print("Error: card color can only be green, red, blue, yellow or white")
                        continue
                s.send(GameData.ClientHintData(playerName, destination, t, value).serialize())
                # My code
                posLength = len(command.split(" "))
                arguments = command.split(" ")
                playerIndex = playerNames.index(destination)
                if t == "value":
                    # hint value user value posOfValues
                    for i in range(posLength - 4):
                        # [player][card][hintValue]
                        userTables[playerIndex][int(arguments[i+4])][0] = 1
                else:
                    # hint color user color posOfColor
                    for i in range(posLength - 4):
                        # [player][card][hintColor]
                        userTables[playerIndex][int(arguments[i+4])][1] = 1
                
                usedNoteTokens += 1 # I increase the # of used token
                
                invalidCommand = False
            except:
                print("Maybe you wanted to type 'hint <type> <destinatary> <value> <pile position>'?")
                continue
        elif command == "":
            print("[" + playerName + " - " + status + "]: ", end="")
            invalidCommand = True
        else:
            print("Unknown command: " + command)
            continue
        stdout.flush()
        """


# My code

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
myCardValues = np.zeros(
    5 * 2, dtype=np.int8)  #5 cards, 2 value per card: value, color
myCardValues = np.reshape(myCardValues, (5, 2)) - 1
discardPile = None
usedNoteTokens = None
numberOfCards = None


def colorToValue(color):
    # base on the order of the tableCards inside data
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
    try:
        s.send(
            GameData.ClientPlayerDiscardCardRequest(playerName,
                                                    cardNumber).serialize())
        # My code
        # I remove the card from the set of cards. Same procedure of the case when we play a card
        if myCardValues[cardNumber][0] != -1 or myCardValues[cardNumber][
                1] != -1:
            myCardValues = list(myCardValues)
            myCardValues.pop(cardNumber)  #remove the played card
            myCardValues.insert(len(myCardValues),
                                [-1, -1])  # inserted an invalid cart
            myCardValues = np.array(
                myCardValues)  # convert the list into an array

        if usedNoteTokens is None:
            usedNoteTokens = 1
        else:
            usedNoteTokens -= 1  # I decrease the # of used token
        return True
    except:
        print("Maybe you wanted to type 'discard <num>'?")
        return False


def playCard(s, cardNumber):
    global myCardValues
    try:
        # My code: remove the current card from the set, I lose the information about that card
        if myCardValues[cardNumber][0] != -1 or myCardValues[cardNumber][
                1] != -1:
            myCardValues = list(myCardValues)
            myCardValues.pop(cardNumber)  #remove the played card
            myCardValues.insert(len(myCardValues),
                                [-1, -1])  # inserted an invalid cart
            myCardValues = np.array(
                myCardValues)  # convert the list into an array

        s.send(
            GameData.ClientPlayerPlayCardRequest(playerName,
                                                 cardNumber).serialize())
        return True
    except Exception as e:
        print(e)
        print("Maybe you wanted to type 'play <num> '?")
        return False


def hintCards(s, t, destination, value, places=None):
    global userTables
    global usedNoteTokens
    try:
        if t != "colour" and t != "color" and t != "value":
            print("Error: type can be 'color' or 'value'")
            #return False
            return False
        if t == "value":
            value = int(value)
            if int(value) > 5 or int(value) < 1:
                print("Error: card values can range from 1 to 5")
                return False
        else:
            if value not in ["green", "red", "blue", "yellow", "white"]:
                print(
                    "Error: card color can only be green, red, blue, yellow or white"
                )
                return False
        s.send(
            GameData.ClientHintData(playerName, destination, t,
                                    value).serialize())
        # My code
        #posLength = len(command.split(" "))
        #arguments = places #command.split(" ")
        playerIndex = playerNames.index(destination)
        if playerNames.index(playerName) < playerIndex or playerNames.index(
                playerName) == 0:
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
    # it basically do a show
    s.send(GameData.ClientGetGameStateRequest(playerName).serialize())
    data = s.recv(DATASIZE)
    data = GameData.GameData.deserialize(data)

    if not data.currentPlayer == playerName:
        return

    usedNoteTokens = data.usedNoteTokens
    #playerNames = []

    numberOfCards = data.handSize

    numPlayer = len(data.players)
    if playerNames == []:
        for p in data.players:
            playerNames.append(p.name)

    oldUserTables = deepcopy(userTables)

    pi = 0  # player index
    for p in data.players:
        #playerNames.append(p.name)
        if p.name != playerName:
            edit = False
            for ci, c in enumerate(p.hand):
                userTables[pi][ci][2] = c.value
                userTables[pi][ci][3] = colorToValue(c.color)
                if edit == False and any(oldUserTables[pi].flatten() > 0) and (
                        oldUserTables[pi][ci][2] != c.value
                        or oldUserTables[pi][ci][3] != colorToValue(c.color)):
                    #userTables[pi] = np.concatenate((userTables[pi][:ci], userTables[pi][ci+1:], np.array(np.reshape([-1, -1, c.value, colorToValue(c.color)], (1,4)))))
                    userTables[pi] = np.concatenate(
                        (userTables[pi][:ci][:], userTables[pi][ci + 1:][:],
                         np.reshape([-1, -1, -1, -1], (1, 4))))
                    if ci == 4:
                        userTables[pi][ci][2] = c.value
                        userTables[pi][ci][3] = colorToValue(c.color)
                    edit = True
            pi += 1

    # I fill also the table
    for i, (_, v) in enumerate(data.tableCards.items()):
        table[i] = len(v)
    # table[0] = len(data.tableCards['red'])
    # table[1] = len(data.tableCards['yellow'])
    # table[2] = len(data.tableCards['green'])
    # table[3] = len(data.tableCards['blue'])5
    # table[4] = len(data.tableCards['white'])

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
            #print(f"VALUE: {myCardValues[i][0]} - COLOR: {myCardValues[i][1]} - {valueToColor(myCardValues[i][1])}")
            if myCardValues[i][0] > -1 and myCardValues[i][
                    1] > -1 and myCardValues[i][0] <= table[myCardValues[i]
                                                            [1]]:
                print(f"discard {i} because already present")
                if not discardCard(s, i):
                    continue
                stop = True
        # case I have 2 cards with same value of same color
        for i in range(NUMBER_OF_CARD):
            for j in range(NUMBER_OF_CARD):
                if i != j and (all(myCardValues[i] > -1)
                               and all(myCardValues[i] == myCardValues[j])):
                    print(
                        f"discard {i} because already present in the cards set"
                    )
                    if not discardCard(s, i):
                        continue
                    stop = True
        # add discard case in case that all cards of a value are played
        for i in range(NUMBER_OF_CARD):  # I iterate over possible values
            if all(table > i):
                for j in range(NUMBER_OF_CARD):  # I iterate over my cards
                    if myCardValues[j][0] == i:
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

        for i in range(NUMBER_OF_CARD):
            if all(myCardValues[i] > -1):
                if table[myCardValues[i][1]] >= myCardValues[i][
                        0]:  # case card already played
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
                        print(f"discard {i} because you can't play it")
                        if not discardCard(s, i):
                            continue
                        stop = True
                    if myCardValues[i][0] == 2 and checkVector[
                            0] == 3 and checkVector[1] == 2:
                        print(f"discard {i} because you can't play it")
                        if not discardCard(s, i):
                            continue
                        stop = True
                    if myCardValues[i][0] == 3 and checkVector[
                            0] == 3 and checkVector[1] == 2 and checkVector[
                                2] == 2:
                        print(f"discard {i} because you can't play it")
                        if not discardCard(s, i):
                            continue
                        stop = True
                    if myCardValues[i][0] == 4 and checkVector[
                            0] == 3 and checkVector[1] == 2 and checkVector[
                                2] == 2 and checkVector[2] == 3:
                        print(f"discard {i} because you can't play it")
                        if not discardCard(s, i):
                            continue
                        stop = True
            if stop:
                break

    # Play suggestion
    if stop == False:
        for i in range(NUMBER_OF_CARD):
            for j in range(NUMBER_OF_CARD):
                # table with 2 rows we have on the first cell the value and in the second the color
                #if (myCardValues[i][0] == 1 and table[myCardValues[i][1]][0] == 0) or \
                #(myCardValues[i][1] == table[myCardValues[i][1]][1] and  myCardValues[i][0] == (table[myCardValues[i][1]][0] + 1) and table[myCardValues[i][j]][0] <= 4):
                # With the change that table is only one row we have:
                if sum(table) == 0 and myCardValues[i][0] == 1:
                    print(f"play {i}")
                    stop = True
                elif myCardValues[i][1] != -1 and ((myCardValues[i][0] == 1 and table[myCardValues[i][1]] == 0) or \
                (myCardValues[i][0] == (table[myCardValues[i][1]] + 1) and table[myCardValues[i][j]] <= 4)):
                    print(f"play {i}")
                    stop = True
                if stop:
                    if not playCard(s, i):
                        continue
                    break
            if stop:
                break

    suggestPlayer = None
    valuePerColor = np.zeros(
        numPlayer *
        NUMBER_OF_CARD)  # NUMBER_OF_CARD in this case is NUMBER_OF_COLORS
    valuePerColor = np.reshape(valuePerColor, (numPlayer, NUMBER_OF_CARD))

    if BLUE_TOKEN - usedNoteTokens > 0:  # I have to check that I have 1 token available for do a Hint.
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
                if suggestPlayer is not None and suggestValue is not None and userTables[
                        suggestPlayer][i][2] == suggestValue:
                    suggestHintValues.append(i)

            # Color part
            for pi in range(numPlayer - 1):  # for each player
                for ci in range(NUMBER_OF_CARD):  # for each card
                    # we count the # of card of that colour.
                    if userTables[pi][ci][
                            1] != 1:  # if the card color is already hinted we don't add to the sum.
                        valuePerColor[pi][userTables[pi][ci][3]] += 1
            hintPlayers, hintColorValues = np.where(
                valuePerColor == np.max(valuePerColor))
            hintPlayer, hintColor = hintPlayers[0], hintColorValues[
                0]  # I have to take only the first case
            # todo: add the part of check that is good to do color hint only if we don't have nothing else to suggest that can be play soon.
            # fix from tabel[hintColor][0] -> table[hintColor]
            if valuePerColor[hintPlayer, hintColor] > table[hintColor] and np.max(
                    valuePerColor
            ) != 0:  # I suggest the color if # of color of that color is grater then the # of card in the table
                suggestColorValues = []
                for i in range(5):
                    if userTables[hintPlayer][i][3] == hintColor:
                        suggestColorValues.append(i)

                if hintPlayer is not None:
                    if playerNames.index(
                            playerName) < hintPlayer or playerNames.index(
                                playerName) == 0:
                        hintPlayer += 1

                    print(
                        f"hint color {playerNames[hintPlayer]} {valueToColor(hintColor)} {suggestColorValues}"
                    )  # I can send a 0 and I will obtain the correct positions.
                    hintCards(s, "color", playerNames[hintPlayer],
                              valueToColor(hintColor), suggestColorValues)
            else:

                if suggestPlayer is not None:
                    if playerNames.index(
                            playerName) < suggestPlayer or playerNames.index(
                                playerName) == 0:
                        suggestPlayer += 1

                    print(
                        f"hint value {playerNames[suggestPlayer]} {suggestValue} {suggestHintValues}"
                    )
                    hintCards(s, "value", playerNames[suggestPlayer],
                              suggestValue, suggestHintValues)
    # Discard part
    if usedNoteTokens > 0 and stop == False and suggestPlayer is None and np.max(
            valuePerColor) == 0:
        cardsValue = myCardValues[:, 0]
        min = None
        minI = None
        for i in range(NUMBER_OF_CARD):
            if min is None or (cardsValue[i] < min and cardsValue[i] != 0):
                min = cardsValue[i]
                minI = i
        if minI is not None:
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
    # My edit
    # da togliere il manage input, così tolgo il thread e posso lavorare
    #Thread(target=manageInput).start()
    # My code
    first = True
    firstIteration = True
    while run:
        # My code
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
            # My code
            numPlayer = data.connectedPlayers - 1  # I don't consider my self a player
            # toask: I can add a player while an other has marked his state as ready

            print("Ready: " + str(data.acceptedStartRequests) + "/" +
                  str(data.connectedPlayers) + " players")
            data = s.recv(DATASIZE)
            data = GameData.GameData.deserialize(data)
        if type(data) is GameData.ServerStartGameData:
            dataOk = True
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

            # My code
            #suggestedMove(s)
            #data = None
            if data.currentPlayer == playerName:
                suggestedMove(s)
                print("[" + playerName + " - " + status + "]: ", end="")
                #manageInput()

        if type(data) is GameData.ServerActionInvalid:
            dataOk = True
            print("Invalid action performed. Reason:")
            print(data.message)
        if type(data) is GameData.ServerActionValid:
            dataOk = True
            print("Action valid!")
            print("Current player: " + data.player)

            # My code
            if playerName == data.player:
                suggestedMove(s)
                print("[" + playerName + " - " + status + "]: ", end="")
                #manageInput()

        if type(data) is GameData.ServerPlayerMoveOk:
            dataOk = True
            print("Nice move!")
            print("Current player: " + data.player)

            # My code
            if playerName == data.player:
                suggestedMove(s)
                print("[" + playerName + " - " + status + "]: ", end="")
                #manageInput()

        if type(data) is GameData.ServerPlayerThunderStrike:
            dataOk = True
            print("OH NO! The Gods are unhappy with you!")

            # My code
            if playerName == data.player:
                suggestedMove(s)
                print("[" + playerName + " - " + status + "]: ", end="")
                #manageInput()

        if type(data) is GameData.ServerHintData:
            dataOk = True
            print("Hint type: " + data.type)
            print("Player " + data.destination + " cards with value " +
                  str(data.value) + " are:")
            for i in data.positions:
                print("\t" + str(i))
            # My code: add info to my table about my cards
            if playerName == data.destination:
                for i in data.positions:
                    if data.type == "value":
                        # case value
                        myCardValues[i][0] = data.value
                    else:
                        # case color
                        myCardValues[i][1] = colorToValue(str(data.value))
                #print(myCardValues)
                # After a hint is good to have a suggestion
                suggestedMove(s)
                print("[" + playerName + " - " + status + "]: ", end="")
                #manageInput()
            else:
                # case that is of an other player
                # todo: to test
                posPlayer = playerNames.index(data.destination)
                # I don't need because I don't consider my self a player
                # if playerNames.index(playerName) < posPlayer:
                #     posPlayer -= 1

                for i in data.positions:
                    if data.type == "value":
                        userTables[posPlayer][i][0] = 1
                    else:
                        userTables[posPlayer][i][1] = 1

        if type(data) is GameData.ServerInvalidDataReceived:
            dataOk = True
            print(data.data)
        if type(data) is GameData.ServerGameOver:
            dataOk = True
            print(data.message)
            print(data.score)
            print(data.scoreMessage)
            stdout.flush()
            # My code
            computeScore(table)

            #run = False
            print("Ready for a new game!")

        if not dataOk:
            print("Unknown or unimplemented data type: " + str(type(data)))

        # I don't think that I need this
        #stdout.flush()
"""
#For call the MCTS
from MonteCarloTreeSearchNode import MCTSN

myState = cf.completeHand(userTables, myCardValues, discardPile, table) # Here I have a full hand
myState = np.c_[np.zeros(5)-1, np.zeros(5)-1, myState] # Here I add the 2 columns for the hinted value and color
myState = np.reshape(myState, (1, 5, 4)) # Here I reshape as the same shape of the state
state = np.concatenate((myState, userTables)) # Here I have myState + other User State.

names = np.concatenate((playerName, playerNames))


root = MCTSN(state, 0, numPlayer, names, table, discardPile, 0)
move_number = 0
while not root.is_game_over(root.state):
    selected_node = root.best_action()
    root = selected_node
    move_number += 1
    print(f"{move_number} -> {root.player}")
    player = (root.player + 1) % root.numPlayer
print(f"Final state: \n Winning player: {MCTSN.game_result(root.table)}")
"""
