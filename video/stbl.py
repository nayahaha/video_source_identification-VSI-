import struct
from video.decoding_info import *

def parse_stbl_atom(stbl_data, stbl_info, track_id):
    stsd_info = {}
    stts_info = {}
    stss_info = {}
    ctts_info = {}
    stsc_info = {}
    stsz_info = {}
    stco_info = {}
    sgpd_info = {}
    sbgp_info = {}

    offset = 0
    while offset < len(stbl_data):
        stbl_subAtom_size, stbl_subAtom_type = struct.unpack('>I4s', stbl_data[offset:offset+8])
        stbl_subAtom_type = stbl_subAtom_type.decode('utf-8')

        if stbl_subAtom_type == 'stsd':
            stbl_subAtom_type = f"{stbl_subAtom_type}_{track_id}"
            stsd_info['type'] = stbl_subAtom_type
            stsd_info['size'] = stbl_subAtom_size
            parse_stsd_atom(stbl_data[offset+8:offset+stbl_subAtom_size], stsd_info, track_id)

            stbl_info[stsd_info['type']]=stsd_info

        elif stbl_subAtom_type == 'stts':
            stbl_subAtom_type = f"{stbl_subAtom_type}_{track_id}"
            stts_info['type'] = stbl_subAtom_type
            stts_info['size'] = stbl_subAtom_size
            parse_stts_atom(stbl_data[offset+8:offset+stbl_subAtom_size], stts_info, track_id)

            stbl_info[stts_info['type']]=stts_info
            
        elif stbl_subAtom_type == 'stss':
            stbl_subAtom_type = f"{stbl_subAtom_type}_{track_id}"
            stss_info['type'] = stbl_subAtom_type
            stss_info['size'] = stbl_subAtom_size
            parse_stss_atom(stbl_data[offset+8:offset+stbl_subAtom_size], stss_info, track_id)
            
            stbl_info[stss_info['type']]=stss_info
            
        elif stbl_subAtom_type == 'ctts':
            stbl_subAtom_type = f"{stbl_subAtom_type}_{track_id}"
            ctts_info['type'] = stbl_subAtom_type
            ctts_info['size'] = stbl_subAtom_size
            parse_ctts_atom(stbl_data[offset+8:offset+stbl_subAtom_size], ctts_info, track_id)
            
            stbl_info[ctts_info['type']]=ctts_info

        elif stbl_subAtom_type == 'stsc':
            stbl_subAtom_type = f"{stbl_subAtom_type}_{track_id}"
            stsc_info['type'] = stbl_subAtom_type
            stsc_info['size'] = stbl_subAtom_size
            parse_stsc_atom(stbl_data[offset+8:offset+stbl_subAtom_size], stsc_info,track_id)
            
            stbl_info[stsc_info['type']]=stsc_info

        elif stbl_subAtom_type == 'stsz':
            stbl_subAtom_type = f"{stbl_subAtom_type}_{track_id}"
            stsz_info['type'] = stbl_subAtom_type
            stsz_info['size'] = stbl_subAtom_size
            parse_stsz_atom(stbl_data[offset+8:offset+stbl_subAtom_size], stsz_info,track_id)
            
            stbl_info[stsz_info['type']]=stsz_info

        elif stbl_subAtom_type == 'stco':
            stbl_subAtom_type = f"{stbl_subAtom_type}_{track_id}"
            stco_info['type'] = stbl_subAtom_type
            stco_info['size'] = stbl_subAtom_size
            parse_stco_atom(stbl_data[offset+8:offset+stbl_subAtom_size], stco_info, track_id)
            
            stbl_info[stco_info['type']]=stco_info
            
        elif stbl_subAtom_type == 'sgpd':
            stbl_subAtom_type = f"{stbl_subAtom_type}_{track_id}"
            sgpd_info['type'] = stbl_subAtom_type
            sgpd_info['size'] = stbl_subAtom_size
            parse_sgpd_atom(stbl_data[offset+8:offset+stbl_subAtom_size], sgpd_info, track_id)
            
            stbl_info[sgpd_info['type']]=sgpd_info
            
        elif stbl_subAtom_type == 'sbgp':
            stbl_subAtom_type = f"{stbl_subAtom_type}_{track_id}"
            sbgp_info['type'] = stbl_subAtom_type
            sbgp_info['size'] = stbl_subAtom_size
            parse_sbgp_atom(stbl_data[offset+8:offset+stbl_subAtom_size], sbgp_info, track_id)
            
            stbl_info[sbgp_info['type']]=sbgp_info
            

        offset += stbl_subAtom_size
