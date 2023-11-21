import csv
import struct
import os
import argparse

def read_binary_file(filename):
    with open(filename, 'rb') as f:
        return f.read()

def read_csv_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        return [(row[0], row[1], row[2]) for row in reader]

def write_binary_file(filename, data):
    filepath = os.path.join('new_files', filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'wb') as f:
        f.write(data)

def main():
    print("MGS3 *.gcx Import by Giza(tr1ton)")
    parser = argparse.ArgumentParser(description="Import texts from a binary file")
    parser.add_argument("input_file", help="Input binary file name")
    args = parser.parse_args()

    binary_data = read_binary_file(args.input_file)
    base_filename = os.path.splitext(args.input_file)[0]
    read_csvfile = f"{base_filename}.csv"
    csv_data = read_csv_file(read_csvfile)

    offset = binary_data.find(b'\x00\x00\x00\x00\x18\x00\x00\x00')
    if offset == -1:
        print('Hex sequence not found in binary file')
        return
    offset_end=offset-16
    offset_end_int=struct.unpack('<I', binary_data[offset_end:offset_end+4])[0]
    print(f"offset_end: {offset_end_int}")

    #new_offset = len(binary_data)-(offset+8)
    new_offset = (offset_end+offset_end_int)-(offset+8)
    print(f"new_offset: {new_offset}")

    new_offset_end=(offset_end_int)+(offset-16)
    print(f"new_offset_end: {new_offset_end}")

    text_count = struct.unpack('<I', binary_data[offset+8:offset+12])[0]
    print(f'gcx_text_count: {text_count}')
    print(f'csv_text_count: {len(csv_data)}')
    #print(f'csv_text: {csv_data[870][1]}')
    #binary_data = binary_data[:offset+12]
    #binary_data = binary_data[:offset+12] + struct.pack('<I', 100) + binary_data[offset+12:]
    #binary_data = binary_data[:offset+12] + struct.pack('<I', 100) + binary_data[offset+16:]
    if text_count != len(csv_data):
        print('Text count mismatch')
        return

    #binary_data_new = binary_data[:offset+12]
    binary_data_new = binary_data[:offset_end]

    for text in csv_data:
        #print(f'new_offset: {new_offset}')
        if text[0] == "0xffffffff":
            #print(f"text[0]: {text[0]}")
            zero_offset = -1
            #binary_data_new += struct.pack('<I', 0xFFFFFFFF)
        else:
            #binary_data_new += struct.pack('<I', new_offset)
            new_offset += len(text[2].encode('utf-8')) + 1
        #ex_bytes=1

    new_offset_end_2=(new_offset+offset+8)-(offset-16)
    print(f'new_offset_end_2: {new_offset_end_2}')
    binary_data_new += struct.pack('<I', new_offset_end_2)

    new_offset = (offset_end+offset_end_int)-(offset+8)

    binary_data_new += binary_data[offset_end+4:offset_end+28]
    #binary_data_new += binary_data[offset_end+4:offset_end+28]
    
    #binary_data = binary_data[:offset+12] + struct.pack('<I', new_offset) + binary_data[offset+12:]
    #binary_data += struct.pack('<I', new_offset)
    for text in csv_data:
        #print(f'new_offset: {new_offset}')
        if text[0] == "0xffffffff":
            #print(f"text[0]: {text[0]}")
            zero_offset = -1
            binary_data_new += struct.pack('<I', 0xFFFFFFFF)
        else:
            binary_data_new += struct.pack('<I', new_offset)
            new_offset += len(text[2].encode('utf-8')) + 1
        #ex_bytes=1
    
    
    
    #binary_data_new += binary_data[offset+8+4+(text_count*4):]
    binary_data_new += binary_data[offset+8+4+(text_count*4):new_offset_end]
    #print(f"test {offset+8+4+(text_count*4)}")

    for text in csv_data:
        #print(f'text: {text[2]}')
        #binary_data += struct.pack('<I', new_offset)
        if text[0] != "0xffffffff":
            binary_data_new += text[2].encode('utf-8') + b'\x00'
        #new_offset += len(text[2]) + 1

    binary_data_new += binary_data[new_offset_end:]

    write_binary_file(args.input_file, binary_data_new)

if __name__ == '__main__':
    main()