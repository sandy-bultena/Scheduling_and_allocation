from pony.orm import *

# Test database to verify that Pony works. Anything done here won't affect the main scheduler_db.
db_name = "pony_scheduler_db"

db = Database()


# Create all the Entity classes.
class Lab(db.Entity):
    id = PrimaryKey(int)
    name = Required(str)
    description = Required(str)


# Binds all entities created in this script to the specified database.
# If the database doesn't exist, it will be created. (I hope)
db.bind(provider='mysql',
        host='10.101.0.27',
        user='evan_test',
        passwd='test_stage_pwd_23',
        db=db_name,
        create_db=True)

# Map the Entity classes to the database tables once the entities have been defined and the
# database has been bound.
