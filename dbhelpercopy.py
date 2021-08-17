import sqlite3

class DBHelper:
  def __init__(self, dbname="todo2.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

  def setup(self):
    tblstmt = "CREATE TABLE IF NOT EXISTS cowin (owner integer PRIMARY KEY,state text, district text)"
    stateidx = "CREATE INDEX IF NOT EXISTS stateIndex ON cowin (state ASC)"
    districtidx = "CREATE INDEX IF NOT EXISTS districtIndex ON cowin (district ASC)" 
    ownidx = "CREATE INDEX IF NOT EXISTS ownIndex ON cowin (owner ASC)"
    self.conn.execute(tblstmt)
    self.conn.execute(stateidx)
    self.conn.execute(districtidx)
    self.conn.execute(ownidx)
    self.conn.commit()
  
  def add_item(self, state, district,owner):
    stmt = "INSERT or REPLACE INTO cowin (state,district, owner) VALUES (?,?, ?)"
    args = (state,district, owner)
    self.conn.execute(stmt, args)
    self.conn.commit()

  def add_state(self, state, owner):
    stmt = "INSERT OR REPLACE INTO cowin (owner,state) VALUES (?,?)"
    args = (owner,state)
    self.conn.execute(stmt, args)
    self.conn.commit()
  
  def check_if_id_exists(self,owner):
    stmt = "SELECT EXISTS(SELECT 1 FROM cowin WHERE owner = (?))"
    args = (owner, )
    self.conn.execute(stmt, args)
 
  def update_state(self,state,owner):
    stmt = "UPDATE cowin SET state = (?) WHERE owner = (?)"
    args = (state, owner)
    self.conn.execute(stmt, args)
    self.conn.commit()

  def update_district(self,district,owner):
    stmt = "UPDATE cowin SET district = (?) WHERE owner = (?)"
    args = (district, owner)
    self.conn.execute(stmt, args)
    self.conn.commit()

  def add_district(self, district,state,owner):
    stmt = "INSERT OR REPLACE INTO cowin (district,state,owner) VALUES (?,?,?)"
    args = (district,state, owner)
    self.conn.execute(stmt, args)
    self.conn.commit()

  def delete_item(self, owner):
    stmt = "DELETE state , district FROM cowin WHERE owner = (?)"
    args = (owner,)
    self.conn.execute(stmt, args)
    self.conn.commit()

  def delete_all_items(self, owner):
    stmt = "DELETE FROM cowin WHERE owner = (?)"
    args = (owner, )
    self.conn.execute(stmt, args)
    self.conn.commit()

  def get_items(self, owner):
    stmt = "SELECT state FROM cowin WHERE owner = (?)"
    args = (owner, )
    return [x[0] for x in self.conn.execute(stmt, args)]
  
  def get_state(self,owner):
    stmt = "SELECT state FROM cowin WHERE owner= (?)"
    args = (owner, )
    result = self.conn.execute(stmt,args).fetchone()
    return result[0]

  def get_district(self,owner):
    stmt = "SELECT district FROM cowin WHERE owner= (?)"
    args = (owner, )
    result = self.conn.execute(stmt,args).fetchone()
    return result[0]
  def get_all_Data(self):
    stmt = "SELECT * FROM cowin"
    result = self.conn.execute(stmt).fetchall()
    print("Total rows are:  ", len(result))
    print("Printing each row")
    for row in result:
        print("owner: ", row[0])
        print("state: ", row[1])
        print("district: ", row[2])
        print("\n")
    return (result)

  def addowner(self,owner):
    stmt = "INSERT OR IGNORE INTO cowin (owner) VALUES (?) "
    args = (owner, )
    self.conn.execute(stmt,args)
    self.conn.commit()
      