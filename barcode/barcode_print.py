import argparse
import re
import subprocess
import tempfile
import time
import os
from pprint import pprint
from dkbc.dkbc import DKBC
from inventory_label.inventory_label import InventoryLabel

iso_iec_15434_start = re.compile("^>?\[\)>(\{RS\})?[>]?[0-9]{2}{GS}")
# https://www.eurodatacouncil.org/images/documents/ANS_MH10.8.2%20_CM_20140512.pdf
ansi_mh10_8_2_item = re.compile("(?P<DI>[0-9]*[A-Z])(?P<value>[A-Za-z0-9\-\.\ ]*)")

known_dis = {
    "K": "Customer PO Number",
    "1K": "Supplier Order Number",
    "10K": "Invoice Number",
    "P": "Part No.",
    "1P": "Supplier Part Number",
    "Q": "Quantity",
    "4L": "Country of Origin",
}

parser = argparse.ArgumentParser()
parser.add_argument("--batch", action="store_true", help="Batch scan")
parser.add_argument("--print", action="store_true", help="Print label")
parser.add_argument("--debug", action="store_true", help="Debug mode")
args = parser.parse_args()

dkbc = DKBC()


def decode_barcode(barcode):
    # Check for valid code first
    if not iso_iec_15434_start.match(barcode):
        raise ValueError("Invalid barcode!")

    fields = {}
    sections = barcode.split("{GS}")
    for section in sections[1:]:
        match = ansi_mh10_8_2_item.match(section)
        if match:
            di = match.group("DI")
            value = match.group("value")

            if di in known_dis:
                fields[known_dis[di]] = value
            elif args.debug:
                print("NEW DI!", di, value)
        elif args.debug:
            print("Invalid section", section)

    return fields


scanning = True

while scanning:
    if args.batch:
        scanning = True
    else:
        scanning = False

    barcode = input("Scan barcode:")

    try:
        fields = decode_barcode(barcode)

        # TODO - use other digikey api when scanning non-dk barcodes
        barcode = barcode.replace("{RS}", "\x1e")
        barcode = barcode.replace("{GS}", "\x1d")
        barcode = barcode.replace("{EOT}", "\x04")
        digikey_data = dkbc.process_barcode(barcode)
    except ValueError:
        fields = None
        simple_code = None
        digikey_data = dkbc.process_barcode(barcode)

    if args.debug:
        if fields:
            pprint(fields)
        pprint(digikey_data)

    new_code = [
        "[)>\u001e06",
        "1P" + digikey_data["ManufacturerPartNumber"],
        "P" + digikey_data["DigiKeyPartNumber"],
    ]

    # Add GS delimiters and EOT at the end
    reduced_barcode = "\x1d".join(new_code) + "\x04"

    if "ProductDescription" in digikey_data:
        description = digikey_data["ProductDescription"]
    else:
        description = ""

    print(digikey_data["ManufacturerPartNumber"] + " " + description)

    temp_dir = tempfile.mkdtemp(prefix="barcode_")
    label_filename = os.path.join(temp_dir, "barcode.png")
    if args.debug:
        print("Temp file", label_filename)

    label = InventoryLabel(font_name="Andale Mono.ttf")
    label.create_label(
        digikey_data["ManufacturerPartNumber"],
        description,
        reduced_barcode.encode("ascii"),
        label_filename,
        debug=args.debug,
    )

    if args.print:
        result = subprocess.run(
            [
                "lp",
                "-d",
                "Brother_QL_570",
                "-o",
                "media=Custom.62x23mm",
                "-o",
                "fit-to-page",
                "-o",
                "orientation-requested=3",
                label_filename,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if result.returncode:
            print("Error printing {}".format(label_filename))

    os.remove(label_filename)
