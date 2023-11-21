import argparse
import binascii
import csv
import os

def main():
    print("MGS3 *.gcx Export by Giza(tr1ton)")
    parser = argparse.ArgumentParser(description="Extracting texts from a binary file and saving them to CSV")
    parser.add_argument("input_file", help="Input binary file name")
    args = parser.parse_args()

    # Open the binary file
    with open(args.input_file, 'rb') as file:
        binary_data = file.read()

    # Search hex 00 00 00 00 18 00 00 00
    pattern = binascii.unhexlify('0000000018000000')
    data_pairs = []

    index = 0
    while index < len(binary_data):
        index = binary_data.find(pattern, index)
        if index == -1:
            break

        # Read the next 4 bytes in Little endian
        offset_length = int.from_bytes(binary_data[index + len(pattern):index + len(pattern) + 4], byteorder='little')
        index += len(pattern) + 4
        print(offset_length)

        # Read the next 4 bytes, which will be offsets to the texts
        text_offsets = []
        for _ in range(offset_length):
            text_offset = int.from_bytes(binary_data[index:index + 4], byteorder='little')
            text_offsets.append(text_offset)
            index += 4

        # Processing texts
        texts = []
        index -=(4*offset_length)+4
        for text_offset in text_offsets:
            text_start = index + text_offset
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
            csv_writer.writerow([hex(offset), text])

    print(f"Ready! Texts are saved in {output_file}")

if __name__ == "__main__":
    main()