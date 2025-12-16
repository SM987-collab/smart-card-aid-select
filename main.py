from smartcard.System import readers
from smartcard.util import toHexString

USE_SIMULATOR = True   

# GlobalPlatform Issuer Security Domain AID
AID = [0xA0, 0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00]

# SELECT APDU
SELECT_APDU = [
    0x00,        # CLA
    0xA4,        # INS
    0x04,        # P1 (select by AID)
    0x00,        # P2
    len(AID)
] + AID


# ==========================================================
# SIMULATOR
# ==========================================================
class SimulatedCardConnection:
    """
    Simple software smart-card simulator.
    Simulates SELECT AID behavior only.
    """

    def __init__(self, supported_aid):
        self.supported_aid = supported_aid

    def connect(self):
        print("[SIMULATOR] Card connected")

    def getATR(self):
        # Fake ATR (for logging only)
        return [0x3B, 0x90, 0x11, 0x00]

    def transmit(self, apdu):
        print("[SIMULATOR] APDU received:", toHexString(apdu))

        if len(apdu) < 5:
            return [], 0x67, 0x00  # Wrong length

        cla, ins, p1, p2, lc = apdu[:5]
        data = apdu[5:5 + lc]

        # Handle SELECT AID
        if ins == 0xA4 and p1 == 0x04 and data == self.supported_aid:
            print("[SIMULATOR] AID selected")
            return [], 0x90, 0x00

        print("[SIMULATOR] AID not found")
        return [], 0x6A, 0x82


# ==========================================================
# REAL CARD CONNECTION
# ==========================================================
def connect_real_card():
    print("Searching for PC/SC readers...")
    r = readers()

    if not r:
        raise Exception("No smart card readers found")

    print("Available readers:")
    for i, reader in enumerate(r):
        print(f"[{i}] {reader}")

    # Automatically use the first reader
    reader = r[0]
    print(f"\nUsing reader: {reader}")

    connection = reader.createConnection()
    connection.connect()
    return connection


# ==========================================================
# MAIN
# ==========================================================
def main():

    if USE_SIMULATOR:
        print("Running in SIMULATOR mode")
        connection = SimulatedCardConnection(AID)
        connection.connect()
    else:
        print("REAL hardware")
        connection = connect_real_card()

    print("ATR:", toHexString(connection.getATR()))

    print("\n Sending select command for AID :", toHexString(SELECT_APDU))
    response, sw1, sw2 = connection.transmit(SELECT_APDU)

    print(" Response Data:", toHexString(response))
    print(f" Status Words: SW1={hex(sw1)}, SW2={hex(sw2)}")

    if sw1 == 0x90 and sw2 == 0x00:
        print("SUCCESS: AID selected")
    else:
        print("AID not selectable")


if __name__ == "__main__":
    main()
