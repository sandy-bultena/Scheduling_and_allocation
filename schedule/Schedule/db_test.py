from pony.orm import db_session

from database.PonyDatabaseConnection import *
import Time_slot as ModelTSlot


@db_session
def model_to_entity(slot: ModelTSlot.TimeSlot):
    e_slot = TimeSlot(id=slot.id, day=slot.day, duration=slot.duration,
                      start=slot.start, movable=slot.movable)


if __name__ == "__main__":
    t_slot = ModelTSlot.TimeSlot()
    print(f"Created a model TimeSlot: {t_slot.day} {t_slot.start} {str(t_slot.duration)} hours.")
    print("Attempting database insertion by creation of corresponding entity TimeSlot...")
    model_to_entity(t_slot)
