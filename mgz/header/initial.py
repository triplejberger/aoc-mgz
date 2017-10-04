from construct import *
from mgz.header.objects import *
from mgz.header.playerstats import *
from mgz.enums import *
from mgz.util import *

"""Player attributes"""
attributes = "attributes"/Struct(
    Array(lambda ctx: ctx._._._.replay.num_players, TheirDiplomacyEnum("their_diplomacy"/Byte)),
    Array(9, MyDiplomacyEnum("my_diplomacy"/Int32sl)),
    Padding(5),
    "player_name_length"/Int16ul,
    "player_name"/String(this.player_name_length, padchar = b'\x00', trimdir = 'right', encoding='latin1'),
    Padding(1), # 0x16
    "num_header_data"/Int32ul, # always 198
    Padding(1), # 0x21
    player_stats,
    If(lambda ctx: ctx.num_header_data > 198,
        Padding(42*4)
    ),
    Padding(1),
    "camera_x"/Float32l,
    "camera_y"/Float32l,
    "end_of_camera"/Tell,
    "num_unk"/Int32sl,
    If(lambda ctx: ctx.num_unk > 0, # present in resumed games
        Array(lambda ctx: ctx.num_unk, "unk_structure"/Struct(Padding(8))),
    ),
    Padding(5),
    "civilization"/Byte,
    Padding(3),
    "player_color"/Byte,
    Padding(1),
)

"""Initial state of players, including Gaia"""
player = "players"/Struct(
    attributes,
    "start_of_objects"/Find(b'\x0b\x00\x08\x00\x00\x00\x02\x00\x00', None),
    # If this isn't a restored game, we can read all the existing objects
    Embedded("not_restored"/If(this._.restore_time == 0, Struct(
            RepeatUpTo(b'\x00', existing_object),
            Padding(14),
        )
    )),
    # Can't parse existing objects in a restored game, skip the whole structure
    Embedded("is_restored"/If(this._.restore_time > 0, Struct(
            "end_of_objects"/GotoObjectsEnd(),
            # Just an empty array for now
            Array(0, existing_object)
        ),
    ))
)

"""Initial state"""
initial = "initial"/Struct(
    "restore_time"/Int32ul, # zero for non-restored
    "start_of_players"/Find(b'\x98\x9E\x00\x00\x02\x0B', None),
    Array(lambda ctx: ctx._.replay.num_players, player),
    Padding(19),
)