def parse_stsd_atom(stsd_data, atom_info, track_id): # sample Description
    sample_info = {}
    version = struct.unpack('>B', stsd_data[0:1])[0]
    flags = struct.unpack('>3B', stsd_data[1:4])
    entry_count = struct.unpack('>I', stsd_data[4:8])[0]
    atom_info[f'version_{track_id}'] = version
    atom_info[f'flags_{track_id}'] = flags
    atom_info[f'entry_count_{track_id}'] = entry_count

    offset = 8
    for _ in range(entry_count):
        entry_size, entry_type = struct.unpack('>I4s', stsd_data[offset:offset+8])
        entry_type = entry_type.decode('utf-8')
        atom_info[f'entrySize_{track_id}'] = entry_size
        atom_info[f'entryType_{track_id}'] = entry_type
        sample_info['type'] = entry_type
        sample_info['size'] = entry_size
        if entry_type == 'avc1':
            H264_sample_description(stsd_data[offset+8:offset+entry_size], entry_size, sample_info)
        elif entry_type == 'hvc1':
            hevc_sample_description(stsd_data[offset+8:offset+entry_size], sample_info)
        elif  entry_type == 'mp4a':
            sample_description(stsd_data[offset+8:offset+entry_size], sample_info)
        atom_info[sample_info['type']]=sample_info
        offset += entry_size

def parse_stts_atom(stts_data, atom_info, track_id):
    version = struct.unpack('>B', stts_data[0:1])[0]
    flags = struct.unpack('>3B', stts_data[1:4])
    entry_count = struct.unpack('>I', stts_data[4:8])[0]
    atom_info[f'version_{track_id}'] = version
    atom_info[f'flags_{track_id}'] = flags
    atom_info[f'entry_count_{track_id}'] = entry_count

    offset = 8
    for i in range(entry_count):
        sample_count = struct.unpack('>I', stts_data[offset:offset+4])[0]
        sample_delta = struct.unpack('>I', stts_data[offset+4:offset+8])[0]
        atom_info[f'sample_count[{i}]_{track_id}'] = sample_count
        atom_info[f'sample_delta[{i}]_{track_id}'] = sample_delta

        offset += 8
def parse_stss_atom(stss_data, atom_info, track_id):
    version = struct.unpack('>B', stss_data[0:1])[0]
    flags = struct.unpack('>3B', stss_data[1:4])
    entry_count = struct.unpack('>I', stss_data[4:8])[0]
    atom_info[f'version_{track_id}'] = version
    atom_info[f'flags_{track_id}'] = flags
    atom_info[f'entry_count_{track_id}'] = entry_count

    offset = 8
    for i in range(entry_count):
        sample = struct.unpack('>I', stss_data[offset:offset+4])[0]
        atom_info[f'sample_number[{i}]_{track_id}'] = sample
        offset += 4

def parse_ctts_atom(ctts_data, atom_info, track_id):
    version = struct.unpack('>B', ctts_data[0:1])[0]
    flags = struct.unpack('>3B', ctts_data[1:4])
    entry_count = struct.unpack('>I', ctts_data[4:8])[0]
    atom_info[f'version_{track_id}'] = version
    atom_info[f'flags_{track_id}'] = flags
    atom_info[f'entry_count_{track_id}'] = entry_count

    offset = 8
    for i in range(entry_count):
        sample_count = struct.unpack('>I', ctts_data[offset:offset+4])[0]
        sample_offset = struct.unpack('>I', ctts_data[offset+4:offset+8])[0]
        atom_info[f'sample_count[{i}]_{track_id}'] = sample_count
        atom_info[f'sample_offset[{i}]_{track_id}'] = sample_offset
        offset += 8

def parse_stsc_atom(stsc_data, atom_info, track_id):
    version = struct.unpack('>B', stsc_data[0:1])[0]
    flags = struct.unpack('>3B', stsc_data[1:4])
    entry_count = struct.unpack('>I', stsc_data[4:8])[0]
    atom_info[f'version_{track_id}'] = version
    atom_info[f'flags_{track_id}'] = flags
    atom_info[f'entry_count_{track_id}'] = entry_count

    offset = 8
    for i in range(entry_count):
        first_chunk, samples_per_chunk, sample_description_index = struct.unpack('>3I', stsc_data[offset:offset+12])
        atom_info[f'first_chunk[{i}]_{track_id}'] = first_chunk
        atom_info[f'samples_per_chunk[{i}]_{track_id}'] = samples_per_chunk
        atom_info[f'sample_description_index[{i}]_{track_id}'] = sample_description_index

        offset += 12
