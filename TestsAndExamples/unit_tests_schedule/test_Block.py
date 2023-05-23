import pytest
import sys
from os import path

sys.path.append(path.dirname(path.dirname(__file__) + "/../../"))

from schedule.Schedule.Block import Block
import schedule.Schedule.Block as blk
from schedule.Schedule.Labs import Lab
from schedule.Schedule.Teachers import Teacher
import schedule.Schedule.IDGeneratorCode as id_gen


@pytest.fixture(scope="module", autouse=True)
def before_and_after_module():
    pass


@pytest.fixture(autouse=True)
def run_before():
    pass


# Properties
def test_start_getter():
    """Verifies that the start getter works as intended. Same as the TimeSlot start getter."""
    day = "mon"
    start = "8:30"
    dur = 2
    block = Block(day, start, dur)
    assert block.start == start


def test_day_getter():
    """Verifies that the day getter works as intended. Same as in TimeSlot."""
    day = "mon"
    start = "8:30"
    dur = 2
    block1 = Block(day, start, dur)
    assert block1.day == day


def test_day():
    """Verifies that the day setter works as intended, changing the day property of any Block
    synced_blocks to the current Block. """
    day = "mon"
    start1 = "8:00"
    start2 = "12:00"
    dur = 2
    block1 = Block(day, start1, dur)
    block2 = Block(day, start2, dur)
    block1.sync_block(block2)
    block2.sync_block(block1)
    block1.day = "thu"
    assert block2.day == "thu"


def test_id():
    """Verifies that the id property works as intended."""
    day = "mon"
    start = "8:30"
    dur = 2
    block = Block(day, start, dur)
    old_id = block.id
    block = Block(day, start, dur)
    assert block.id == old_id + 1


def test_id_with_id_given():
    """Verifies that the id property works as intended."""
    blk._block_id_generator = id_gen.get_id_generator()

    day = "mon"
    start = "8:30"
    dur = 2
    existing_id = 12
    block1 = Block(day, start, dur, block_id=existing_id)
    assert block1.id == existing_id
    block2 = Block(day, start, dur)
    assert block2.id == existing_id + 1
    block3 = Block(day, start, dur, block_id=existing_id - 5)
    assert block3.id == existing_id - 5
    block4 = Block(day, start, dur)
    assert block4.id == block2.id + 1


def test_assign_lab_good():
    """Verifies that the assign_lab method can assign a valid Lab object to the Block."""
    day = "mon"
    start = "8:30"
    dur = 2
    block = Block(day, start, dur)
    lab = Lab()
    block.assign_lab(lab)
    assert block.has_lab(lab)


def test_assign_lab_multiple():
    """Verifies that the assign_lab method can assign a valid Lab object to the Block."""
    day = "mon"
    start = "8:30"
    dur = 2
    block = Block(day, start, dur)
    lab1 = Lab()
    lab2 = Lab()
    block.assign_lab(lab1)
    block.assign_lab(lab2)
    labs = block.labs
    assert block.has_lab(lab1)
    assert block.has_lab(lab2)
    assert len(labs) == 2


def test_assign_lab_multiple_with_duplicate():
    """Verifies that the assign_lab method can assign a valid Lab object to the Block."""
    day = "mon"
    start = "8:30"
    dur = 2
    block = Block(day, start, dur)
    lab1 = Lab()
    lab2 = Lab()
    block.assign_lab(lab1)
    block.assign_lab(lab1)
    block.assign_lab(lab2)
    labs = block.labs
    assert len(labs) == 2


def test_remove_lab_good():
    """Verifies that remove_lab() can successfully remove a valid Lab object from this Block."""
    day = "mon"
    start = "8:30"
    dur = 2
    block = Block(day, start, dur)
    lab1 = Lab()
    lab2 = Lab()
    block.assign_lab(lab1)
    block.assign_lab(lab2)
    block.remove_lab(lab1)
    labs = block.labs
    assert not block.has_lab(lab1)
    assert block.has_lab(lab2)
    assert len(labs) == 1


def test_remove_lab_no_crash():
    """Verifies that remove_lab won't crash the program if the Block doesn't contain
    the specified valid Lab. """
    day = "mon"
    start = "8:30"
    dur = 2
    block = Block(day, start, dur)
    lab = Lab()
    block.assign_lab(lab)
    other_lab = Lab("R-101", "dummy")
    block.remove_lab(other_lab)
    assert block.has_lab(lab)


