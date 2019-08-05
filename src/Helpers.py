import database.config as db_conf


def get_data_instance(md5: bytes, gray_scale: bytes, width: int, height: int) -> dict:
    if md5 and gray_scale is not None:
        data = dict()
        data[db_conf.feat_pic_md5] = md5
        data[db_conf.feat_pic_gray_scale] = gray_scale
        data[db_conf.feat_pic_width] = width
        data[db_conf.feat_pic_height] = height
        return data
    else:
        return None


def generate_log(reason: str, state: str):
    if reason:
        data = dict()
        data[db_conf.feat_mon_reason] = reason
        data[db_conf.feat_mon_state] = state
        return data
    else:
        return None
