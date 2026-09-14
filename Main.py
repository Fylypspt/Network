from cons import char_map, multiples, tick
from concurrent.futures import ThreadPoolExecutor
import time
import random
import threading

cable_lock = threading.Lock()

DEBUG = False
testString = "Hey"

startSeq = [1, 1, 1, 1, 1, 1, 1, 1]

#addresses:
adressSize = 4
broadcast = [1,1,1,1]

noiseChance = 0 #.05
maxTicks = 200      # test only, the protocol has no total limit

cable = 0

DebugMsgs = [
    "Clock - Tick limit reached: Preamble never found",
    "Clock - Tick limit reached: Frame abandoned mid-transmission",
    "Clock - Frame dropped, nothing decoded",
]

DebugCounter = {
    "Clock - Tick limit reached: Preamble never found": 0,
    "Clock - Tick limit reached: Frame abandoned mid-transmission": 0,
    "Clock - Frame dropped, nothing decoded": 0,
    "Hey": 0, #!!!!!!!
    "Undetected corruption": 0,
}

def CreateBit(data):
    if random.random() <= noiseChance:
        if DEBUG:
            print("Noise")
        if data == 0:
            data = 1
        else:
            data = 0
        return data
    else:
        return data

def binToDec(bin):
    # split into 8-bit blocks
    finalbin = []
    for i in range(0, len(bin), 8):
        bloco = bin[i:i+8]
        finalbin.append(bloco)

    storedMultiple = []

    # convert each block to decimal
    for letter in finalbin:
        firstMulti = []
        for i, val in enumerate(letter):
            if val == 1:
                firstMulti.append(multiples[i])
        storedMultiple.append(sum(firstMulti))

    return storedMultiple

def decToBin(dec):
    binary = []

    # build binary big to small
    for mult in multiples:
        if dec >= mult:
            binary.append(1)
            dec -= mult
        else:
            binary.append(0)

    return binary

def textToBin(text):
    if DEBUG:
        print("Text to Binary")
    # text -> binary
    letters = list(text)
    finalBinary = []
    cleanBinary = []

    for letter in letters:
        decimal_num = char_map[letter]
        binaryResult = []

        # convert char to 8-bit binary
        for v in multiples:
            if decimal_num >= v:
                binaryResult.append(1)
                decimal_num -= v
            else:
                binaryResult.append(0)

        finalBinary.append(binaryResult)

    # flatten binary lists
    for byte in finalBinary:
        for bit in byte:
            cleanBinary.append(bit)

    if DEBUG:
        print(f"{text} to {finalBinary}")

    return cleanBinary

def binToText(bits):
    if DEBUG:
        print("Binary to Text")
    # binary -> text
    dataL = []
    data = ""
    storedMultiple = binToDec(bits)
    inv_char_map = {v: k for k, v in char_map.items()}

    # convert decimals to chars
    for mul in storedMultiple:
        if mul in inv_char_map:
            dataL.append(inv_char_map[mul])
        else:
            dataL.append("?")

    # join chars
    for letter in dataL:
        data += str(letter)

    if DEBUG:
        print(f"{bits} to {data}")
    return data

def addParity(bits):
    blocos = []

    # split into 8-bit blocks
    for i in range(0, len(bits), 8):
        blocos.append(bits[i : i + 8])

    # one parity bit per block
    for bloco in blocos:
        parityCounter = 0
        for bit in bloco:
            if bit == 1:
                parityCounter += 1
        if parityCounter % 2 == 0:
            bloco.append(0)
        else:
            bloco.append(1)

    withParity = []

    for bloco in blocos:
        for bit in bloco:
            withParity.append(bit)

    return withParity

def checkParity(bits):
    blocos = []

    # split into 9-bit blocks
    for i in range(0, len(bits), 9):
        blocos.append(bits[i : i + 9])

    # check everything before building anything
    for i, bloco in enumerate(blocos):
        parityCounter = 0
        for bit in bloco:
            if bit == 1:
                parityCounter += 1
        if parityCounter % 2 != 0:
            if DEBUG:
                print(f"ERROR Parity Broken in byte {i}")
            return [], False

    cleanBits = []

    # drop the parity bit
    for bloco in blocos:
        for bit in bloco[:8]:
            cleanBits.append(bit)

    return cleanBits, True

#--------------------------------------------------------------

