from cons import char_map, multiples, tick, maxBits
from concurrent.futures import ThreadPoolExecutor
import time

testString = "Hey"
recData = []

startSeq = [1,1,1,1,1,1,1,1]

cable = 0

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
                    
        return cleanBinary

    else:
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

        return data

def startClock():
    global cable
    lastSeq = []
    time.sleep(tick / 2)
    data = []

    #state 0
    while not (lastSeq == startSeq):
        time.sleep(tick)
        lastSeq.append(cable)

        #keep only the last 8
        if len(lastSeq) > 8:
            lastSeq.pop(0)

    #state 1
    SizeBinary = []

    #read data size
    for i in range(8):
        time.sleep(tick)
        SizeBinary.append(cable)

    size = binToDec(SizeBinary)[0]

    #state 2
    #read actual data
    for i in range(size*8):
        time.sleep(tick)
        data.append(cable)

    return data
    

def sendData(data):
    global cable

    time.sleep(tick * 10) #testing silence

    #start
    for bit in startSeq:
        cable = bit
        time.sleep(tick)

    #size
    binarySize = decToBin(int(len(data)/8))

    for bit in binarySize:
        cable = bit
        time.sleep(tick)

    #data
    for bit in data:
        cable = bit
        time.sleep(tick)

    #reset cable
    cable = 0

def transmit(data):
    with ThreadPoolExecutor() as executor:
        res = executor.submit(startClock)
        res2 = executor.submit(sendData, data)

    binary = res.result()

    return ASCIIConv(binary, False)

def test():
    bin = ASCIIConv(testString, True)
    return transmit(bin)
    
print(test())