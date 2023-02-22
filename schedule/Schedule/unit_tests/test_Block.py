import pytest
import sys
from os import path

sys.path.append(path.dirname(path.dirname(__file__)))

from Block import Block
from Section import Section
from Lab import Lab
from Teacher import Teacher
from pony.orm import *
from database.PonyDatabaseConnection import define_database
from unit_tests.db_constants import *


class TestBlock:
    db: Database = define_database(host=HOST, passwd=PASSWD, db=DB_NAME, provider=PROVIDER,
                                   user=USERNAME)

    @pytest.fixture(autouse=True)
    def run_before(self):
        self.db.create_tables()
        yield
        # self.db.drop_all_tables(with_all_data=True)
        self.db.drop_table(table_name='lab', if_exists=True, with_all_data=True)
        self.db.drop_table(table_name='block', if_exists=True, with_all_data=True)
        self.db.drop_table(table_name='time_slot', if_exists=True, with_all_data=True)
        self.db.drop_table(table_name='section', if_exists=True, with_all_data=True)
        self.db.drop_table(table_name='teacher', if_exists=True, with_all_data=True)
        self.db.drop_table(table_name='course', if_exists=True, with_all_data=True)
        # The code below prevents us from getting a BindingError when this function is called
        # after the first test. Makes the test suite run really slow, but at least it ensures
        # that all the tests pass. Based on a solution found here:
        # https://github.com/ponyorm/pony/issues/214#issuecomment-787452937
        # self.db.disconnect()
        # self.db.provider = None
        # self.db.schema = None

    def test_number_getter(self):
        """Verifies that the number property works as intended."""
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        assert block.number == num

    def test_number_setter_good(self):
        """Verifies that the number setter can set an appropriate value."""
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        new_num = 4
        block.number = new_num
        assert block.number == new_num

    def test_number_setter_bad(self):
        """Verifies that the number setter throws an exception when receiving bad input."""
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        bad_num = "foo"
        with pytest.raises(Exception) as e:
            block.number = bad_num
        assert "must be an integer and cannot be null" in str(e.value).lower()

    def test_delete(self):
        """Verifies that the delete() method successfully destroys an instance of a Block."""
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        block.delete()
        assert block not in Block.list()

    def test_start_getter(self):
        """Verifies that the start getter works as intended. Same as TimeSlot.start getter."""
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        assert block.start == start

    def test_start_setter_synced_2_blocks(self):
        """Verifies that the start setter works as intended, and that it changes the start value of any Blocks synced to
        the Block on which it was called. """
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block1 = Block(day, start, dur, num)
        block2 = Block("wed", start, dur, 2)
        block1.sync_block(block2)
        block2.sync_block(block1)
        new_start = "10:00"
        block1.start = new_start
        assert block2.start == new_start

    def test_start_setter_synced_4_blocks(self):
        """Same as previous test, but with 4 blocks instead of 2."""
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block1 = Block(day, start, dur, num)
        block2 = Block("wed", start, dur, 2)
        block3 = Block("thu", start, dur, 3)
        block4 = Block("sat", start, dur, 4)
        block1.sync_block(block2)
        block1.sync_block(block3)
        block1.sync_block(block4)
        block2.sync_block(block1)
        block2.sync_block(block3)
        block2.sync_block(block4)
        block3.sync_block(block1)
        block3.sync_block(block2)
        block3.sync_block(block4)
        block4.sync_block(block1)
        block4.sync_block(block2)
        block4.sync_block(block3)

        new_start = "10:00"
        block1.start = new_start
        assert block2.start == new_start and block3.start == new_start and block4.start == new_start

    def test_day_getter(self):
        """Verifies that the day getter works as intended. Same as in TimeSlot."""
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block1 = Block(day, start, dur, num)
        assert block1.day == day

    def test_day(self):
        """Verifies that the day setter works as intended, changing the day property of any Block synced to the current
        Block. """
        day = "mon"
        start1 = "8:00"
        start2 = "12:00"
        dur = 2
        num1 = 1
        num2 = 2
        block1 = Block(day, start1, dur, num1)
        block2 = Block(day, start2, dur, num2)
        block1.sync_block(block2)
        block2.sync_block(block1)
        block1.day = "thu"
        assert block2.day == "thu"

    def test_id(self):
        """Verifies that the id property works as intended."""
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        assert block.id == 1

    def test_section_getter(self):
        """Verifies that the section getter works as intended."""
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        """Since sections are not assigned to Blocks at initialization, the value of section will 
        be None. """
        assert block.section is None

    def test_section_setter_good(self):
        """Verifies that the section setter can set a valid section."""
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        sect = Section(id=1)
        block.section = sect
        assert block.section == sect

    def test_section_setter_bad(self):
        """Verifies that the section setter throws a TypeError when receiving a value that isn't
        a Section. """
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        bad_sect = {
            "foo": "foo",
            "bar": "bar"
        }
        with pytest.raises(TypeError) as e:
            block.section = bad_sect
        assert "invalid section" in str(e.value).lower()

    def test_assign_lab_good(self):
        """Verifies that the assign_lab method can assign a valid Lab object to the Block."""
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        lab = Lab()
        block.assign_lab(lab)
        assert getattr(block, '_labs', {})[lab.id] == lab

    def test_assign_lab_bad(self):
        """Verifies that assign_lab() will reject an input that isn't a Lab object."""
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        bad_lab = "baz"
        with pytest.raises(TypeError) as e:
            block.assign_lab(bad_lab)
        assert "invalid lab" in str(e.value).lower()

    def test_remove_lab_good(self):
        """Verifies that remove_lab() can successfully remove a valid Lab object from this Block."""
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        lab = Lab()
        block.assign_lab(lab)
        block.remove_lab(lab)
        assert lab not in getattr(block, '_labs').values()

    def test_remove_lab_bad(self):
        """Verifies that remove_lab() throws an exception if asked to remove something that isn't
        a Lab from this Block. """
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        lab = Lab()
        block.assign_lab(lab)
        bad_lab = "tesla"
        with pytest.raises(TypeError) as e:
            block.remove_lab(bad_lab)
        assert "invalid lab" in str(e.value).lower()

    def test_remove_lab_no_crash(self):
        """Verifies that remove_lab won't crash the program if the Block doesn't contain
        the specified valid Lab. """
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        lab = Lab()
        block.assign_lab(lab)
        other_lab = Lab("R-101", "dummy")
        block.remove_lab(other_lab)
        assert lab in getattr(block, "_labs").values()

    def test_remove_all_labs(self):
        """Verifies that remove_all_labs works as intended, removing all Labs from the current
        Block. """
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        this_lab = Lab("R-100", "the second-worst place in the world")
        other_lab = Lab("R-101", "the worst place in the world")
        block.assign_lab(this_lab)
        block.assign_lab(other_lab)
        block.remove_all_labs()
        assert len(getattr(block, '_labs')) == 0

    def test_labs(self):
        """Verifies that labs() returns a list of all Lab objects assigned to this Block."""
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        this_lab = Lab("R-100", "the second-worst place in the world")
        other_lab = Lab("R-101", "the worst place in the world")
        block.assign_lab(this_lab)
        block.assign_lab(other_lab)
        labs = block.labs()
        assert len(labs) == 2 and labs[0] == this_lab and labs[1] == other_lab

    def test_labs_empty(self):
        """Verifies that labs() returns an empty list if called while no Labs are assigned to the
        Block. """
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        labs = block.labs()
        assert len(labs) == 0

    def test_has_lab_good(self):
        """Verifies that has_lab() returns true when the specified Lab is assigned to this Block."""
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        lab = Lab()
        block.assign_lab(lab)
        assert block.has_lab(lab)

    def test_has_lab_false(self):
        """"Verifies that has_lab() returns false when the Lab isn't assigned to this Block."""
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        lab = Lab()
        assert block.has_lab(lab) is False

    def test_has_lab_bad_input(self):
        """Verifies that has_lab() returns false when checking for something that isn't a Lab."""
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        lab = Lab()
        block.assign_lab(lab)
        bad_lab = "nonce"
        assert block.has_lab(bad_lab) is False

    def test_assign_teacher_good(self):
        """Verifies that the assign_teacher() method works as intended."""
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        teach = Teacher("John", "Smith")
        block.assign_teacher(teach)
        assert getattr(block, '_teachers')[teach.id] == teach

    def test_assign_teacher_bad(self):
        """Verifies that assign_teacher() throws an exception for bad input."""
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        bad_teach = "foo"
        with pytest.raises(TypeError) as e:
            block.assign_teacher(bad_teach)
        assert "invalid teacher" in str(e.value).lower()

    def test_remove_teacher_good(self):
        """Verifies that remove_teacher() works as intended."""
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        teach = Teacher("John", "Smith")
        block.assign_teacher(teach)
        block.remove_teacher(teach)
        assert len(getattr(block, '_teachers')) == 0

    def test_remove_teacher_bad(self):
        """Verifies that remove_teacher() throws an exception when trying to remove something
        that isn't a Teacher object. """
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        teach = Teacher("John", "Smith")
        block.assign_teacher(teach)
        bad_teach = "foo"
        with pytest.raises(TypeError) as e:
            block.remove_teacher(bad_teach)
        assert "invalid teacher" in str(e.value).lower()

    def test_remove_teacher_no_crash(self):
        """Verifies that remove_teacher() doesn't crash the program when attempting to remove a
        Teacher that isn't assigned to this Block. """
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        teach = Teacher("John", "Smith")
        block.assign_teacher(teach)
        other_teach = Teacher("Jane", "Doe")
        block.remove_teacher(other_teach)
        assert len(getattr(block, '_teachers')) == 1 and getattr(block, '_teachers')[
            teach.id] == teach

    def test_remove_all_teachers(self):
        """Verifies that remove_all_teachers() works as intended."""
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        teach = Teacher("John", "Smith")
        other_teach = Teacher("Jane", "Doe")
        block.assign_teacher(teach)
        block.assign_teacher(other_teach)
        block.remove_all_teachers()
        assert len(getattr(block, '_teachers')) == 0

    def test_remove_all_teachers_no_crash(self):
        """Verifies that remove_all_teachers() won't crash the program when no teachers have been
        assigned yet. """
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        block.remove_all_teachers()
        assert len(getattr(block, '_teachers')) == 0

    def test_teachers(self):
        """Verifies that teachers() returns a list of all the Teachers assigned to this Block."""
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        teach = Teacher("John", "Smith")
        other_teach = Teacher("Jane", "Doe")
        block.assign_teacher(teach)
        block.assign_teacher(other_teach)
        teachers = block.teachers()
        assert len(teachers) == 2 and teach in teachers and other_teach in teachers

    def test_teachers_empty_list(self):
        """Verifies that teachers() will return an empty list if no Teachers are assigned to this
        Block. """
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        teachers = block.teachers()
        assert len(teachers) == 0

    def test_has_teacher_true(self):
        """Verifies that has_teacher() returns true when the specified Teacher has been assigned
        to this Block. """
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        teach = Teacher("John", "Smith")
        block.assign_teacher(teach)
        assert block.has_teacher(teach)

    def test_has_teach_false(self):
        """Verifies that has_teacher returns false when the specified Teacher isn't assigned to
        this Block. """
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        teach = Teacher("John", "Smith")
        block.assign_teacher(teach)
        other_teach = Teacher("Jane", "Doe")
        assert block.has_teacher(other_teach) is False

    def test_has_teach_bad_input(self):
        """Verifies that has_teacher() returns false when passed something that isn't a Teacher
        object. """
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        teach = Teacher("John", "Smith")
        block.assign_teacher(teach)
        bad_teach = "foo"
        assert block.has_teacher(bad_teach) is False

    def test_teachers_obj(self):
        """Verifies that teachersObj() returns a dict of teachers."""
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        teach = Teacher("John", "Smith")
        other_teach = Teacher("Jane", "Doe")
        block.assign_teacher(teach)
        block.assign_teacher(other_teach)
        teachers = block.teachersObj()
        assert type(teachers) is dict

    def test_sync_block_good(self):
        """Verifies that sync_block() synchronizes a passed Block with this Block."""
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block1 = Block(day, start, dur, num)
        block2 = Block("tue", start, dur, 2)
        block1.sync_block(block2)
        assert len(getattr(block1, '_sync')) == 1 and block2 in getattr(block1, '_sync')

    def test_sync_block_bad(self):
        """Verifies that sync_block() throws an exception when receiving something that isn't a
        Block. """
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        bad_block = "foo"
        with pytest.raises(TypeError) as e:
            block.sync_block(bad_block)
        assert "invalid block" in str(e.value).lower()

    def test_unsync_block_good(self):
        """Verifies that unsync_block() works as intended."""
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block1 = Block(day, start, dur, num)
        block2 = Block("tue", start, dur, 2)
        block1.sync_block(block2)
        block1.unsync_block(block2)
        assert len(getattr(block1, '_sync')) == 0

    def test_unsync_block_no_crash_bad_input(self):
        """Verifies that unsync_block will not crash the program when receiving bad input."""
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block1 = Block(day, start, dur, num)
        block2 = Block("tue", start, dur, 2)
        block1.sync_block(block2)
        block1.unsync_block("foo")
        assert len(getattr(block1, '_sync')) == 1 and block2 in getattr(block1, '_sync')

    def test_synced(self):
        """Verifies that synced() returns a list of all the Blocks that are synced with this
        Block. """
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block1 = Block(day, start, dur, num)
        block2 = Block("tue", start, dur, 2)
        block1.sync_block(block2)
        blocks = block1.synced()
        assert len(blocks) == 1 and block2 in blocks

    def test_synced_empty_list(self):
        """Verifies that synced() returns an empty list if called when no Blocks are synced with
        this Block. """
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block1 = Block(day, start, dur, num)
        blocks = block1.synced()
        assert len(blocks) == 0

    def test_reset_conflicted(self):
        """Verifies that reset_conflicted works as intended, setting the value of conflicted to
        False. """
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block1 = Block(day, start, dur, num)
        block1.reset_conflicted()
        assert getattr(block1, '_conflicted') is 0

    def test_conflicted_getter(self):
        """Verifies that the conflicted getter works as intended, returning a default value of
        False. """
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block1 = Block(day, start, dur, num)
        assert block1.conflicted is 0

    def test_conflicted_setter_good(self):
        """Verifies that the conflicted setter works as intended."""
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block1 = Block(day, start, dur, num)
        block1.conflicted = 1
        assert block1.conflicted is 1

    # def test_conflicted_setter_bad():
    #     """Verifies that the conflicted setter converts invalid input to a boolean value."""
    #     day = "mon"
    #     start = "8:30"
    #     dur = 2
    #     num = 1
    #     block1 = Block(day, start, dur, num)
    #     block1.conflicted = "yes"
    #     assert block1.conflicted is True

    def test_is_conflicted(self):
        """Verifies that is_conflicted() returns the value of the conflicted property."""
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block1 = Block(day, start, dur, num)
        block1.conflicted = True
        assert block1.is_conflicted() is True

    def test_print_description_full(self):
        """Verifies that print_description returns a description containing info about the Block,
        its assigned Labs, and its Section. """
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        sect = Section("42", 2, "Section 42", id=1)
        lab1 = Lab("R-101", "Worst place in the world")
        lab2 = Lab("R-102", "Second-worst place in the world")
        block.section = sect
        block.assign_lab(lab1)
        block.assign_lab(lab2)
        desc = block.print_description()
        assert str(sect.number) in desc and day in desc and start in desc and lab1.number in desc \
               and lab2.number in desc

    def test_print_description_short(self):
        """Verifies that print_description returns information about just the Block if it has no
        assigned Section. """
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        lab1 = Lab("R-101", "Worst place in the world")
        lab2 = Lab("R-102", "Second-worst place in the world")
        block.assign_lab(lab1)
        block.assign_lab(lab2)
        desc = block.print_description()
        assert day in desc \
               and start in desc and lab1.number in desc and lab1.descr in desc \
               and lab2.number in desc and lab2.descr in desc

    def test_print_description_2(self):
        """Verifies that print_description_2() works as intended: returning information about just
        the Block itself. """
        day = "mon"
        start = "8:30"
        dur = 2
        num = 1
        block = Block(day, start, dur, num)
        desc = block.print_description_2()
        assert f"{num} : {day}, {start} {dur:.1f} hour(s)" in desc

    # def test_conflicts():
    #     """Verifies that conflicts() returns an empty list when no Conflicts are
    #     assigned to this Block."""
    #     day = "mon"
    #     start = "8:30"
    #     dur = 2
    #     num = 1
    #     block = Block(day, start, dur, num)
    #     conflicts = block.conflicts()
    #     assert len(conflicts) == 0

    def test_refresh_number(self):
        """Verifies that refresh_number gives the Block a new number if its number is 0."""
        day = "mon"
        start = "8:30"
        dur = 2
        num = 0
        block = Block(day, start, dur, num)
        sect = Section("42", id=1)
        sect.add_block(block)
        block.refresh_number()
        assert block.number == 1

    def test_list(self):
        """Verifies that list() returns a tuple containing all extant Blocks."""
        Block._Block__instances = {}
        block_1 = Block("mon", "8:00", 1.5, 1)
        block_2 = Block("mon", "8:00", 1.5, 2)
        blocks = Block.list()
        assert len(blocks) == 2 and block_1 in blocks and block_2 in blocks

    def test_list_empty(self):
        """Verifies that list() returns an empty tuple if there are no Blocks."""
        Block._Block__instances = {}
        blocks = Block.list()
        assert len(blocks) == 0

    def test_get_day_blocks(self):
        """Verifies that get_day_blocks() returns a list of all Blocks occurring on a specific
        day of the week. """
        day = "mon"
        block_1 = Block("mon", "8:00", 1.5, 1)
        block_2 = Block("mon", "8:00", 1.5, 2)
        block_3 = Block("tue", "8:00", 1.5, 2)
        block_4 = Block("wed", "8:00", 1.5, 2)
        unfiltered_blocks = [block_1, block_2, block_3, block_4]
        monday_blocks = Block.get_day_blocks(day, unfiltered_blocks)
        assert len(monday_blocks) == 2 and block_1 in monday_blocks and block_2 in monday_blocks

    def test_get_day_blocks_bad_input(self):
        """Verifies that get_day_blocks() won't crash the program if passed a list containing
        non-Block objects. """
        day = "mon"
        block_1 = Block("mon", "8:00", 1.5, 1)
        block_2 = Block("mon", "8:00", 1.5, 2)
        block_3 = Block("tue", "8:00", 1.5, 2)
        block_4 = Block("wed", "8:00", 1.5, 2)
        bad_blocks = ["foo", "bar", "baz"]
        monday_blocks = Block.get_day_blocks(day, bad_blocks)
        assert len(monday_blocks) == 0

    def test_get_day_blocks_empty_list(self):
        """Verifies that get_day_blocks() returns an empty list if no Blocks match the passed
        day. """
        block_1 = Block("mon", "8:00", 1.5, 1)
        block_2 = Block("mon", "8:00", 1.5, 2)
        block_3 = Block("tue", "8:00", 1.5, 2)
        block_4 = Block("wed", "8:00", 1.5, 2)
        unfiltered_blocks = [block_1, block_2, block_3, block_4]
        bad_day = "fri"
        friday_blocks = Block.get_day_blocks(bad_day, unfiltered_blocks)
        assert len(friday_blocks) == 0
