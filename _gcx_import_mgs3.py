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
    offset_end_int_1=struct.unpack('<I', binary_data[offset_end:offset_end+4])[0]
    offset_end_int_2=struct.unpack('<I', binary_data[offset_end+4:offset_end+8])[0]
    offset_end_int_3=struct.unpack('<I', binary_data[offset_end+8:offset_end+12])[0]
    offset_end_int_4=struct.unpack('<I', binary_data[offset_end+12:offset_end+16])[0]
       
    print(f"offset_end_int_1: {offset_end_int_1}")   
    print(f"offset_end_int_2: {offset_end_int_2}")   
    print(f"offset_end_int_3: {offset_end_int_3}") 
    print(f"offset_end_int_4: {offset_end_int_4}")  

    #оффсет с начала файла
    new_offset_end=(offset_end_int_2)+(offset-16)
    print(f"new_offset_end: {new_offset_end}")

    text_count = struct.unpack('<I', binary_data[offset+8:offset+12])[0]
    print(f'gcx_text_count: {text_count}')
    print(f'csv_text_count: {len(csv_data)}')


    new_offset = (text_count*4)+4
    print(f"new_offset: {new_offset}")
    if text_count != len(csv_data):
        print('Text count mismatch')
        return

    binary_data_new = binary_data[:offset_end]

    for text in csv_data:
        if text[0] == "0xffffffff":
            zero_offset = -1
        else:
            new_offset += len(text[2].encode('utf-8')) + 1

    new_offset_end_2=offset_end_int_1-offset_end_int_4
    new_offset_end_2=(new_offset+offset+8)-(offset-16)+new_offset_end_2
    #print(f'new_offset_end_2: {new_offset_end_2}')
    new_offset_end_3=(new_offset+offset+8)-(offset-16)

    new_offset = (text_count*4)+4

    data_offset=offset_end_int_1-offset_end_int_2
    binary_data_new += struct.pack('<I', new_offset_end_3+data_offset)

    binary_data_new += struct.pack('<I', new_offset_end_3)

    ps2_data_offset=offset_end_int_3-offset_end_int_2
    binary_data_new += struct.pack('<I', new_offset_end_3+ps2_data_offset)

    ps2_data=offset_end_int_4-offset_end_int_2
    binary_data_new += struct.pack('<I', new_offset_end_3+ps2_data)
    binary_data_new += binary_data[offset_end+16:offset_end+28]
    
    for text in csv_data:
        if text[0] == "0xffffffff":
            zero_offset = -1
            binary_data_new += struct.pack('<I', 0xFFFFFFFF)
        else:
            binary_data_new += struct.pack('<I', new_offset)
            new_offset += len(text[2].encode('utf-8')) + 1
    
    for text in csv_data:
        if text[0] != "0xffffffff":
            binary_data_new += text[2].encode('utf-8') + b'\x00'
  
    binary_data_new += binary_data[new_offset_end:]

    write_binary_file(args.input_file, binary_data_new)

if __name__ == '__main__':
    main()