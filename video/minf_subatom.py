import struct

def parse_vmhd_atom(vmhd_data, vmhd_info):
    version = struct.unpack('>B', vmhd_data[0:1])[0]
    flags = struct.unpack('>3B', vmhd_data[1:4])
    qtgfxmode = vmhd_data[4:6]
    if qtgfxmode == b'\x00\x00':
        graphics_mode = 'qtgCopy'
    elif qtgfxmode == b'\x00\x40':
        graphics_mode = 'qtgDitherCopy'
    elif qtgfxmode == b'\x00\x20':
        graphics_mode = 'qtgBlend'
    elif qtgfxmode == b'\x00\x24':
        graphics_mode = 'qtgTransparent'
    elif qtgfxmode == b'\x01\x00':
        graphics_mode = 'qtgStraightAlpha'
    elif qtgfxmode == b'\x01\x01':
        graphics_mode = 'qtgPremulWhiteAlpha'
    elif qtgfxmode == b'\x01\x02':
        graphics_mode = 'qtgPremulBlackAlpha'
    elif qtgfxmode == b'\x01\x04':
        graphics_mode = 'qtgStraightAlphaBlend'
    elif qtgfxmode == b'\x01\x03':
        graphics_mode = 'qtgComposition'
    opcolor = struct.unpack('>3H', vmhd_data[6:12]) # red, green, blue

    vmhd_info['version'] = version
    vmhd_info['flags'] = flags
    vmhd_info['vmhd_graphicsMode'] = graphics_mode
    vmhd_info['vmhd_opColor'] = opcolor

def parse_smhd_atom(smhd_data, atom_info):                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              
    version = struct.unpack('>B', smhd_data[0:1])[0]
    flags = struct.unpack('>3B', smhd_data[1:4])[0]
    balance = struct.unpack('>h', smhd_data[4:6])[0]
    reserved = struct.unpack('>h', smhd_data[6:8])[0]

    atom_info['smhd_version'] = version
    atom_info['smhd_flags'] = flags
    atom_info['smhd_balance'] = balance
    atom_info['smhd_reserved'] = reserved

def parse_dinf_atom(dinf_data, dinf_info, track_id):
    dref_info = {}
    offset = 0
    while offset < len(dinf_data):
        dinf_subAtom_size, dinf_subAtom_type = struct.unpack('>I4s', dinf_data[offset:offset+8])
        dinf_subAtom_type = dinf_subAtom_type.decode('utf-8')
        
        #atom_info[f'{dinf_subAtom_type}_{track_id}'] = dinf_subAtom_type

        if dinf_subAtom_type == 'dref':
            dinf_subAtom_type = f"{dinf_subAtom_type}_{track_id}"
            dref_info['type'] = dinf_subAtom_type
            dref_info['size'] = dinf_subAtom_size
            parse_dref_atom(dinf_data[offset+8:offset+dinf_subAtom_size], dref_info, track_id)

            dinf_info[dref_info['type']]=dref_info

        offset += dinf_subAtom_size

def parse_dref_atom(dref_data, dref_info, track_id):
    version = struct.unpack('>B', dref_data[0:1])[0]
    flags = struct.unpack('>3B', dref_data[1:4])
    entry_count = struct.unpack('>I', dref_data[4:8])[0]

    dref_info[f'version_{track_id}'] = version
    dref_info[f'flags_{track_id}'] = flags
    dref_info[f'entry_count_{track_id}'] = entry_count

    offset = 8
    for _ in range(entry_count):
        size = struct.unpack('>I', dref_data[offset:offset+4])[0]
        entry_type = struct.unpack('>4s', dref_data[offset+4:offset+8])[0].decode('utf-8')
        entry_version = struct.unpack('>B', dref_data[offset+8:offset+9])[0]
        entry_flags = struct.unpack('>3B', dref_data[offset+9:offset+12])

        dref_info[f'entrySize_{track_id}'] = size
        dref_info[f'entryType_{track_id}'] = entry_type
        dref_info[f'entryVersion_{track_id}'] = entry_version
        dref_info[f'entryFlags_{track_id}'] = entry_flags

        offset += size