def test_remove_all_labs():
    """Verifies that remove_all_labs works as intended, removing all Labs from the current
    Block. """
    day = "mon"
    start = "8:30"
    dur = 2
    block = Block(day, start, dur)
    this_lab = Lab("R-100", "the second-worst place in the world")
    other_lab = Lab("R-101", "the worst place in the world")
    block.assign_lab(this_lab)
    block.assign_lab(other_lab)
    assert len(block.labs) == 2
    block.remove_all_labs()
    assert len(block.labs) == 0
    assert not block.has_lab(this_lab)
    assert not block.has_lab(other_lab)


def test_labs():
    """Verifies that labs() returns a list of all Lab objects assigned to this Block."""
    day = "mon"
    start = "8:30"
    dur = 2
    block = Block(day, start, dur)
    this_lab = Lab("R-100", "the second-worst place in the world")
    other_lab = Lab("R-101", "the worst place in the world")
    block.assign_lab(this_lab)
    block.assign_lab(other_lab)
    labs = block.labs
    assert len(labs) == 2 and labs[0] == this_lab and labs[1] == other_lab


def test_labs_empty():
    """Verifies that labs returns an empty list if called while no Labs are assigned to the
    Block. """
    day = "mon"
    start = "8:30"
    dur = 2
    block = Block(day, start, dur)
    labs = block.labs
    assert len(labs) == 0


def test_has_lab_good():
    """Verifies that has_lab() returns true when the specified Lab is assigned to this Block."""
    day = "mon"
    start = "8:30"
    dur = 2
    block = Block(day, start, dur)
    lab = Lab()
    block.assign_lab(lab)
    assert block.has_lab(lab)


def test_has_lab_false():
    """"Verifies that has_lab() returns false when the Lab isn't assigned to this Block."""
    day = "mon"
    start = "8:30"
    dur = 2
    block = Block(day, start, dur)
    lab = Lab()
    assert block.has_lab(lab) is False


def test_assign_teacher_good():
    """Verifies that the assign_teacher() method works as intended."""
    day = "mon"
    start = "8:30"
    dur = 2
    block = Block(day, start, dur)
    teach = Teacher("John", "Smith")
    block.assign_teacher(teach)
    assert block.has_teacher(teach)


def test_assign_teacher_multiple():
    """Verifies that the assign_teacher() method works as intended."""
    day = "mon"
    start = "8:30"
    dur = 2
    block = Block(day, start, dur)
    teach1 = Teacher("John", "Smith")
    teach2 = Teacher("Jane", "Smith")
    block.assign_teacher(teach1)
    block.assign_teacher(teach2)
    assert block.has_teacher(teach1)
    assert block.has_teacher(teach2)
    assert len(block.teachers) == 2


def test_assign_teacher_multiple_with_duplicates():
    """Verifies that the assign_teacher() method works as intended."""
    day = "mon"
    start = "8:30"
    dur = 2
    block = Block(day, start, dur)
    teach1 = Teacher("John", "Smith")
    teach2 = Teacher("Jane", "Smith")
    block.assign_teacher(teach1)
    block.assign_teacher(teach1)
    block.assign_teacher(teach2)
    print(teach1, teach2, block.teachers)
    assert len(block.teachers) == 2


def test_remove_teacher_good():
    """Verifies that remove_teacher() works as intended."""
    day = "mon"
    start = "8:30"
    dur = 2
    block = Block(day, start, dur)
    teach = Teacher("John", "Smith")
    block.assign_teacher(teach)
    other_teach = Teacher("Jane", "Doe")
    block.assign_teacher(other_teach)
    block.remove_teacher(teach)
    assert len(block.teachers) == 1
    assert block.has_teacher(teach) is not True
    assert block.has_teacher(other_teach)


def test_remove_teacher_no_crash():
    """Verifies that remove_teacher() doesn't crash the program when attempting to remove a
    Teacher that isn't assigned to this Block. """
    day = "mon"
    start = "8:30"
    dur = 2
    block = Block(day, start, dur)
    teach = Teacher("John", "Smith")
    block.assign_teacher(teach)
    other_teach = Teacher("Jane", "Doe")
    block.remove_teacher(other_teach)
    assert len(block.teachers) == 1


def test_remove_all_teachers():
    """Verifies that remove_all_teachers() works as intended."""
    day = "mon"
    start = "8:30"
    dur = 2
    block = Block(day, start, dur)
    teach = Teacher("John", "Smith")
    other_teach = Teacher("Jane", "Doe")
    block.assign_teacher(teach)
    block.assign_teacher(other_teach)
    block.remove_all_teachers()
    assert block.has_teacher(teach) is not True
    assert block.has_teacher(other_teach) is not True
    assert len(block.teachers) == 0


