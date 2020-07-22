from PIL import Image       # working with images
import numpy                # converting numbers to binary
import os                   # checking the size of a file


def prepare_textfile(file_name):
    """
    :param file_name: name of the source text file (string)
    adds dots to the end of the file (needed to mark the end for deciphering)
    """
    f = open(file_name, "a")
    f.write(".......")
    f.close()


def read_textfile_bin(file_name):
    """
    :param file_name: name of the source text file (string)
    :return: list of bytes of the file as 8-bit number
    converts characters according to the ascii table
    """
    f = open(file_name, "r")
    curr = ' '
    res = []
    while curr != '':
        curr = f.read(1)
        if curr != '':
            ascii = ord(curr)
            bnum = numpy.binary_repr(ascii, width=8)
            res.append(bnum)

    f.close()
    return res


def divide_bin_by_2bits(bin_str, list):
    """
    :param bin_str: 8-bit number converted to str
    :param list: list with 2-bit parts
    :return: updated list - bin_str divided by 2 bits, appended to end of list
    """
    curr = ''
    for i in bin_str:
        if len(curr) < 2:
            curr += i
        else:
            list.append(curr)
            curr = i
    if curr != '':
        list.append(curr)


def divide_input_by_2bits(input_list):
    """
    :param input_list: list of 8-bit integers
    :return: list of input integers divided by 2 bits
    """
    res = []
    for bin in input_list:
        divide_bin_by_2bits(bin, res)
    return res


def copy_image(img_name):
    """
    :param img_name: name of input image (string)
    :return: copy of the image object
    :return: raster of the copy
    creates a black image of the same size, then copies the image pixel by pixel
    """
    img = Image.open(img_name)
    px = img.load()
    new_img = Image.new(img.mode, img.size)
    new_px = new_img.load()
    width, height = new_img.size
    for i in range(width):
        for j in range(height):
            new_px[i,j] = px[i,j]
    return new_img, new_px


def replace_last_2bits(bin_str, last_bits):
    """
    :param bin_str: 8-bit number converted to str
    :param last_bits: 2 bits
    :return: bin_str with last 2 bits replaced by last_bits
    """
    cropped = bin_str[:-2]
    new = cropped + last_bits
    return new


def new_col_channel(col_channel, new_bits):
    """
    :param col_channel: int in decimal (0-255)
    :param new_bits: 2 bits of input message
    :return: colour channel with 2 bits ciphred inside
    converts col_channel to binary 8-bit num, replaces last 2 bits by new_bits, then converts back to decimal
    """
    col_bin = numpy.binary_repr(col_channel, width=8)
    new_col_bin = replace_last_2bits(col_bin, new_bits)
    new_col = int(new_col_bin, 2)
    return new_col


def new_rgba(rgba, new_bits, pos):
    """
    :param rgba: tuple representing a pixel
    :param new_bits: 2 bits which we want to cipher to one of the colour channels
    :param pos: position of the channel we want to use in the rgba tuple
    :return: new rgba tuple with one channel changed
    """
    r = rgba[0]
    g = rgba[1]
    b = rgba[2]
    a = rgba[3]
    if pos == 0:
        new_r = new_col_channel(r, new_bits)
        return (new_r, g, b, a)
    if pos == 1:
        new_g = new_col_channel(g, new_bits)
        return (r, new_g, b, a)
    if pos == 2:
        new_b = new_col_channel(b, new_bits)
        return (r, g, new_b, a)


def cipher_to_image(img_name, source_name):
    """
    :param img_name: name of input image (string)
    :param source_name: name of input text file (string)
    :return: new image with the text file ciphered inside (saves img to disk and shows it)
    creates a copy of input img and ciphers into the copy
    each pixel contains 4 channels (rgba), function uses only 3 (rgb) - since PNG img usually has a transparent background, by changing the alpha channel, changes could be visible in the background
    the message is ciphred by changing last 2 bits of a colour channel in a pixel to 2 bits of input text file
    change of the result pixel colour is not visible by human eye
    """
    prepare_textfile(source_name)
    ciph_bin = read_textfile_bin(source_name)
    ciph_chunks = divide_input_by_2bits(ciph_bin)

    img, px = copy_image(img_name)
    width, height = img.size

    idx = 0
    for i in range(width):
        for j in range(height):
            pos = 0             # pos - position of a colour channel in tuple representing a pixel
            while pos < 3:      # goes through 3 colour channels (rgb)
                if idx != len(ciph_chunks):
                    chunk = ciph_chunks[idx]
                    rgba = px[i, j]
                    px[i, j] = new_rgba(rgba, chunk, pos)
                    idx += 1
                    pos += 1
                else:
                    break

    img.save(img_name[:-3] + "cipher.png", format="PNG" )
    img.show()




