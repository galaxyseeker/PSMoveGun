import logging
import os

class LoggerUtil:
    @staticmethod
    def setup_logger():
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        # 清除所有现有的处理器
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # 创建一个文件处理器
        log_file = 'PSMoveGun.log'
        
        # 如果日志文件已存在，则删除它
        if os.path.exists(log_file):
            os.remove(log_file)
        
        file_handler = logging.FileHandler(log_file, mode='w')  # 使用 'w' 模式来覆盖文件
        file_handler.setLevel(logging.DEBUG)

        # 创建一个控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 创建一个格式器，并将它添加到处理器
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 将处理器添加到日志记录器
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    @staticmethod
    def debug(message):
        logging.debug(message)

    @staticmethod
    def info(message):
        logging.info(message)

    @staticmethod
    def warning(message):
        logging.warning(message)

    @staticmethod
    def error(message):
        logging.error(message)

    @staticmethod
    def critical(message):
        logging.critical(message)
