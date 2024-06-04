import struct
from video.stbl import *
from video.minf_subatom import *

def parse_mdhd_atom(mdhd_data, mdhd_info, track_id):
    version = struct.unpack('>B', mdhd_data[0:1])[0]
    flag = struct.unpack('>3B', mdhd_data[1:4])
    if version == 1:
        creation_time = struct.unpack('>Q', mdhd_data[4:12])[0]
        modification_time = struct.unpack('>Q', mdhd_data[12:20])[0]
        time_scale = struct.unpack('>I', mdhd_data[20:24])[0]
        duration = struct.unpack('>Q', mdhd_data[24:32])[0]
        i = 32
    else:
        creation_time = struct.unpack('>I', mdhd_data[4:8])[0]
        modification_time = struct.unpack('>I', mdhd_data[8:12])[0]
        time_scale = struct.unpack('>I', mdhd_data[12:16])[0]
        duration = struct.unpack('>I', mdhd_data[16:20])[0]
        i = 20
    language = struct.unpack('>H', mdhd_data[i:i+2])[0]
    quality = struct.unpack('>H', mdhd_data[i+2:i+4])[0]
    
    mdhd_info[f'version_{track_id}'] = version
    mdhd_info[f'flags_{track_id}'] = flag
    mdhd_info[f'creationTime_{track_id}'] = creation_time
    mdhd_info[f'modificationTime_{track_id}'] = modification_time
    mdhd_info[f'timeScale_{track_id}'] = time_scale
    mdhd_info[f'duration_{track_id}'] = duration
    mdhd_info[f'language_{track_id}'] = language
    mdhd_info[f'quality_{track_id}'] = quality

def parse_hdlr_atom_in_trak(hdlr_data, hdlr_atom_size, hdlr_info, track_id): # atom size는 헤더 길이를 제외한 길이
    version = struct.unpack('>B', hdlr_data[0:1])[0]
    flags = struct.unpack('>3B', hdlr_data[1:4])
    component_type = hdlr_data[4:8].decode('utf-8')
    component_subtype = hdlr_data[8:12].decode('utf-8')
    component_manufacturer = hdlr_data[12:16].decode('utf-8', errors = 'ignore')
    component_flags_mask = struct.unpack('>I', hdlr_data[16:20])[0]
    component_name_length = hdlr_atom_size - 20 # component flags mask 뒤로는 010 Editor에서 분석 못함 (010 Editor에서는 rest field로 처리), 하지만 MP4 Box 도구에서는 component name field로 분석함
    component_name = hdlr_data[20:20 + component_name_length].decode('utf-8')
    component_name = component_name.replace('\u0000','')
    component_name = component_name.replace('\u0010','')
    
    hdlr_info[f'version_{track_id}'] = version
    hdlr_info[f'flags_{track_id}'] = flags
    hdlr_info[f'componentType_{track_id}'] = component_type
    hdlr_info[f'component_subtype_{track_id}'] = component_subtype
    hdlr_info[f'component_manufacturer_{track_id}'] = component_manufacturer
    hdlr_info[f'component_flags_mask_{track_id}'] = component_flags_mask
    hdlr_info[f'component_name_{track_id}'] = component_name

def parse_minf_atom(minf_data, minf_info, track_id):
    vmhd_info = {}
    smhd_info = {}
    dinf_info = {}
    stbl_info = {}

    offset = 0
    while offset < len(minf_data):
        minf_subAtom_size, minf_subAtom_type = struct.unpack('>I4s', minf_data[offset:offset+8])
        minf_subAtom_type = minf_subAtom_type.decode('utf-8')
        #print(f"                Sub-Atom Type: {minf_subAtom_type}, Sub-Atom Size: {minf_subAtom_size}")
        
        #atom_info[f'{minf_subAtom_type}_{track_id}'] = minf_subAtom_type
        if minf_subAtom_type == 'vmhd':
            minf_subAtom_type = f"{minf_subAtom_type}_{track_id}"
            vmhd_info['type'] = minf_subAtom_type
            vmhd_info['size'] = minf_subAtom_size
            parse_vmhd_atom(minf_data[offset+8:offset+minf_subAtom_size], vmhd_info)

            minf_info[vmhd_info['type']]=vmhd_info
        
        elif minf_subAtom_type == 'smhd':
            minf_subAtom_type = f"{minf_subAtom_type}_{track_id}"
            smhd_info['type'] = minf_subAtom_type
            smhd_info['size'] = minf_subAtom_size
            parse_smhd_atom(minf_data[offset+8:offset+minf_subAtom_size], smhd_info)

            minf_info[smhd_info['type']]=smhd_info

        elif minf_subAtom_type == 'dinf':
            minf_subAtom_type = f"{minf_subAtom_type}_{track_id}"
            dinf_info['type'] = minf_subAtom_type
            dinf_info['size'] = minf_subAtom_size
            parse_dinf_atom(minf_data[offset+8:offset+minf_subAtom_size], dinf_info, track_id)

            minf_info[dinf_info['type']]=dinf_info

            
        elif minf_subAtom_type == 'stbl':
            minf_subAtom_type = f"{minf_subAtom_type}_{track_id}"
            stbl_info['type'] = minf_subAtom_type
            stbl_info['size'] = minf_subAtom_size
            parse_stbl_atom(minf_data[offset+8:offset+minf_subAtom_size], stbl_info, track_id)

            minf_info[stbl_info['type']]=stbl_info

        offset += minf_subAtom_size

