import struct

def get_moof_tag(video_file, AtomType, moofAtomSize, atom_info):
    while moofAtomSize > 8:  # Atom header size is 8 bytes (size + type)
        atom_header = video_file.read(8)
        atom_size, atom_type = struct.unpack('>I4s', atom_header)
        atom_type = atom_type.decode('utf-8')

        # If the atom contains sub-atoms, recursively parse them
        if atom_size == 1:
            extended_size = struct.unpack('>Q', video_file.read(8))[0]
            atom_size = extended_size

        if atom_size >= 8:  # At least 8 bytes are required for a valid atom
            parse_moof_subatom(video_file, atom_size, atom_info)
        else:
            break

        moofAtomSize -= atom_size
def parse_moof_subatom(video_file, size, atom_info):
    while size > 8:  # Atom header size is 8 bytes (size + type)
        atom_header = video_file.read(8)
        atom_size, atom_type = struct.unpack('>I4s', atom_header)
        atom_type = atom_type.decode('utf-8')

        atom_info['moof_subAtom_type'] = atom_type

        # If the sub-atom contains sub-atoms, recursively parse them
        if atom_size == 1:
            extended_size = struct.unpack('>Q', video_file.read(8))[0]
            atom_size = extended_size

        if atom_size >= 8:  # At least 8 bytes are required for a valid atom
            video_file.seek(atom_size - 8, 1)
        else:
            break

        size -= atom_size