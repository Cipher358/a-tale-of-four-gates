import os

import mysql.connector


class DatabaseInterface:

    def __init__(self):
        self.endpoint = "cp55.ckxgs3folg2a.eu-west-1.rds.amazonaws.com"
        self.port = "3306"
        self.user = "admin"
        self.passwd = os.environ["CP55PASSWD"]
        self.db_name = "cp55"

    def get_connection(self):
        try:
            conn = mysql.connector.connect(host=self.endpoint, user=self.user, passwd=self.passwd,
                                           port=self.port, database=self.db_name)
            return conn
        except Exception as e:
            print("Database connection failed due to {}".format(e))

    def insert_app(self, package_name, analysis_status):
        query = "INSERT INTO apps (package_name, analysis_status) VALUES (%s, %s);"
        values = (package_name, analysis_status)

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, values)

        conn.commit()

        return cursor.lastrowid

    def insert_components(self, app_id, components):
        for component in components:
            component["app_id"] = app_id

        query = "INSERT INTO components (app_id, name, type, enabled, exported, direct_boot_aware, filter_matches, " \
                "permission, authorities, grant_uri_permission, write_permission, read_permission, has_sql, " \
                "foreground_service_type) " \
                "VALUES (%(app_id)s, %(name)s, %(type)s, %(enabled)s, %(exported)s, %s(direct_boot_aware)s, " \
                "%(filter_matches)s, %(permission)s, %s(authorities), %(grant_uri_permission)s, " \
                "%(write_permission)s, %(read_permission)s, %(has_sql)s, %(foreground_service_type)s);"

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.executemany(query, components)

        conn.commit()

        return cursor.lastrowid
