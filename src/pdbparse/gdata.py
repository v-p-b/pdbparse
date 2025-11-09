# This file is a copy of gdata.py from pdbparse library ver. 1.5
# (see https://github.com/moyix/pdbparse)
# with a few mofifications that are necessary for my scripts to work correctly
# Ry Auscitte

# Python 2 and 3

from construct import *

gsym = Struct(
    "leaf_type" / Int16ul,
    "data"
    / Switch(
        lambda ctx: ctx.leaf_type,
        {
            0x110E: "data_v3"
            / Struct(
                "symtype" / Int32ul,
                "offset" / Int32ul,
                "segment" / Int16ul,
                "name" / CString(encoding="utf8"),
            ),
            0x1009: "data_v2"
            / Struct(
                "symtype" / Int32ul,
                "offset" / Int32ul,
                "segment" / Int16ul,
                "name" / PascalString(lengthfield="length" / Int8ul, encoding="utf8"),
            ),
            0x1125: "proc_ref"  # from struct REFSYM2 in cvinfo.h
            / Struct(
                "sumname" / Int32ul,
                "offset" / Int32ul,
                "iMod" / Int16ul,
                "name" / CString(encoding="utf8"),
            ),
            0x1127: "proc_ref"  # from struct REFSYM2 in cvinfo.h
            / Struct(
                "sumname" / Int32ul,
                "offset" / Int32ul,
                "iMod" / Int16ul,
                "name" / CString(encoding="utf8"),
            ),
            0x1108: "udt"  # from struct UDTSYM in cvinfo.h
            / Struct(
                "typind" / Int32ul,
                "name" / CString(encoding="utf8"),
            ),
            0x110D: "datasym"  # from struct DATASYM32 in cvinfo.h
            / Struct(
                "typind" / Int32ul,
                "offset" / Int32ul,
                "segment" / Int16ul,
                "name" / CString(encoding="utf8"),
            ),
            0x110C: "datasym"
            / Struct(
                "typind" / Int32ul,
                "offset" / Int32ul,
                "segment" / Int16ul,
                "name" / CString(encoding="utf8"),
            ),
            0x1110: "foobar"
            / Struct(
                "unk0"
                / Int32ul,  # Type index (containing enum if enumerate) or metadata token
                "unk1"
                / Int32ul,  # Type index (containing enum if enumerate) or metadata token
                "unk2"
                / Int32ul,  # Type index (containing enum if enumerate) or metadata token
                "unk3"
                / Int32ul,  # Type index (containing enum if enumerate) or metadata token
                "unk4"
                / Int32ul,  # Type index (containing enum if enumerate) or metadata token
                "unk5"
                / Int32ul,  # Type index (containing enum if enumerate) or metadata token
                "typind"
                / Int32ul,  # Type index (containing enum if enumerate) or metadata token
                "offset"
                / Int32ul,  # Type index (containing enum if enumerate) or metadata token
                "unk6"
                / Int16ul,  # Type index (containing enum if enumerate) or metadata token
                "flags"
                / Int8ul,  # Type index (containing enum if enumerate) or metadata token
                "name" / CString(encoding="utf8"),
            ),
        },
    ),
)

GlobalsData = "globals" / GreedyRange(
    Struct(
        "length" / Int16ul,
        "symbol" / RestreamData(Bytes(lambda ctx: ctx.length), gsym),
    )
)


def parse(data):
    con = GlobalsData.parse(data)
    return merge_structures(con)


def parse_stream(stream):
    con = GlobalsData.parse_stream(stream)
    return merge_structures(con)


def merge_structures(con):
    new_cons = []
    for sym in con:
        sym_dict = {"length": sym.length, "leaf_type": sym.symbol.leaf_type}
        if sym.symbol.data:
            # RAusc:
            for k in sym.symbol.data.keys():
                sym_dict[k] = sym.symbol.data[k]
            # sym_dict.update({
            #    'symtype': sym.symbol.data.symtype,
            #    'offset': sym.symbol.data.offset,
            #    'segment': sym.symbol.data.segment,
            #    'name': sym.symbol.data.name
            # })
        new_cons.append(Container(sym_dict))
    result = ListContainer(new_cons)
    return result
