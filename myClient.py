#!/usr/bin/env python3

from sys import argv, stdout
from threading import Thread
import GameData
import socket
from constants import *
import os

# My code
import numpy as np

if len(argv) < 4:
    print("You need the player name to start the game.")
    #exit(-1)
    playerName = "Test" # For debug
    playerName = "p2" # add by me
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
    while run:
        command = input()
        # Choose data to send
        if command == "exit":
            run = False
            os._exit(0)
        elif command == "ready" and status == statuses[0]:
            s.send(GameData.ClientPlayerStartRequest(playerName).serialize())
        elif command == "show" and status == statuses[1]:
            s.send(GameData.ClientGetGameStateRequest(playerName).serialize())
        elif command.split(" ")[0] == "discard" and status == statuses[1]:
            try:
                cardStr = command.split(" ")
                cardOrder = int(cardStr[1])
                s.send(GameData.ClientPlayerDiscardCardRequest(playerName, cardOrder).serialize())
            except:
                print("Maybe you wanted to type 'discard <num>'?")
                continue
        elif command.split(" ")[0] == "play" and status == statuses[1]:
            try:
                cardStr = command.split(" ")
                cardOrder = int(cardStr[1])
                
                # My code: remove the current card from the set, I lose the information about that card
                myCardValues[cardOrder][0] = -1
                myCardValues[cardOrder][1] = -1

                s.send(GameData.ClientPlayerPlayCardRequest(playerName, cardOrder).serialize())
            except:
                print("Maybe you wanted to type 'play <num> <pile position>'?")
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
                # Todo: add to the user table the fact that I give a hint. 
            except:
                print("Maybe you wanted to type 'hint <type> <destinatary> <value>'?")
                continue
        elif command == "":
            print("[" + playerName + " - " + status + "]: ", end="")
        else:
            print("Unknown command: " + command)
            continue
        stdout.flush()

# My code

numPlayer = -1
playerNames = []
userTable = np.zeros(4*5*4, dtype=np.int8) # 4 users, 5 cards per users, 4 value per card: Hint value, Hint color, Value,  color
userTable = np.reshape(userTable, (4, 5, 4))
table = np.zeros(5 * 2, dtype=np.int8) # Table value, 5 places, 2 value [value, color] if value = 0 no card same for color
table = np.reshape(table, (5,2))
myCardValues = np.zeros(5*2, dtype=np.int8) #5 cards, 2 value per card: value, color
myCardValues = np.reshape(myCardValues, (5,2))

def colorToValue(color):
    # base on the order of the tableCards inside data
    if color == "red":
        return 0
    if color == "yellow":
        return 1
    if color == "green":
        return 2
    if color == "blue":
        return 3
    return 4