def join_bin(bin_list):
    """
    :param bin_list: list of bits converted to str
    :return: 1 string with all bits from bin_list joined together
    """
    res = ''
    for i in bin_list:
        res += i
    return res


def bin_to_char(bin):
    """
    :param bin: 8-bit binary number
    :return: character represented by bin in the ascii table
    """
    num = int(bin, 2)
    char = chr(num)
    return char


def copy_last_2bits(bits):
    """
    :param bits: bits/number in binary
    :return: last 2 bits converted to str
    """
    s = str(bits)
    last = s[len(s) - 2:]
    return last


def decipher_image(img_name):
    """
    :param img_name: name of image with ciphred message
    :return: text file with deciphred message saved to disk
    function goes through pixels, reads last 2 bits from rgb channels and puts them to list
    when there is 1 byte in the list, it converts the byte to a character and writes it to result file
    end of the message is marked by 5 dots, when the function writes 5 consecutive dots, it stops deciphering
    """
    result_name = img_name[:-3] + "result.txt"      # suffix png is cropped from img_name
    f = open(result_name, "w")
    img = Image.open(img_name)
    px = img.load()
    width, height = img.size

    char_list = []
    before = ''
    dot_count = 0
    is_end = False
    for i in range(width):
        if is_end:
            break
        for j in range(height):
            if is_end:
                break
            for pos in range(3):            # reads from 3 colour channels only, alpha channel is not used for ciphering
                if len(char_list) == 4:     # 4 parts by 2 bits create 1 byte
                    char_bin = join_bin(char_list)
                    char = bin_to_char(char_bin)
                    f.write(char)
                    if before == "." and char == ".":
                        dot_count += 1
                    else:
                        dot_count = 0
                    if dot_count >= 5:
                        is_end = True
                    if is_end:
                        break
                    before = char
                    char_list = []
                bin = numpy.binary_repr(px[i,j][pos], width=8)
                part = copy_last_2bits(bin)
                char_list.append(part)

    f.close()


def get_file_name():
    """
    :return: file name (string)
    reads input from user then tries to open a file with the input name
    if file doesn't exist, prints an error message, cycle repeats until existing file name is given
    """
    not_valid = True
    while not_valid:
        file_name = input()
        try:
            f = open(file_name)
            not_valid = False
            f.close()
        except FileNotFoundError:
            print("File not found. Please try again.")

    return file_name


def is_enough_space(img_name, text_name):
    """
    :param img_name: name of input image (string)
    :param text_name: name of input text file (string)
    :return: True/False - is the img big enough to fit the ciphred text inside
    """
    text_size = os.stat(text_name).st_size
    img = Image.open(img_name)
    width, height = img.size
    img_space = (width * height * 3) // 4      # (num of pixels * 3 col channels) =  how many 2 bit parts it can fit, //4 to get bytes
    if text_size < img_space:
        return True
    else:
        return False


def run():
    """
    user interface of the programme, user chooses to cipher or decipher and types the names of files
    function checks if the img is big enough to fit the ciphred text inside
    """
    print("Do you want to [c]ipher or [d]ecipher?")
    not_valid = True
    while not_valid:
        answer = input()
        if answer == 'c' or answer == 'd':
            not_valid = False
        else:
            print(answer + ' is not a valid input, type "c" for cipher or "d" for decipher')

    if answer == 'c':
        print("Type the name of your source text file here:")
        text_name = get_file_name()

        print("Type the image name:")
        img_name = get_file_name()

        if is_enough_space(img_name, text_name):
            cipher_to_image(img_name, text_name)
            print("Result was saved as: " + img_name[:-3] + "cipher.png")
        else:
            print("Chosen image is too small for the input text file size.")

    if answer == 'd':
        print("Type the name of image you want to deciper:")
        img_name = get_file_name()

        decipher_image(img_name)
        print("The cipher text was saved as: " + img_name[:-3] + "result.txt")



run()




