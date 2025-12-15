from smartcard.System import readers
from smartcard.util import toHexString

# ----------------------------
# CONFIG
# ----------------------------
PERSONAL_READER_NAME = "HID Global OMNIKEY 3x21 Smart Card Reader 0"

# Applet AID
AID = [0xA0, 0x00, 0x00, 0x08, 0x15, 0x03, 0x09, 0x90, 0x02, 0x03, 0x08, 0x02]

# SELECT APDU
SELECT_APDU = [
    0x00,        # CLA
    0xA4,        # INS (SELECT)
    0x04,        # P1 (select by AID)
    0x00,        # P2
    len(AID)
] + AID


def main():
    print("🔹 Searching for smart card readers...")
# it stores the total available readers    
    r = readers()
# if condition to check avaialble readers
    if not r:
        raise Exception("❌ No smart card readers found")

    print("Available readers:")
    selected_reader = None
# selecting the desired reader
    for idx, reader in enumerate(r):
        print(f"[{idx}] {reader}")
        if PERSONAL_READER_NAME in str(reader):
            selected_reader = reader

    if selected_reader is None:
        raise Exception(
            f"❌ Reader '{PERSONAL_READER_NAME}' not found.\n"
            "➡️ Check driver, USB connection, or reader name."
        )

    print("\n✅ Using reader:", selected_reader)

    # Connect to card
    connection = selected_reader.createConnection()
    connection.connect()

    print("✅ Card connected")
    print("ATR:", toHexString(connection.getATR()))

    # Send SELECT APDU
    print("\n➡️ Sending SELECT APDU:", toHexString(SELECT_APDU))
    response, sw1, sw2 = connection.transmit(SELECT_APDU)

    print("⬅️ Response Data:", toHexString(response))
    print(f"⬅️ Status Words: SW1={hex(sw1)}, SW2={hex(sw2)}")

    if sw1 == 0x90 and sw2 == 0x00:
        print("🎉 SUCCESS: Applet selected")
    else:
        print("Applet not selected 6A 82")


if __name__ == "__main__":
    main()