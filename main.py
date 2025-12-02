#! /usr/bin/env python

import pylibmc
import mysql.connector

def test_single_store():
    cnx = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="test",
    )

    cur = cnx.cursor()
    cur.execute("CREATE DATABASE IF NOT EXISTS 'test';")
    cur.execute("SELECT 'hello from singlestore';")
    print(cur.fetchone())

    cur.close()
    cnx.close()


def test_mem_cached():
    mc = pylibmc.Client(["127.0.0.1"], binary=True)

    mc.set("username", "alice", time=300)
    print(mc.get("username"))

def main():
    test_single_store()
    test_mem_cached()

if __name__ == "__main__":
    main()