class clock:
    def __init__(self, Name, Address):
        self.Name = Name
        self.Address = Address
    def execute(self):
        if DEBUG:
            print("Clock - Init")
        global cable
        lastSeq = []
    
        # half tick offset: sample in the middle of the bit, not on the transition
        time.sleep(tick / 2)
    
        totalTicks = 0  # test only, the protocol has no total limit
        preambleFound = False
    
        while totalTicks < maxTicks:
            # state 0
            if DEBUG:
                print("Clock - State 0")
            while not (lastSeq == startSeq) and totalTicks < maxTicks:
                time.sleep(tick)
                totalTicks += 1
                with cable_lock:
                    value = cable
                lastSeq.append(value)
    
                # keep only the last 8
                if len(lastSeq) > 8:
                    lastSeq.pop(0)
    
            if not (lastSeq == startSeq):
                break  # test only
    
            if DEBUG:
                print(f"Clock - Sequence read: {lastSeq}")
            lastSeq = []
            preambleFound = True
    
            # state 1
            if DEBUG:
                print("Clock - State 1")
    
            origin = []
            end = []
            waitLimit = 10
            waited = 0
    
            while len(end) < adressSize:
                if waited >= waitLimit or totalTicks >= maxTicks:
                    if DEBUG:
                        print("Test1")
                    break
                time.sleep(tick)
                totalTicks += 1
                waited += 1
                with cable_lock:
                    end.append(cable)
    
            waited = 0
    
            while len(origin) < adressSize:
                if waited >= waitLimit or totalTicks >= maxTicks:
                    if DEBUG:
                        print("Test2")
                    break   
                time.sleep(tick)
                totalTicks += 1
                waited += 1
                with cable_lock:
                    origin.append(cable)
    
            if not (end == self.Address or end == broadcast):
                if DEBUG:
                    print(f"end: {end}")
                    print(f"org: {origin}")
                    print("Wrong Address")
                continue
            else:
                if DEBUG:
                    print("Right address")
            # state 2
            if DEBUG:
                print("Clock - State 2")
            sizeBinary = []
            waited = 0
    
            waitLimit = 15
    
            # read data size
            while len(sizeBinary) < 8:
                if waited >= waitLimit or totalTicks >= maxTicks:
                    if DEBUG:
                        print("Clock - State 1 timeout, dropping frame")
                    break
                time.sleep(tick)
                totalTicks += 1
                waited += 1
                with cable_lock:
                    sizeBinary.append(cable)
    
            if len(sizeBinary) < 8:
                continue
    
            size = binToDec(sizeBinary)[0]
    
            if DEBUG:
                print(f"Clock - Data size: {size}")
    
            # state 3
            if DEBUG:
                print("Clock - State 3")
            # read actual data
            frameBits = []
            waited = 0
    
            waitLimit = size * 9 + 50
    
            while len(frameBits) < size * 9:
                if waited >= waitLimit or totalTicks >= maxTicks:
                    if DEBUG:
                        print("Clock - State 2 timeout, dropping frame")
                    break
                time.sleep(tick)
                totalTicks += 1
                waited += 1
                with cable_lock:
                    frameBits.append(cable)
    
            if len(frameBits) < size * 9:
                continue
    
            finalCleanBits, ok = checkParity(frameBits)
    
            if not ok:
                if DEBUG:
                    print("Clock - Frame dropped, nothing decoded")
                return "Clock - Frame dropped, nothing decoded"
    
            if DEBUG:
                print(f"Clock - Data: {finalCleanBits}")
            return finalCleanBits
    
        if DEBUG:
            print("Clock - Tick limit reached")  # test only
            
        # if preambleFound:
        #     return "Clock - Tick limit reached: Frame abandoned mid-transmission"
        # else:
        #     return "Clock - Tick limit reached: Preamble never found"

#--------------------------------------------------------------

def writeBit(bit):
    global cable
    with cable_lock:
        cable = CreateBit(bit)
    time.sleep(tick)

def sendData(data, end, org):
    if DEBUG:
        print("Sender - Init")
    global cable

    time.sleep(tick * 10)  # testing silence

    if DEBUG:
        print("Sender - Sending")

    # start
    for bit in startSeq:
        writeBit(bit)

    #endpoint
    if DEBUG:
        print("EndPoint")
    for bit in end:
        writeBit(bit)

    # originpoint
    if DEBUG:
        print("Origin")
    for bit in org:
        writeBit(bit)

    # size
    if DEBUG:
        print("Sender - Size")
    binarySize = decToBin(len(data) // 9)

    if DEBUG:
        print(f"Sender - Sent Size: {binarySize}")

    for bit in binarySize:
        writeBit(bit)

    if DEBUG:
        print("Sender - Data")
    # data
    for bit in data:
        writeBit(bit)

    if DEBUG:
        print(f"Sender - Sent Data: {data}")

    # reset cable
    with cable_lock:
        cable = 0

def transmit(data, end1, end2):
    casa1 = clock("Casa1", [0,0,0,1])
    casa2 = clock("Casa2", [0,0,1,1])
    casa3 = clock("Casa3", [0,1,1,1])

    threads = [
        casa1.execute,
        casa2.execute,
        casa3.execute
    ]

    results = []

    with ThreadPoolExecutor() as executor:
        for task in threads:
            res = executor.submit(task)
            results.append(res)
        executor.submit(sendData, data, end1, end2)

    final = []

    for res in results:
        final.append(res.result())

    return final

def test(end1, end2):
    if DEBUG:
        print("Start")

    bin = textToBin(testString)
    return transmit(addParity(bin), end1, end2)

startT = 0
endT = 0

rg = 1
corruptedResults = []

for i in range(rg):
    startT = time.perf_counter()
    result = test([0,0,0,1], [0,0,1,1])

    for i in range(len(result)):
        if result[i] is not None:
            print(binToText(result[i]))
        else:
            print(result[i])

    #----------------------------------------
#     print(f"{i + 1}: {result}")

#     if i == 1:
#         endT = time.perf_counter()
#         elapsed = endT - startT
        
#         estSec = elapsed * rg
#         estMin = estSec / 60
        
#         print(f"Estimate: {round(estMin, 2)} min")

#     if result in DebugCounter:
#         DebugCounter[result] += 1
#     elif result not in DebugMsgs and result != testString:
#         DebugCounter["Undetected corruption"] += 1
#         corruptedResults.append(result)

# print("\nErrors Encountered:")

# for error, count in DebugCounter.items():
#     print(f"{error:<35} {count:>7}")

# print("\nCorrupted Results:")
# for result in corruptedResults:
#     print(result)