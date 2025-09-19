import argparse
import binascii
import csv
import os
import struct

def main():
    print("MGS2 PS2 *.gcx Export by Giza(tr1ton)")
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
                offset += 8
                proc_value_3 = struct.unpack("<L", binary_data[offset:offset+4])[0]
                if (proc_value_3 == 16):
                    print("Offset found")
                    offset -= 4
                    break

    offset_Start_text = struct.unpack("<L", binary_data[offset+8:offset+12])[0]
    print("offset_Start_text: "+str(offset_Start_text))
    offset_End_text = struct.unpack("<L", binary_data[offset+12:offset+16])[0]
    print("offset_End_text: "+str(offset_End_text))

    extracted_data = binary_data[offset+offset_Start_text:offset+offset_End_text]
    text_data = extracted_data.replace(b'\x00', b'\n')
    decoded_text = text_data.decode('cp1251', 'ignore')
    base_filename = os.path.splitext(args.input_file)[0]
    csv_file_path = f"{base_filename}.csv"
    #csv_file_path = 'output.csv'
    with open(csv_file_path, 'w', encoding='cp1251') as csv_file:
        csv_file.write(decoded_text)

    print(f"Данные сохранены в {csv_file_path}")

    exit()
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