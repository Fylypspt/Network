from cons import char_map, multiples, tick, maxBits
from concurrent.futures import ThreadPoolExecutor
import time
import random

testString = "Hey"
recData = []

startSeq = [1,1,1,1,1,1,1,1]

cable = 0

def CreateBit(data):
    print("--Bit Creation--")
    if random.random() <= 0.05:
        print("Noise")
        if data == 0:
            data = 1
        else:
            data = 0
        print("--End Bit--")
        return data
    else:
        print("Clean")
        print("--End Bit--")
        return data

def binToDec(bin):
    #split into 8-bit blocks
    finalbin = []
    for i in range(0, len(bin), 8):
        bloco = bin[i:i+8]
        finalbin.append(bloco)

    storedMultiple = []

    #convert each block to decimal
    for letter in finalbin:
        firstMulti = []
        for i, val in enumerate(letter):
            if val == 1:                    
                firstMulti.append(multiples[i])
        storedMultiple.append(sum(firstMulti))

    return storedMultiple

def decToBin(dec): #!!!
    binary = []
    
    #build binary big to small
    for mult in multiples:
        if dec >= mult:
            binary.append(1)
            dec -= mult
        else:
            binary.append(0)
            
    return binary

def ASCIIConv(info, work):
    if work == True:
        print("Text to Binary")
        #text -> binary
        letters = list(info)
        finalBinary = []
        cleanBinary = []

        for letter in letters:
            decimal_num = char_map[letter]
            binaryResult = []
            
            #convert char to 8-bit binary
            for v in multiples:
                if decimal_num >= v:
                    binaryResult.append(1)
                    decimal_num -= v
                else:
                    binaryResult.append(0)

            finalBinary.append(binaryResult)
    
        #flatten binary lists
        for letter in finalBinary:
            for bit in letter:
                cleanBinary.append(bit)


        print(f"{info} to {finalBinary}")            
        return cleanBinary

    else:
        print("Binary to Text")
        #binary -> text
        dataL = []
        data = ""
        storedMultiple = binToDec(info)

        #convert decimals to chars
        for index, mul in enumerate(storedMultiple):
            for l, v in char_map.items():
                if v == storedMultiple[index]:
                    dataL.append(l)

        #join chars
        for letter in dataL:
            data += str(letter)

        print(f"{info} to {data}")
        return data

def startClock():
    print("Clock - Init")
    global cable
    lastSeq = []
    time.sleep(tick / 2)
    data = []

    #state 0
    print("Clock - State 0")
    while not (lastSeq == startSeq):
        time.sleep(tick)
        lastSeq.append(cable)

        #keep only the last 8
        if len(lastSeq) > 8:
            lastSeq.pop(0)
    print(f"Clock - Sequence read: {lastSeq}")

    print("Clock - State 1")
    #state 1
    SizeBinary = []

    #read data size
    for i in range(8):
        time.sleep(tick)
        SizeBinary.append(cable)

    size = binToDec(SizeBinary)[0]

    print(f"Clock - Data size: {size}")

    print("Clock - State 2")
    #state 2
    #read actual data
    for i in range(size*8):
        time.sleep(tick)
        data.append(cable)

    print(f"Clock - Data: {data}")
    return data
    

def sendData(data):
    print("Sender - Init")
    global cable

    time.sleep(tick * 10) #testing silence


    print("Sender - Sending")
    #start
    for bit in startSeq:
        cable = CreateBit(bit)
        time.sleep(tick)

    print(f"Sender - Sent StartSeq: {startSeq}")

    print("Sender - Size")
    #size
    binarySize = decToBin(int(len(data)/8))

    print(f"Sender - Sent Size: {binarySize}")

    for bit in binarySize:
        cable = CreateBit(bit)
        time.sleep(tick)

    print("Sender - Data")
    #data
    for bit in data:
        cable = CreateBit(bit)
        time.sleep(tick)
    print(f"Sender - Sent Data: {data}")

    #reset cable
    cable = 0

def transmit(data):
    with ThreadPoolExecutor() as executor:
        res = executor.submit(startClock)
        res2 = executor.submit(sendData, data)

    binary = res.result()

    return ASCIIConv(binary, False)

def test():
    print("Start")
    bin = ASCIIConv(testString, True)
    return transmit(bin)
    
print(test())