def parse_stsz_atom(stsz_data, atom_info, track_id):
    version = struct.unpack('>B', stsz_data[0:1])[0]
    flags = struct.unpack('>3B', stsz_data[1:4])
    sample_size = struct.unpack('>I', stsz_data[4:8])[0]
    sample_count = struct.unpack('>I', stsz_data[8:12])[0]
    atom_info[f'version_{track_id}'] = version
    atom_info[f'flags_{track_id}'] = flags
    atom_info[f'sample_size_{track_id}'] = sample_size
    atom_info[f'sample_count_{track_id}'] = sample_count

    offset = 12
    if(sample_size == 0):
        for i in range(sample_count):
            sample = struct.unpack('>I', stsz_data[offset:offset+4])[0]
            atom_info[f'entry_size[{i}]_{track_id}'] = sample
            offset += 4
def parse_stco_atom(stco_data, atom_info, track_id):
    version = struct.unpack('>B', stco_data[0:1])[0]
    flags = struct.unpack('>3B', stco_data[1:4])
    entry_count = struct.unpack('>I', stco_data[4:8])[0]

    atom_info[f'version_{track_id}'] = version
    atom_info[f'flags_{track_id}'] = flags
    atom_info[f'entry_count_{track_id}'] = entry_count

    offset = 8
    for i in range(entry_count):
        chunk_offset = struct.unpack('>I', stco_data[offset:offset+4])[0]
        atom_info[f'chunk offset[{i}]_{track_id}'] = chunk_offset
        offset += 4
def parse_sgpd_atom(sgpd_data, atom_info, track_id):
    version = struct.unpack('>B', sgpd_data[0:1])[0]
    flags = struct.unpack('>3B', sgpd_data[1:4])
    grouping_type = struct.unpack('>4s', sgpd_data[4:8])[0]
    grouping_type = grouping_type.decode('utf-8')

    atom_info[f'version_{grouping_type}_{track_id}'] = version
    atom_info[f'flags_{grouping_type}_{track_id}'] = flags
    atom_info[f'grouping_type_{grouping_type}_{track_id}'] = grouping_type

    if grouping_type == 'roll':
        if version == 1:
            default_length = struct.unpack('>I', sgpd_data[8:12])[0]
            atom_info[f'default length_{grouping_type}_{track_id}'] = default_length
        elif version >= 2:
            default_sample_description_index = struct.unpack('>I', sgpd_data[8:12])[0]
            atom_info[f'default sample description index_{grouping_type}_{track_id}'] = default_sample_description_index
        
        entry_count = struct.unpack('>I', sgpd_data[12:16])[0]
        offset = 16
        atom_info[f'entry_count_{grouping_type}_{track_id}'] = entry_count

        for i in range(entry_count):
            if version == 1:
                if default_length == 0:
                    description_length = struct.unpack('>I', sgpd_data[offset:offset+4])[0]
                    roll_distance = struct.unpack('>i', sgpd_data[offset+4:offset+6])[0]
                    atom_info[f'description length[{i}]_{grouping_type}_{track_id}'] = description_length
                    offset += 6
                    continue

            roll_distance = struct.unpack('>h', sgpd_data[offset:offset+2])[0]
            atom_info[f'roll distance[{i}]_{grouping_type}_{track_id}'] = roll_distance
            offset += 2
    else:   # grouping_type - sync, tscl
        pass    # TODO need to understand the structure

def parse_sbgp_atom(sbgp_data, atom_info, track_id):
    version = struct.unpack('>B', sbgp_data[0:1])[0]
    flags = struct.unpack('>3B', sbgp_data[1:4])
    grouping_type = struct.unpack('>4s', sbgp_data[4:8])[0]
    grouping_type = grouping_type.decode('utf-8')

    atom_info[f'version_{track_id}'] = version
    atom_info[f'flags_{track_id}'] = flags
    atom_info[f'grouping_type_{track_id}'] = grouping_type

    if version == 1:
        grouping_type_param = struct.unpack('>I', sbgp_data[8:12])[0]
        entry_count = struct.unpack('>I', sbgp_data[12:16])[0]
        offset = 16
        atom_info[f'grouping type parameter_{track_id}'] = grouping_type_param
    else:
        entry_count = struct.unpack('>I', sbgp_data[8:12])[0]
        offset = 12
    atom_info[f'entry_count_{track_id}'] = entry_count

    for i in range(entry_count):
        sample_count = struct.unpack('>I', sbgp_data[offset:offset+4])[0]
        group_description_index = struct.unpack('>I', sbgp_data[offset+4:offset+8])[0]
        atom_info[f'sample count[{i}]_{track_id}'] = sample_count
        atom_info[f'group_description_index[{i}]_{track_id}'] = group_description_index
        offset += 8