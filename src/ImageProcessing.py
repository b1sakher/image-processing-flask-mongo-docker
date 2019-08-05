import urllib.request
import hashlib
import io
from PIL import Image
from database.DataBaseHandler import DataBaseHandler


class ImageProcessing:
    def __init__(self, client):
        self.db_handler = DataBaseHandler(client)

    def __get_md5_from_byte(self, to_hash: bytes):
        """
        Generates the MD5 hash from a bytes image
        :param to_hash: bytes image
        :return: MD5 hash
        """
        if to_hash:
            try:
                return hashlib.md5(to_hash)
            except Exception as ex:
                message = "An exception of type {0} occurred. Arguments:\n{1!r}"
                log = message.format(type(ex).__name__, ex.args)
                self.db_handler.insert_into_monitor_collection(log, "fail")
                return None
        else:
            return None

    def __get_url_content_in_bytes(self, url_input: str):
        """
        Get an image in bytes from a URL
        :param url_input:
        :return: image in bytes
        """
        try:
            with urllib.request.urlopen(url_input) as url:
                return url.read()
        except Exception as ex:
            message = "An exception of type {0} occurred. Arguments:\n{1!r}"
            log = message.format(type(ex).__name__, ex.args)
            self.db_handler.insert_into_monitor_collection(log, "fail")
            return None

    def __byte_to_gray_scale(self, image_bytes):
        """
        Calculate the gray scale representation of an image, notice that GR(I) = (R+B+G)/3
        :param image_bytes:
        :return: gray scale image, height and width
        """
        if image_bytes:
            try:
                gr_img = Image.open(io.BytesIO(image_bytes)).convert('LA')
                width, height = gr_img.size
                img_byte_arr = io.BytesIO()
                gr_img.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                return img_byte_arr, width, height
            except Exception as ex:
                message = "An exception of type {0} occurred. Arguments:\n{1!r}"
                log = message.format(type(ex).__name__, ex.args)
                self.db_handler.insert_into_monitor_collection(log, "fail")
                return None, 0, 0
        else:
            return None, 0, 0

    def __serialize_md5(self, md5):
        """
        Serialize an MD5 hash into hexa
        :param md5:
        :return:
        """
        if md5:
            return md5.hexdigest()
        else:
            return None

    def process_images(self):
        """
        For each link in the input file, fo the following:
        - Get image from Link
        - Generate MD5 hash
        - Calculate Gray scale image
        - Insert data into Mongo DB
        NB: If fail, insert log into MongoDB

        :return: Void
        """
        self.db_handler.delete_all_records_from_monitor_collection()
        self.db_handler.delete_all_records_from_image_collection()
        with open('urls.txt') as f:
            lis = f.readlines()

        for link in lis:
            image = self.__get_url_content_in_bytes(link)
            md = self.__get_md5_from_byte(image)
            gray_scale, width, height = self.__byte_to_gray_scale(image)
            self.db_handler.insert_into_image_collection(self.__serialize_md5(md), gray_scale, width, height)
