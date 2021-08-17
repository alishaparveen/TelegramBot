import time
import todobotcopy
from dbhelpercopy import DBHelper


if __name__=="__main__":
  db = DBHelper()
  db.setup()
  last_textchat = (None, None)
  last_update_id = None
  try:
    while True:
      updates = todobotcopy.get_updates(last_update_id)
      if len(updates["result"]) > 0:
        last_update_id = todobotcopy.get_last_update_id(updates) + 1
        todobotcopy.handle_updates(updates)
      time.sleep(0.5)
  except Exception as e:
    print(e)

