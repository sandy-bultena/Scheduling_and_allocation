from pony.orm import *

import sys
from os import path

sys.path.append(path.dirname(path.dirname(__file__)))

from PonyDatabaseConnection import TimeSlot, Block, Lab
import Time_slot as ModelTSlot
from Block import Block as ModelBlock
from Lab import Lab as ModelLab


@db_session
def model_to_entity_lab(m_lab: ModelLab):
    e_lab = Lab(name=m_lab.number, description=m_lab.descr)


@db_session
def model_to_entity(slot: ModelTSlot.TimeSlot):
    """Create an entity TimeSlot from a passed model TimeSlot, storing it in the database."""
    e_slot = TimeSlot(day=slot.day, duration=slot.duration,
                      start=slot.start, movable=slot.movable)


@db_session
def entity_to_model() -> ModelTSlot.TimeSlot:
    """Retrieves an entity TimeSlot from the database and creates a model TimeSlot from it."""
    e_slot = TimeSlot.get(id=1)
    print(e_slot)
    m_slot = ModelTSlot.TimeSlot(e_slot.day, e_slot.start, float(e_slot.duration), e_slot.movable)
    m_slot._TimeSlot__id = ModelTSlot.TimeSlot._max_id = e_slot.id
    return m_slot


@db_session
def model_block_to_entity_block(block: ModelBlock):
    e_slot = TimeSlot(day=block.day, duration=block.duration,
                      start=block.start, movable=block.movable)
    # e_slot.id is listed as NoneType with a value of None, even though the TimeSlot object seems
    # to have been created. Perhaps it's because the changes weren't committed yet?
    flush()
    e_block = Block(time_slot_id=e_slot.id, number=block.number)


@db_session
def get_max_ts_id() -> int:
    """Retrieves the highest TimeSlot ID from the database."""
    val = max(s.id for s in TimeSlot)
    # print(f"Value of select statement is {val}, type {type(val)}.")
    # A max statement will return an integer if any TimeSlots exist in the database, or None.
    max_id = val if val is not None else 0
    return max_id


if __name__ == "__main__":
    # file_path = os.path.realpath(__file__)
    # print(file_path)

    max_ts_id = get_max_ts_id()
    print(max_ts_id)
    # If the max ID is greater than 0, it means the TimeSlot table is not empty.
    # We must therefore ensure that the model TimeSlot class updates its static _max_id field
    # accordingly.
    if max_ts_id > 0:
        ModelTSlot.TimeSlot._max_id = max_ts_id

    t_slot = ModelTSlot.TimeSlot()
    print(f"Created a model TimeSlot: {t_slot.day} {t_slot.start} {str(t_slot.duration)} hours.")
    print("Attempting database insertion by creation of corresponding entity TimeSlot...")

    model_to_entity(t_slot)

    slot = entity_to_model()
    print(f"Created a model TimeSlot: {slot.day} {slot.start} {str(slot.duration)} hours.")

    m_block = ModelBlock("Mon", "9:30", 1.5, 420)
    print(f"Created a model Block: {m_block}")
    model_block_to_entity_block(m_block)

    lab = ModelLab(descr="Test")
    print(f"Created a model Lab: {lab}")
    model_to_entity_lab(lab)
