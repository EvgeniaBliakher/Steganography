from PIL import Image
import numpy
import os


def prepare_textfile(file_name):
    f = open(file_name, "a")
    f.write(".......")
    f.close()


def read_textfile_bin(file_name):
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
    res = []
    for bin in input_list:
        divide_bin_by_2bits(bin, res)
    return res


def replace_last_2bits(bin_str, last_bits):
    cropped = bin_str[:-2]
    new = cropped + last_bits
    return new


def new_col_channel(col_channel, new_bits):
    col_bin = numpy.binary_repr(col_channel, width=8)
    new_col_bin = replace_last_2bits(col_bin, new_bits)
    new_col = int(new_col_bin, 2)
    return new_col


def new_rgba(rgba, new_bits, pos):
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


def copy_image(img_name):
    img = Image.open(img_name)
    px = img.load()
    new_img = Image.new(img.mode, img.size)
    new_px = new_img.load()
    width, height = new_img.size
    for i in range(width):
        for j in range(height):
            new_px[i,j] = px[i,j]
    return new_img, new_px


def cipher_to_image(img_name, source_name):
    prepare_textfile(source_name)
    ciph_bin = read_textfile_bin(source_name)
    ciph_chunks = divide_input_by_2bits(ciph_bin)

    img, px = copy_image(img_name)
    width, height = img.size

    idx = 0
    for i in range(width):
        for j in range(height):
            pos = 0
            while pos < 3:
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
    res = ''
    for i in bin_list:
        res += i
    return res


def copy_last_2bits(bits):
    s = str(bits)
    last = s[len(s) - 2:]
    return last


def bin_to_char(bin):
    num = int(bin, 2)
    char = chr(num)
    return char


def decipher_image(img_name):
    result_name = img_name[:-3] + "result.txt"
    f = open(result_name, "w")
    # f.close()
    # f = open(result_name, "a")
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
            for pos in range(3):
                if len(char_list) == 4:
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


def is_enough_space(img_name, text_name):
    text_size = os.stat(text_name).st_size
    img = Image.open(img_name)
    width, height = img.size
    img_space = (width * height * 3 ) // 4
    if text_size < img_space:
        return True
    else:
        return False


def run():
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
        text_name = input()
        print("Type the image name:")
        img_name = input()

        if is_enough_space(img_name, text_name):
            cipher_to_image(img_name, text_name)
            print("Result was saved as: " + img_name[:-3] + "cipher.png")
        else:
            print("Chosen image is too small for the input text file size.")

    if answer == 'd':
        print("Type the name of image you want to deciper:")
        img_name = input()

        decipher_image(img_name)
        print("The cipher text was saved as: " + img_name[:-3] + "result.txt")



run()




# cipher_to_image("cat1.png", "text.txt")
# decipher_image("cat1.cipher.png")

