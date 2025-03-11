import os
import sys
import binascii

def dd(ibs, iseek, infile, outfile):
    with open(infile, 'rb') as input_file:
        # 跳过指定数量的块
        skip_bytes = iseek * ibs
        input_file.seek(skip_bytes)

        # 打开输出文件以二进制写入模式
        with open(outfile, 'wb') as output_file:
            # 循环读取输入文件并写入输出文件
            while True:
                # 读取一个输入块的数据
                block = input_file.read(ibs)
                if not block:
                    # 如果没有更多数据，退出循环
                    break
                # 将读取的数据写入输出文件
                output_file.write(block)

def gen_imghdr(addr, ifile, ofile):
    try:
        idata = open(ifile, "rb").read()
    except:
        sys.exit("Could not open input file '{}'".format(ifile))

    vtor = addr
    size = len(idata)
    crc = binascii.crc32(idata)

    odata = vtor.to_bytes(4, byteorder='little') + size.to_bytes(4, byteorder='little') + crc.to_bytes(4, byteorder='little')

    try:
        with open(ofile, "wb") as ofile:
            ofile.write(odata)
    except:
        sys.exit("Could not open output file '{}'".format(ofile))

def combined(NAME, CMAKE_CURRENT_BINARY_DIR, CMAKE_OBJCOPY):
    cwd = os.getcwd()
    os.chdir(CMAKE_CURRENT_BINARY_DIR)
    APP = NAME + '_APP'
    APP_BIN = f'{CMAKE_CURRENT_BINARY_DIR}/{APP}.bin'    
    APP_HDR = f'{CMAKE_CURRENT_BINARY_DIR}/{APP}_hdr.bin'
    COMBINED = f'{NAME}_combined' 
    dd(1024,32, f'{NAME}.bin', APP_BIN)
    gen_imghdr(0x10008000, APP_BIN, APP_HDR)
    os.system(f'{CMAKE_OBJCOPY} --update-section .app_hdr={APP_HDR} {NAME}.elf {COMBINED}.elf')
    os.system(f'{CMAKE_OBJCOPY} -Obinary {COMBINED}.elf {COMBINED}.bin')
    os.chdir(cwd)
    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        combined(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        combined("CNS_10", r'F:\PICO\CNS_10\build\cns10', "D:/gcc-arm-none-eabi-10.3-2021.10/bin/arm-none-eabi-objcopy.exe")
    
