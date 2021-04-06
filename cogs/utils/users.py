import sqlite3

def set_val(member: int, name: str, key: str,value: int, guildId: int):
    db = sqlite3.connect('users.db')
    cr = db.cursor()
    if not value == 'get':
        cr.execute('CREATE TABLE IF NOT EXISTS users(member INTEGER, name TEXT, total_warnings INTEGER, current_warnings INTEGER, server INTEGER)')
        cr.execute('SELECT member, name, total_warnings, current_warnings, server FROM users WHERE member = (?) AND server = (?)',(member,guildId))

        rows = cr.fetchall()
        if len(rows)==0:
            cr.execute(f"INSERT INTO users (member, name, total_warnings, current_warnings, server) VALUES (?, ?, ?, ?, ?)",
                        (member,name, 0, 0, guildId))
            db.commit()
            cr.execute(f"UPDATE users SET {key} = (?) WHERE member = (?) AND server = (?)",
                            (value,member,guildId))
            db.commit()
        else:
            for row in rows:
                if int(row[0]) == member and int(row[4]) == int(guildId):
                    cr.execute(f"UPDATE users SET {key} = (?) WHERE member = (?) AND server = (?)",
                                (value,member,guildId))
                    db.commit()
                    break
        cr.close()
        db.close()
        val = get_val(member,key, guildId)
        return val

def get_val(member:int, key: str, guildId: int):
    db = sqlite3.connect('users.db')
    cr = db.cursor()
    cr.execute(f'SELECT member,{key}, server FROM users WHERE member = (?) AND server = (?)',(member,guildId))
    val = False
    for row in cr.fetchall():
        if row[0] == member and row[2] == guildId:
            val = row[1]
    cr.close()
    db.close()
    return val

def get_member(member:int, guildId: int):
    db = sqlite3.connect('users.db')
    cr = db.cursor()
    cr.execute('SELECT member, total_warnings, current_warnings, server FROM users WHERE member = (?) AND server = (?)',(member,guildId))
    val = False
    for row in cr.fetchall():
        if row[0] == member and row[3] == guildId:
            val = [row[1],row[2]]
            break
    cr.close()
    db.close()
    return val

def increment_val(member:int, key:str, guildId:int):
    found = get_val(member,key,guildId)
    if found is False:
        return False
    db = sqlite3.connect('users.db')
    cr = db.cursor()
    cr.execute(f"UPDATE users SET {key} = {key} + 1 WHERE member = (?) AND server = (?)",
                            (member,guildId))
    db.commit()
    cr.close()
    db.close()
    return get_val(member,key, guildId)

def decrement_val(member:int, key:str, guildId:int):
    found = get_val(member,key,guildId)
    if found is False:
        return False
    db = sqlite3.connect('users.db')
    cr = db.cursor()
    cr.execute(f"UPDATE users SET {key} = {key} - 1 WHERE member = (?) AND server = (?)",
                            (member,guildId))
    db.commit()
    cr.close()
    db.close()
    return get_val(member,key, guildId)

def get_table():
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS users(member INTEGER, name TEXT, total_warnings INTEGER, current_warnings INTEGER, server INTEGER)')
    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()
    cur.close()
    db.close()
    return rows