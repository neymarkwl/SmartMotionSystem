import datetime
import mysql.connector


class MotionDBHelper:
    def __init__(self, host="localhost", user="root", password="root123", database="motion_db"):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        """建表（如果不存在）"""
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS motion_records
                            (
                                id
                                INT
                                AUTO_INCREMENT
                                PRIMARY
                                KEY,
                                motion_type
                                VARCHAR
                            (
                                50
                            ),
                                count INT,
                                duration INT,
                                calorie FLOAT,
                                create_time DATETIME
                                )
                            ''')
        self.conn.commit()

    def add_record(self, motion_type, count, duration, calorie):
        """添加一条运动记录"""
        sql = "INSERT INTO motion_records VALUES (NULL, %s, %s, %s, %s, %s)"
        self.cursor.execute(sql, (motion_type, count, duration, calorie, datetime.datetime.now()))
        self.conn.commit()

    def get_all_records(self):
        """查询所有历史记录（按时间倒序）"""
        self.cursor.execute("SELECT * FROM motion_records ORDER BY create_time DESC")
        return self.cursor.fetchall()

    # 统计页面专用查询方法
    def get_records_by_date(self, date):
        """按日期查询记录"""
        sql = "SELECT * FROM motion_records WHERE DATE(create_time) = %s"
        self.cursor.execute(sql, (date,))
        return self.cursor.fetchall()

    def get_week_records(self):
        """按周查询记录"""
        sql = "SELECT * FROM motion_records WHERE YEARWEEK(create_time) = YEARWEEK(NOW())"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_month_records(self):
        """按月查询记录"""
        sql = "SELECT * FROM motion_records WHERE MONTH(create_time) = MONTH(NOW()) AND YEAR(create_time) = YEAR(NOW())"
        self.cursor.execute(sql)
        return self.cursor.fetchall()