def suggestedMove(data):
    s.send(GameData.ClientGetGameStateRequest(playerName).serialize())
    data = s.recv(DATASIZE)
    data = GameData.GameData.deserialize(data)

    for pi, p in enumerate(data.players):
        playerNames.append(p.name)
        for ci, c in enumerate(p.hand):
            userTable[pi][ci][2] = c.value
            userTable[pi][ci][3] = colorToValue(c.color)

    # Hint suggestion
    # For now only value suggestion
    
    suggestPlayer = None
    suggestValue = None
    
    for i in range(numPlayer - 1):
        for v in range(5):
            for ci in range(5):
                if userTable[i][ci][2] == v:
                    suggestPlayer = i
                    suggestValue = v
                if suggestPlayer is not None:
                    break
            if suggestPlayer is not None:
                    break
        if suggestPlayer is not None:
                    break
    suggestValues = []
    for i in range(5):
        if userTable[suggestPlayer][i][2] == suggestValue:
            suggestValues.append(i)

    #print(f"Suggested move: hint value {playerNames[suggestPlayer]} {suggestValue} {suggestValues}")
    
    # Play way
    stop = False
    for i in range(NUMBER_OF_CARD):
        for j in range(NUMBER_OF_CARD):
            #print(f"Value = {myCardValues[i][0]}\tColor = {myCardValues[i][1]}\t{myCardValues.shape}") #to remove, used for testing
            # First condition: if I have the card 1 and the 
            if (myCardValues[i][0] == 1 and table[myCardValues[i][1]][0] == 0) or \
               (myCardValues[i][1] == table[myCardValues[i][1]][1] and  myCardValues[i][0] == (table[myCardValues[i][1]][0] + 1) and table[myCardValues[i][j]][0] <= 4): 
                print(f"Suggest move: play {i}")
                stop = True
            if stop:
                break
        if stop:
            break
    
    if stop == False and suggestPlayer is not None:
        print(f"Suggested move: hint value {playerNames[suggestPlayer]} {suggestValue} {suggestValues}")
    
    # Discard part
    if stop == False and suggestPlayer is None:
        cardsValue = myCardValues[:][0]
        min = None
        minI = None
        for i in range(NUMBER_OF_CARD):
            if cardsValue[i] < min and cardsValue[i] != 0:
                min = cardsValue[i]
                minI = i
        if minI is not None:
            print(f"Suggested move: discard {minI}")
    #for ci, c in enumerate(data.tableCards):
    #    table[ci][0] = colorToValue(ci)
    #    table[ci][1] = ci.len()

    #print(userTable)

    #print(data.players)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    request = GameData.ClientPlayerAddData(playerName)
    s.connect((HOST, PORT))
    s.send(request.serialize())
    data = s.recv(DATASIZE)
    data = GameData.GameData.deserialize(data)
    if type(data) is GameData.ServerPlayerConnectionOk:
        print("Connection accepted by the server. Welcome " + playerName)
    print("[" + playerName + " - " + status + "]: ", end="")
    Thread(target=manageInput).start()
    while run:
        dataOk = False
        data = s.recv(DATASIZE)
        if not data:
            continue
        data = GameData.GameData.deserialize(data)
        if type(data) is GameData.ServerPlayerStartRequestAccepted:
            dataOk = True
            # My code
            numPlayer = data.connectedPlayers # toask: I can add a player while an other has marked his state as ready
            
            print("Ready: " + str(data.acceptedStartRequests) + "/"  + str(data.connectedPlayers) + " players")
            data = s.recv(DATASIZE)
            data = GameData.GameData.deserialize(data)
        if type(data) is GameData.ServerStartGameData:
            dataOk = True
            print("Game start!")
            s.send(GameData.ClientPlayerReadyData(playerName).serialize())
            status = statuses[1]
            # My code
            if type(data) is not GameData.ServerHintData:
                suggestedMove(s) 
                data = None
        if type(data) is GameData.ServerGameStateData:
            dataOk = True
            print("Current player: " + data.currentPlayer)
            print("Player hands: ")
            for p in data.players:
                print(p.toString())
            print("Table cards: ")
            for pos in data.tableCards:
                print(pos + ": [ ")
                for c in data.tableCards[pos]:
                    print(c.toString() + " ")
                print("]")
            print("Discard pile: ")
            for c in data.discardPile:
                print("\t" + c.toString())            
            print("Note tokens used: " + str(data.usedNoteTokens) + "/8")
            print("Storm tokens used: " + str(data.usedStormTokens) + "/3")

            # My code
            suggestedMove(s) 
            #data = None
        if type(data) is GameData.ServerActionInvalid:
            dataOk = True
            print("Invalid action performed. Reason:")
            print(data.message)
        if type(data) is GameData.ServerActionValid:
            dataOk = True
            print("Action valid!")
            print("Current player: " + data.player)
        if type(data) is GameData.ServerPlayerMoveOk:
            dataOk = True
            print("Nice move!")
            print("Current player: " + data.player)
        if type(data) is GameData.ServerPlayerThunderStrike:
            dataOk = True
            print("OH NO! The Gods are unhappy with you!")
        if type(data) is GameData.ServerHintData:
            dataOk = True
            print("Hint type: " + data.type)
            print("Player " + data.destination + " cards with value " + str(data.value) + " are:")
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
                print(myCardValues)
            suggestedMove(s) 
            #data = None

        if type(data) is GameData.ServerInvalidDataReceived:
            dataOk = True
            print(data.data)
            # My code
            suggestedMove(s) 
            #data = None
        if type(data) is GameData.ServerGameOver:
            dataOk = True
            print(data.message)
            print(data.score)
            print(data.scoreMessage)
            stdout.flush()
            run = False
        if not dataOk:
            print("Unknown or unimplemented data type: " +  str(type(data)))
        print("[" + playerName + " - " + status + "]: ", end="")
        stdout.flush()