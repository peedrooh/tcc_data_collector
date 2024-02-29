import os
import board
import time 
import tty, sys, termios

from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306


picam2 = Picamera2();
camera_config = picam2.create_preview_configuration();
picam2.configure(camera_config);
encoder = H264Encoder(bitrate=10000000);

filedescriptor = termios.tcgetattr(sys.stdin);
tty.setcbreak(sys.stdin);
key=0;

#i2c = board.I2C();
def oled_setup(i2c:board.I2C = board.I2C(), width:int = 128, height:int = 64, addr = 0x3C, font_path:str = "/home/pedro/.fonts/Archivo-Bold.ttf"):
    oled = adafruit_ssd1306.SSD1306_I2C(width, height, i2c, addr=addr);
    oled.fill(0);
    oled.show();
    image = Image.new("1", (oled.width, oled.height));
    draw = ImageDraw.Draw(image);
    font = ImageFont.truetype("/home/pedro/.fonts/Archivo-Bold.ttf", 12);

    return (oled, image, draw, font);

def get_dirs(directory_path: str):
    dirs = [];
    for entry in os.listdir(directory_path):
        if(os.path.isdir(os.path.join(directory_path, entry)) and "collected_data_" in entry):
            dirs.append(entry);
    return dirs;

def get_files(directory_path: str):
    files = [];
    for entry in os.listdir(directory_path):
        if(not os.path.isdir(os.path.join(directory_path, entry)) and "position_" in entry):
            files.append(entry);
    return files;

def draw_text(draw: ImageDraw.Draw, oled: adafruit_ssd1306.SSD1306_I2C, title:str = "", line1:str = "", line2:str = "", line3:str = ""):
    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0);
    draw.text((0, 0), title, font=font_archivo, fill=255);
    draw.text((0, 16), line1, font=font_archivo, fill=255);
    draw.text((0, 32), line2, font=font_archivo, fill=255);
    draw.text((0, 48), line3, font=font_archivo, fill=255);
    oled.image(image);
    oled.show();

def photoshoot_procedure(cam, oled: adafruit_ssd1306.SSD1306_I2C, image: ImageDraw, draw: ImageDraw.Draw, font_archivo: ImageFont, title:str = "", msg:str = "", wait_time:int = 5, dir_base_path:str = "./data/collected_data_0"):
    files = get_files(dir_base_path);
    file_name = f'position_{len(files)+1}.jpg';
    
    draw_text(draw, oled, title, "", msg);
    time.sleep(wait_time);
    
    cam.start();
    for i in reversed(range(2)):
        draw_text(draw, oled, title, "", f'Foto em {i+1} segundos', "");
        time.sleep(1);
    cam.capture_file(dir_base_path + "/" + file_name);

def loop(oled: adafruit_ssd1306.SSD1306_I2C, image: ImageDraw, draw: ImageDraw.Draw, font_archivo: ImageFont):
    dir_base_path = "./data";
    dirs = get_dirs(dir_base_path);
    new_dir_path = "collected_data_" + str(len(dirs) + 1);
    while(1):
        dirs = sorted(get_dirs("./data"));
        new_dir_index = len(dirs);

        draw_text(draw, oled, "Image Logger", "Pressione Enter para", "iniciar secao de fotos");

        for line in sys.stdin:
            if 'Exit' == line.rstrip():
                break;

            dir_base_path = "./data";
            dirs = get_dirs(dir_base_path);
            new_dir_name = "collected_data_" + str(len(dirs) + 1);
            dir_path = dir_base_path + "/" + new_dir_name;

            os.mkdir(dir_path);
            
            photoshoot_procedure(picam2, oled, image, draw, font_archivo, "Posicao 1 - Frente", "Posicionar na frente.", 3, dir_path);
            photoshoot_procedure(picam2, oled, image, draw, font_archivo, "Posicao 2 - Frente", "Rotacionar 90 graus", 3, dir_path);
            photoshoot_procedure(picam2, oled, image, draw, font_archivo, "Posicao 3 - Frente", "Rotacionar 180 graus", 3, dir_path);
            photoshoot_procedure(picam2, oled, image, draw, font_archivo, "Posicao 4 - Atras", "Posicionar atras", 3, dir_path);
            photoshoot_procedure(picam2, oled, image, draw, font_archivo, "Posicao 5 - Atras", "Rotacionar 90 graus", 3, dir_path);
            photoshoot_procedure(picam2, oled, image, draw, font_archivo, "Posicao 6 - Atras", "Rotacionar 180 graus", 3, dir_path);
            photoshoot_procedure(picam2, oled, image, draw, font_archivo, "Posicao 7 - Diagonal1", "Posicionar diagonal 1", 3, dir_path);
            photoshoot_procedure(picam2, oled, image, draw, font_archivo, "Posicao 8 - Diagonal1", "Rotacionar 90 graus", 3, dir_path);
            photoshoot_procedure(picam2, oled, image, draw, font_archivo, "Posicao 9 - Diagonal1", "Rotacionar 180 graus", 3, dir_path);
            photoshoot_procedure(picam2, oled, image, draw, font_archivo, "Posicao 10 - Diagonal2", "Posicionar diagonal 2", 3, dir_path);
            photoshoot_procedure(picam2, oled, image, draw, font_archivo, "Posicao 11 - Diagonal2", "Rotacionar 90 graus", 3, dir_path);
            photoshoot_procedure(picam2, oled, image, draw, font_archivo, "Posicao 12 - Diagonal2", "Rotacionar 180 graus", 3, dir_path);

            output = dir_path + '/video.h264';
            draw_text(draw, oled, "Video", "", "Gravando video...");
            picam2.start_recording(encoder, output);
            time.sleep(15);
            picam2.stop_recording();

            termios.tcflush(sys.stdin, termios.TCIOFLUSH);
            break;

if __name__ == "__main__":
    oled, image, draw, font_archivo = oled_setup();
    loop(oled, image, draw, font_archivo);