def test_teachers():
    """Verifies that teachers() returns a list of all the Teachers assigned to this Block."""
    day = "mon"
    start = "8:30"
    dur = 2
    block = Block(day, start, dur)
    teach = Teacher("John", "Smith")
    other_teach = Teacher("Jane", "Doe")
    block.assign_teacher(teach)
    block.assign_teacher(other_teach)
    teachers = block.teachers
    assert len(teachers) == 2 and teach in teachers and other_teach in teachers


def test_teachers_empty_list():
    """Verifies that teachers will return an empty list if no Teachers are assigned to this
    Block. """
    day = "mon"
    start = "8:30"
    dur = 2
    block = Block(day, start, dur)
    teachers = block.teachers
    assert len(teachers) == 0


def test_has_teacher_true():
    """Verifies that has_teacher() returns true when the specified Teacher has been assigned
    to this Block. """
    day = "mon"
    start = "8:30"
    dur = 2
    block = Block(day, start, dur)
    teach = Teacher("John", "Smith")
    block.assign_teacher(teach)
    assert block.has_teacher(teach)


def test_has_teach_false():
    """Verifies that has_teacher returns false when the specified Teacher isn't assigned to
    this Block. """
    day = "mon"
    start = "8:30"
    dur = 2
    block = Block(day, start, dur)
    teach = Teacher("John", "Smith")
    block.assign_teacher(teach)
    other_teach = Teacher("Jane", "Doe")
    assert block.has_teacher(other_teach) is False


def test_reset_conflicted():
    """Verifies that reset_conflicted works as intended, setting the value of conflicted_number to
    False. """
    day = "mon"
    start = "8:30"
    dur = 2
    block1 = Block(day, start, dur)
    block1.reset_conflicted()
    assert block1.conflicted_number == 0


def test_conflicted_getter():
    """Verifies that the conflicted_number getter works as intended, returning a default value of
    False. """
    day = "mon"
    start = "8:30"
    dur = 2
    block1 = Block(day, start, dur)
    assert block1.conflicted_number == 0


def test_conflicted_setter_good():
    """Verifies that the conflicted_number setter works as intended."""
    day = "mon"
    start = "8:30"
    dur = 2
    block1 = Block(day, start, dur)
    block1.conflicted_number = 1
    assert block1.conflicted_number == 1


def test_is_conflicted_true():
    """Verifies that is_conflicted() returns the true if the conflicted number is not zero."""
    day = "mon"
    start = "8:30"
    dur = 2
    block1 = Block(day, start, dur)
    block1.conflicted_number = 5
    assert block1.is_conflicted is True


def test_is_conflicted_false():
    """Verifies that is_conflicted() returns the false if the conflicted number is zero."""
    day = "mon"
    start = "8:30"
    dur = 2
    block1 = Block(day, start, dur)
    block1.conflicted_number = 0
    assert block1.is_conflicted is False


def test_string_representation():
    """Verifies that string_representation returns a description containing info about the Block,
    its assigned Labs, and its Section. """
    day = "mon"
    start = "8:30"
    dur = 2
    block = Block(day, start, dur)
    lab1 = Lab("R-101", "Worst place in the world")
    lab2 = Lab("R-102", "Second-worst place in the world")
    block.assign_lab(lab1)
    block.assign_lab(lab2)
    desc = str(block)
    assert day in desc and start in desc and lab1.number in desc \
           and lab2.number in desc


def test_string_representation_no_section():
    """Verifies that string representation returns information about just the Block if it has no
    assigned Section. """
    day = "mon"
    start = "8:30"
    dur = 2
    block = Block(day, start, dur)
    lab1 = Lab("R-101", "Worst place in the world")
    lab2 = Lab("R-102", "Second-worst place in the world")
    block.assign_lab(lab1)
    block.assign_lab(lab2)
    desc = str(block)
    assert day in desc \
           and start in desc and lab1.number in desc and lab1.descr in desc \
           and lab2.number in desc and lab2.descr in desc


def test_description():
    """Verifies that short_description() works as intended: returning information about just
    the Block itself. """
    day = "mon"
    start = "8:30"
    dur = 2
    block = Block(day, start, dur)
    desc = block.description
    assert f"{day}, {start} {dur:.1f} hour(s)" in desc