def parse_hdlr_atom(hdlr_data, hdlr_atom_size, hdlr_info):  # trak atom 밖에 있는 경우(track_id 사용 x)
    version = struct.unpack('>B', hdlr_data[0:1])[0]
    flags = struct.unpack('>3B', hdlr_data[1:4])
    component_type = hdlr_data[4:8].decode('utf-8')
    #component_type = struct.unpack('>I', hdlr_data[4:8])[0]
    component_subtype = hdlr_data[8:12].decode('utf-8')
    component_manufacturer = hdlr_data[12:16].decode('utf-8', errors = 'ignore')
    #component_manufacturer = struct.unpack('>I', hdlr_data[12:16])[0]
    #component_manufacturer = component_manufacturer.decode('utf-8')
    component_flags_mask = struct.unpack('>I', hdlr_data[16:20])[0]
    component_name_length = hdlr_atom_size - 20 # component flags mask 뒤로는 010 Editor에서 분석 못함 (010 Editor에서는 rest field로 처리), 하지만 MP4 Box 도구에서는 component name field로 분석함
    component_name = hdlr_data[20:20 + component_name_length].decode('utf-8')

    hdlr_info[f'version'] = version
    hdlr_info[f'flags'] = flags
    hdlr_info[f'componentType'] = component_type
    hdlr_info[f'component_subtype'] = component_subtype
    hdlr_info[f'component_manufacturer'] = component_manufacturer
    hdlr_info[f'component_flags_mask'] = component_flags_mask
    hdlr_info[f'component_name'] = component_name

def parse_meta_atom(meta_data, atom_info):
    offset = 0
    while offset < len(meta_data):
        meta_subAtom_size, meta_subAtom_type = struct.unpack('>I4s', meta_data[offset:offset+8])
        if meta_subAtom_size < 8:
            offset += 4
            continue

        meta_subAtom_type = meta_subAtom_type.decode('utf-8')
        atom_info[meta_subAtom_type] = meta_subAtom_type            
        if meta_subAtom_type == 'hdlr':
            hdlr_info = {}
            hdlr_info['type'] = meta_subAtom_type
            hdlr_info['size'] = meta_subAtom_size
            parse_hdlr_atom(meta_data[offset+8:offset+meta_subAtom_size], meta_subAtom_size-8, hdlr_info)
            atom_info[hdlr_info['type']] = hdlr_info
        elif meta_subAtom_type == 'ilst':
            ilst_info = {}
            ilst_info['type'] = meta_subAtom_type
            ilst_info['size'] = meta_subAtom_size
            parse_ilst_atom(meta_data[offset+8:offset+meta_subAtom_size], ilst_info)
            atom_info[ilst_info['type']] = ilst_info
        offset += meta_subAtom_size

def parse_ilst_atom(ilst_data, atom_info):
    ilst_info = {}
    offset = 0
    while offset < len(ilst_data):
        ilst_subAtom_size, ilst_subAtom_type = struct.unpack('>I4s', ilst_data[offset:offset+8])
        if ilst_subAtom_size < 8:
            offset += 4
            continue
        
        if ilst_subAtom_type == b'\xa9nam':
            ilst_info['type'] = 'Title'
            ilst_info['size'] = ilst_subAtom_size
            parse_metadata_atom(ilst_data[offset+8:offset+ilst_subAtom_size], "Title", ilst_info)
        elif ilst_subAtom_type == b'\xa9art':
            ilst_info['type'] = 'Artist'
            ilst_info['size'] = ilst_subAtom_size
            parse_metadata_atom(ilst_data[offset+8:offset+ilst_subAtom_size], "Artist", ilst_info)
        elif ilst_subAtom_type == b'\xa9too':
            ilst_info['type'] = 'Encoder'
            ilst_info['size'] = ilst_subAtom_size
            sub_info = {}
            sub_size, sub_type = struct.unpack('>I4s', ilst_data[offset+8:offset+16])
            sub_type = sub_type.decode('utf-8')
            sub_info['type'] = sub_type
            sub_info['size'] = sub_size
            encoder = ilst_data[offset+16:offset+ilst_subAtom_size].decode('utf-8')
            encoder = encoder.replace('\u0000','')
            encoder = encoder.replace('\u0001','')
            sub_info['encoder'] = encoder
            ilst_info[sub_info['type']] = sub_info
        elif ilst_subAtom_type == b'\xa9cmt':
            ilst_info['type'] = 'Comment'
            ilst_info['size'] = ilst_subAtom_size
            sub_info = {}
            sub_size, sub_type = struct.unpack('>I4s', ilst_data[offset+8:offset+16])
            sub_type = sub_type.decode('utf-8')
            sub_info['type'] = sub_type
            sub_info['size'] = sub_size
        elif ilst_subAtom_type == b'data':
            ilst_info['type'] = ilst_subAtom_type.decode('utf-8')
            ilst_info['size'] = ilst_subAtom_size
            ilst_info['data'] = ilst_data[offset:offset+8].decode('utf-8')
        else:
            offset += 8
            continue

        atom_info[ilst_info['type']] = ilst_info
        offset += ilst_subAtom_size

def parse_metadata_atom(metadata_data, metadata_name, atom_info):
    metadata_value = metadata_data.decode('utf-8')
    atom_info['metadata value'] = metadata_value
