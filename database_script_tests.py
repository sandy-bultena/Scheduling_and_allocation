from schedule.Models import *

from sqlmodel import Field, Session, SQLModel, create_engine, select
import yaml


def main():
    engine = create_engine("sqlite:///data.db", echo=True)

    SQLModel.metadata.create_all(engine)
    with open('data/W2021_2020_08_18+pruned.yaml', 'r') as f:
        data = yaml.safe_load(f.read())

    pseudo_database = {
        'teacher': {},
        'block': {},
        'course': {},
        'lab': {},
        'section': {},
        'semester': {},
        'stream': {},
        'unavailable': {},
    }

    day_to_num = {
        'mon': 1,
        'tue': 2,
        'wed': 3,
        'thur': 4,
        'fri': 5,
        'sat': 6,
        'sun': 0
    }

    with Session(engine) as session:
        for tt_id, tt in data['teachers']['list'].items():
            new_teach = Teacher(
                first_name=tt['fname'],
                last_name=tt['lname'],
                department=tt['dept'],
                release=tt['release'] or 0.0,
            )
            pseudo_database['teacher'][tt_id] = new_teach
            session.add(new_teach)

        for lb_id, lb in data['labs']['list'].items():
            new_lab = Lab(
                number=lb['number'],
                description=lb['descr'],
            )
            pseudo_database['lab'][lb_id] = new_lab
            session.add(new_lab)

        for str_id, sr in data['streams']['list'].items():
            new_stream = Stream(
                number=lb['number'],
                description=lb['descr'],
            )
            pseudo_database['stream'][str_id] = new_stream
            session.add(new_stream)

        for cc_id, cc in data['courses']['list'].items():
            new_course = Course(
                number=cc['number'],
                name=cc['name'],
                needs_alloc=bool(cc['allocation']),
            )
            pseudo_database['course'][cc_id] = new_course
            session.add(new_course)
            for sec_id, sec in cc['sections'].items():
                new_section = Section(
                    name=sec['name'],
                    number=sec['number'],
                    hours=sec['hours'],
                    number_of_students=sec['num_students'],
                )
                pseudo_database['section'][sec_id] = new_section
                new_section.course = new_course
                session.add(new_section)

                for str_id in sec['streams']:
                    new_section.streams.append(pseudo_database['stream'][str_id])

                for blk_id, blk in sec['blocks'].items():
                    new_block = Block(
                        day=blk['day_number'],
                        start=blk['start'],
                        duration=blk['duration'] * 60,
                        movable=bool(blk['movable'])
                    )
                    pseudo_database['block'] = new_block
                    new_block.section = new_section
                    for lb_id in blk['labs']:
                        new_block.labs.append(pseudo_database['lab'][lb_id])
                    session.add(new_block)

        session.commit()
        session.close()


if __name__ == '__main__':
    main()
