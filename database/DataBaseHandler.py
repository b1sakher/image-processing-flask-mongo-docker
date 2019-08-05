import database.config as db_conf
import time
import src.Helpers as Helpers


class DataBaseHandler:
    def __init__(self, client):
        self.client = client
        self.db = self.client[db_conf.DATABASE_NAME]
        self.pictures_collection = self.db[db_conf.COLLECTION_PICTURES]
        self.monitor_collection = self.db[db_conf.COLLECTION_MONITORING]
        self.__create_image_collection_index()

    def __create_image_collection_index(self):
        """
        Creates an index on MD5
        :return: VOID
        """
        self.pictures_collection.create_index(db_conf.feat_pic_md5, unique=True)

    def insert_into_image_collection(self, md5, gray_scale, width, height):
        """
        Inserts a new document into Pictures collection in MongoDB
        :param md5:
        :param gray_scale:
        :param width:
        :param height:
        :return: VOID
        """
        data_input = Helpers.get_data_instance(md5, gray_scale, width, height)
        if data_input is not None:
            try:
                ts = time.time()
                data_input[db_conf.feat_pic_timestamp] = ts
                result = self.pictures_collection.insert_one(data_input)
                log = 'One post: {0}'.format(result.inserted_id)
                print(log)
                self.insert_into_monitor_collection(log, "success")
            except Exception as ex:
                message = "An exception of type {0} occurred. Arguments:\n{1!r}"
                log = message.format(type(ex).__name__, ex.args)
                print(log)

    def insert_into_monitor_collection(self, log, state):
        """
        Inserts a new document into Monitor collection, served to monitor the process
        :param log:
        :param state: Success or Fail
        :return: VOID
        """
        data_input = Helpers.generate_log(log, state)
        if data_input is not None:
            try:
                ts = time.time()
                data_input[db_conf.feat_mon_timestamp] = ts
                result = self.monitor_collection.insert_one(data_input)
                log = 'One post: {0}'.format(result.inserted_id)
                print(log)
            except Exception as ex:
                message = "An exception of type {0} occurred. Arguments:\n{1!r}"
                log = message.format(type(ex).__name__, ex.args)
                print(log)

    def delete_all_records_from_image_collection(self):
        self.pictures_collection.delete_many({})

    def delete_all_records_from_monitor_collection(self):
        self.monitor_collection.delete_many({})