# ====================================================================================================================
# Synchronization
# ====================================================================================================================
def test_start_setter_synced_2_blocks_check_block1_moves_block2():
    """Verifies that the start setter works as intended, and that it changes the start value of
    any Blocks synced_blocks to the Block on which it was called. """
    day = "mon"
    start = "8:30"
    dur = 2
    block1 = Block(day, start, dur)
    block2 = Block("wed", start, dur)
    block1.sync_block(block2)
    new_start = "10:00"
    block1.start = new_start
    assert block2.start == new_start


def test_start_setter_synced_2_blocks_check_block2_moves_block1():
    """Verifies that the start setter works as intended, and that it changes the start value of
    any Blocks synced_blocks to the Block on which it was called. """
    day = "mon"
    start = "8:30"
    dur = 2
    block1 = Block(day, start, dur)
    block2 = Block("wed", start, dur)
    block1.sync_block(block2)
    new_start = "10:00"
    block2.start = new_start
    assert block1.start == new_start


def test_start_setter_synced_4_blocks():
    """Same as previous test, but with 4 blocks instead of 2."""
    day = "mon"
    start = "8:30"
    dur = 2
    block1 = Block(day, start, dur)
    block2 = Block("wed", start, dur)
    block3 = Block("thu", start, dur)
    block4 = Block("fri", start, dur)
    block1.sync_block(block2)
    block1.sync_block(block3)
    block1.sync_block(block4)

    new_start = "10:00"
    block1.start = new_start
    assert block2.start == new_start and block3.start == new_start and block4.start == new_start


def test_start_setter_synced_4_blocks_move_block3():
    """Same as previous test, but with 4 blocks instead of 2."""
    day = "mon"
    start = "8:30"
    dur = 2
    block1 = Block(day, start, dur)
    block2 = Block("wed", start, dur)
    block3 = Block("thu", start, dur)
    block4 = Block("fri", start, dur)
    block1.sync_block(block2)
    block1.sync_block(block3)
    block1.sync_block(block4)

    new_start = "10:00"
    block3.start = new_start
    assert block2.start == new_start and block1.start == new_start and block4.start == new_start


def test_sync_block_good():
    """Verifies that sync_block() synchronizes a passed Block with this Block."""
    day = "mon"
    start = "8:30"
    dur = 2
    block1 = Block(day, start, dur)
    block2 = Block("tue", start, dur)
    block1.sync_block(block2)
    assert block2 in block1.synced_blocks
    assert block1 in block2.synced_blocks


def test_unsync_block1_from_block2():
    """Verifies that unsync_block() works as intended."""
    day = "mon"
    start = "8:30"
    dur = 2
    block1 = Block(day, start, dur)
    block2 = Block("tue", start, dur)
    block1.sync_block(block2)
    assert block1 in block2.synced_blocks
    assert block2 in block1.synced_blocks

    block2.unsync_block(block1)
    assert block1 not in block2.synced_blocks
    assert block2 not in block1.synced_blocks


def test_synced():
    """Verifies that synced_blocks returns a tuple of all the Blocks that are synced_blocks with this
    Block. """
    day = "mon"
    start = "8:30"
    dur = 2
    block1 = Block(day, start, dur)
    block2 = Block("tue", start, dur)
    block3 = Block("wed", start, dur)
    block1.sync_block(block2)
    block1.sync_block(block3)
    blocks = block1.synced_blocks

    assert len(blocks) == 2 and block2 in blocks and block3 in blocks


def test_synced_empty_tuple():
    """Verifies that synced_blocks() returns an empty tuple if called when no Blocks are synced_blocks with
    this Block. """
    day = "mon"
    start = "8:30"
    dur = 2
    block1 = Block(day, start, dur)
    blocks = block1.synced_blocks
    assert len(blocks) == 0


def test_synced_blocks_interdependence_works_as_expected():
    block1 = Block("mon", "8:30", 2)
    block2 = Block("tue", "8:30", 2)
    block3 = Block("wed", "8:30", 2)
    block4 = Block("fri", "8:30", 2)

    # make all blocks dependent on block1, and vice versa
    block1.sync_block(block2)
    block1.sync_block(block3)
    block1.sync_block(block4)

    # disconnect block 3 from block 1,
    block3.unsync_block(block1)
    block3.start = "11:30"

    # changing block 3 should have no effect on anybody
    assert block1.start == block2.start == block4.start == "8:30"
    assert block3.start == "11:30"

    # changing should not affect block 3, but still affect block 2 and block 4
    block1.start = "9:30"
    assert block1.start == block2.start == block4.start == "9:30"
    assert block3.start == "11:30"
