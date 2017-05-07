# Custom Settings
from os import environ

SERVER_RDB = 'server2.memento.live'
SERVER_RDB_INFO = {
                        "host": SERVER_RDB,
                        "user": 'memento',
                        "passwd": environ['MEMENTO_PASS'],
                        "db": 'memento',
                        "charset": 'utf8mb4',
                        "port": 3306
                    }
SERVER_PDB = 'http://server1.memento.live'
SERVER_PDB_INFO = {
                        "host": SERVER_PDB,
                        "user": 'memento',
                        "passwd": environ['MEMENTO_PASS'],
                        "db": 'memento',
                        "charset": 'utf8mb4',
                        "port": 3306
                    }
SERVER_API = 'http://server1.memento.live:8080/api/persist/'
SERVER_API_HEADER = { "Content-Type" : "application/json",
                      "charset": "utf-8",
                      "Authorization": environ['MEMENTO_BASIC']}