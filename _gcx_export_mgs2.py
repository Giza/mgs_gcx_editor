import argparse
import binascii
import csv
import os
import struct

def main():
    print("MGS2 *.gcx Export by Giza(tr1ton)")
    parser = argparse.ArgumentParser(description="Extracting texts from a binary file and saving them to CSV")
    parser.add_argument("input_file", help="Input binary file name")
    args = parser.parse_args()

    # Open the binary file
    with open(args.input_file, 'rb') as file:
        binary_data = file.read()

    # Search offset
    offset = 0
    while offset < len(binary_data):
		# Parse
        proc_value_1 = struct.unpack("<L", binary_data[offset:offset+4])[0]
        #print(proc_value_1)
        offset += 4

        if (proc_value_1 == 0):
            proc_value_2 = struct.unpack("<L", binary_data[offset:offset+4])[0]
            if (proc_value_2 == 0):
                offset += 20
                proc_value_3 = struct.unpack("<L", binary_data[offset:offset+4])[0]
                if (proc_value_3 == 20):
                    print("Offset found")
                    offset -= 16
                    break

    # Read the next 4 bytes in Little endian
    offset_length = struct.unpack("<L", binary_data[offset+20:offset+24])[0]
    print(f"Number of lines: {offset_length}")
    offset += 24

    # Read the next 4 bytes, which will be offsets to the texts
    text_offsets = []
    for _ in range(offset_length):
        text_offset = int.from_bytes(binary_data[offset:offset + 4], byteorder='little')
        text_offsets.append(text_offset)
        offset += 4
    
    data_pairs = []
    # Processing texts
    texts = []
    offset -= (4*offset_length)+4
    #print(offset)
    for text_offset in text_offsets:
        text_start = offset + text_offset
        text_end = binary_data.find(b'\x00', text_start)
        if text_end == -1:
            text_end = len(binary_data)
        text = binary_data[text_start:text_end].decode('utf-8', errors='ignore')
        texts.append((text_offset, text))
    data_pairs.extend(texts)

    # We write the received texts to a csv file
    base_filename = os.path.splitext(args.input_file)[0]
    output_file = f"{base_filename}.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        for offset, text in data_pairs:
            csv_writer.writerow([hex(offset), text, text])

    print(f"Ready! Texts are saved in {output_file}")

if __name__ == "__main__":
    main()
