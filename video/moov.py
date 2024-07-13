import struct
from video.moov_subatom import *

def get_moov_tag(video_file, AtomType, moovAtomSize, atom_info):
    moov_subAtomList = ['mvhd', 'trak', 'udta', 'iods']  # Add other Atom types if needed
    trak_count = 1
    mvhd_data = None
    moov_info = {}
    mvhd_info = {}
    while moovAtomSize >= 8:
        atom_header = video_file.read(8)
        AtomSize, AtomType = struct.unpack('>I4s', atom_header)
        AtomType = AtomType.decode('utf-8')

        if AtomType == 'mvhd':
            #moov_info['type'] = AtomType
            mvhd_info['type'] = AtomType
            mvhd_info['size'] = AtomSize
            mvhd_data = video_file.read(AtomSize - 8)
            mvhd_version = struct.unpack('>B', mvhd_data[0:1])[0]
            mvhd_flags = struct.unpack('>3B', mvhd_data[1:4])

            if mvhd_version == 1:
                mvhd_creation_time = struct.unpack('>Q', mvhd_data[4:12])[0]
                mvhd_modification_time = struct.unpack('>Q', mvhd_data[12:20])[0]
                mvhd_time_scale = struct.unpack('>I', mvhd_data[20:24])[0]
                mvhd_duration = struct.unpack('>Q', mvhd_data[24:32])[0]
                i=32
                
            else:
                mvhd_creation_time = struct.unpack('>I', mvhd_data[4:8])[0]
                mvhd_modification_time = struct.unpack('>I', mvhd_data[8:12])[0]
                mvhd_time_scale = struct.unpack('>I', mvhd_data[12:16])[0]
                mvhd_duration = struct.unpack('>I', mvhd_data[16:20])[0]
                i=20
            
            mvhd_preferredRate = struct.unpack('>f', mvhd_data[i:i+4])[0]
            mvhd_preferredVolume = struct.unpack('>e', mvhd_data[i+4:i+6])[0]
            mvhd_reserved = struct.unpack('>10B', mvhd_data[i+6:i+16])[0]
            mvhd_matrixStructure = struct.unpack('>9I', mvhd_data[i+16:i+52])[0]
            mvhd_previewTime = struct.unpack('>I', mvhd_data[i+52:i+56])[0]
            mvhd_previewDuration = struct.unpack('>I', mvhd_data[i+56:i+60])[0]
            mvhd_posterTime = struct.unpack('>I', mvhd_data[i+60:i+64])[0]
            mvhd_selectionTime = struct.unpack('>I', mvhd_data[i+64:i+68])[0]
            mvhd_selectionDurationme = struct.unpack('>I', mvhd_data[i+68:i+72])[0]
            mvhd_currentTime = struct.unpack('>I', mvhd_data[i+72:i+76])[0]
            mvhd_nextTrackID = struct.unpack('>I', mvhd_data[i+76:i+80])[0]

            mvhd_info['mvhd_version'] = mvhd_version
            mvhd_info['mvhd_flags'] = mvhd_flags
            mvhd_info['mvhd_creationTime'] = mvhd_creation_time
            mvhd_info['mvhd_modificationTime'] = mvhd_modification_time
            mvhd_info['mvhd_timeScale'] = mvhd_time_scale
            mvhd_info['mvhd_duration'] = mvhd_duration
            mvhd_info['mvhd_preferredRate'] = mvhd_preferredRate
            mvhd_info['mvhd_preferredVolume'] = mvhd_preferredVolume
            mvhd_info['mvhd_reserved'] = mvhd_reserved
            mvhd_info['mvhd_matrixStructure'] = mvhd_matrixStructure
            mvhd_info['mvhd_previewTime'] = mvhd_previewTime
            mvhd_info['mvhd_previewDuration'] = mvhd_previewDuration
            mvhd_info['mvhd_posterTime'] = mvhd_posterTime
            mvhd_info['mvhd_selectionTime'] = mvhd_selectionTime
            mvhd_info['mvhd_selectionDurationme'] = mvhd_selectionDurationme
            mvhd_info['mvhd_currentTime'] = mvhd_currentTime
            mvhd_info['mvhd_nextTrackID'] = mvhd_nextTrackID
            atom_info[mvhd_info['type']] = mvhd_info
            #atom_info[moov_info['type']]=mvhd_info
            moovAtomSize -= 8
        elif AtomType == 'trak':
            tkhd_info = {}

            trak1_info = {}
            trak2_info = {}
            trak256_info = {}
            trak512_info = {}
            trak_subAtomList = ['tkhd', '','mdia']  # Add other Atom types if needed
            size = AtomSize - 8
            while size > 8:  # Atom header size is 8 bytes (size + type)
                atom_header = video_file.read(8)
                atom_size, atom_type = struct.unpack('>I4s', atom_header)
                atom_type = atom_type.decode('utf-8')

                # If the sub-atom contains sub-atoms, recursively parse them
                if atom_size == 1:
                    extended_size = struct.unpack('>Q', video_file.read(8))[0]
                    atom_size = extended_size

                if atom_size >= 8:  # At least 8 bytes are required for a valid atom
                    #video_file.seek(atom_size - 8, 1)
                    data = video_file.read(atom_size-8)
                    if atom_type == 'tkhd':
                        tkhd_version = struct.unpack('>B', data[0:1])[0]
                        tkhd_flags = struct.unpack('>3B', data[1:4])
                        if tkhd_version == 1:
                            tkhd_creation_time = struct.unpack('>Q', data[4:12])[0]
                            tkhd_modification_time = struct.unpack('>Q', data[12:20])[0]
                            track_id = struct.unpack('>I', data[20:24])[0]
                            tkhd_reserved1 = struct.unpack('>I', data[24:28])[0]
                            tkhd_duration = struct.unpack('>Q', data[28:36])[0]
                            i=36
                        else:
                            tkhd_creation_time = struct.unpack('>I', data[4:8])[0]
                            tkhd_modification_time = struct.unpack('>I', data[8:12])[0]
                            track_id = struct.unpack('>I', data[12:16])[0]
                            tkhd_reserved1 = struct.unpack('>I', data[16:20])[0]
                            tkhd_duration = struct.unpack('>I', data[20:24])[0]
                            i=24
                        
                        tkhd_reserved2 = struct.unpack('>Q', data[i:i+8])[0]
                        tkhd_layer = struct.unpack('>H', data[i+8:i+10])[0]
                        tkhd_alt_group = struct.unpack('>H', data[i+10:i+12])[0]
                        tkhd_volume = struct.unpack('>e', data[i+12: i+14])[0]
                        tkhd_reserved3 = struct.unpack('>H', data[i+14:i+16])[0]
                        tkhd_matrixStructure = struct.unpack('>9I', data[i+16:i+52])[0]
                        tkhd_width = struct.unpack('>I', data[i+52:i+56])[0]
                        tkhd_height = struct.unpack('>I', data[i+56:i+60])[0]
                        
                        AtomType = f"{AtomType}_{track_id}"
                        atom_type = f"{atom_type}_{track_id}"
                        moov_info['type'] = AtomType
                        #trak_info[f'{AtomType}_{track_id}'] = AtomType

                        tkhd_info['type'] = atom_type
                        tkhd_info['size'] = atom_size
                        tkhd_info[f'version_{track_id}'] = tkhd_version
                        tkhd_info[f'flags_{track_id}'] = tkhd_flags
                        tkhd_info[f'creationTime_{track_id}'] = tkhd_creation_time
                        tkhd_info[f'modificationTime_{track_id}'] = tkhd_modification_time
                        tkhd_info[f'trakID_{track_id}'] = track_id
                        tkhd_info[f'reserved1_{track_id}'] = tkhd_reserved1
                        tkhd_info[f'layer_{track_id}'] = tkhd_layer
                        tkhd_info[f'alternateGroup_{track_id}'] = tkhd_alt_group
                        tkhd_info[f'volume_{track_id}'] = tkhd_volume
                        tkhd_info[f'reserved2_{track_id}'] = tkhd_reserved2
                        tkhd_info[f'matrixStructure_{track_id}'] = tkhd_matrixStructure
                        tkhd_info[f'width_{track_id}'] = tkhd_width
                        tkhd_info[f'height_{track_id}'] = tkhd_height
                        
                        if track_id == 1:
                            trak1_info['type'] = AtomType
                            trak1_info['size'] = AtomSize
                            trak1_info[tkhd_info['type']]=tkhd_info
                            atom_info[moov_info['type']]=trak1_info
                        elif track_id ==2:
                            trak2_info['type'] = AtomType
                            trak2_info['size'] = AtomSize
                            trak2_info[tkhd_info['type']]=tkhd_info
                            atom_info[moov_info['type']]=trak2_info
                        elif track_id == 256:
                            trak256_info['type'] = AtomType
                            trak256_info['size'] = AtomSize
                            trak256_info[tkhd_info['type']]=tkhd_info
                            atom_info[moov_info['type']]=trak256_info
                        else:
                            trak512_info['type'] = AtomType
                            trak512_info['size'] = AtomSize
                            trak512_info[tkhd_info['type']]=tkhd_info
                            atom_info[moov_info['type']]=trak512_info

                    elif atom_type == 'edts':
                        edts_info = {}
                        elst_info = {}

                        atom_type = f'{atom_type}_{track_id}'
                        elst_size, elst_type = struct.unpack('>I4s', data[0:8])
                        elst_type = elst_type.decode('utf-8')

                        elst_version = struct.unpack('>B', data[8:9])[0]
                        elst_flags = struct.unpack('>3B', data[9:12])
                        elst_numOfEntries = struct.unpack('>I', data[12:16])[0]


                        edts_info['type'] = atom_type
                        edts_info['size'] = atom_size
                        #moov_info['type'] = AtomType

                        elst_info['type'] = elst_type
                        elst_info['size'] = elst_size
                        elst_info[f'version_{track_id}'] = elst_version
                        elst_info[f'flags_{track_id}'] = elst_flags
                        elst_info[f'NumOfEntries_{track_id}'] = elst_numOfEntries

                        offset = 16
                        for i in range(elst_numOfEntries):
                            if elst_version == 1:
                                segment_duration, media_time, media_rate = struct.unpack('>qii', data[offset:offset+16])
                                offset += 16
                            else:
                                segment_duration, media_time, media_rate = struct.unpack('>iii', data[offset:offset+12])
                                offset += 12

                            elst_info[f'segmentDuration[{i}]_{track_id}'] = segment_duration
                            elst_info[f'mediaTime[{i}]_{track_id}'] = media_time
                            elst_info[f'mediaRate[{i}]_{track_id}'] = media_rate
                        edts_info[elst_info['type']] = elst_info

                        if track_id == 1:
                            trak1_info[edts_info['type']] = edts_info
                            atom_info[moov_info['type']]=trak1_info
                        elif track_id ==2:
                            trak2_info[edts_info['type']] = edts_info
                            atom_info[moov_info['type']]=trak2_info
                        elif track_id == 256:
                            trak256_info[edts_info['type']] = edts_info
                            atom_info[moov_info['type']]=trak256_info
                        else:
                            trak512_info[edts_info['type']] = edts_info
                            atom_info[moov_info['type']]=trak512_info

                    elif atom_type == 'mdia':
                        mdia_info = {}
                        mdhd_info = {}
                        hdlr_info = {}
                        minf_info = {}

                        atom_type = f"{atom_type}_{track_id}"
                        mdia_info['type'] = atom_type
                        mdia_info['size'] = atom_size

                        offset = 0
                        mdia_relativeOrder = 1
                        while offset < len(data):
                            mdia_subAtom_size, mdia_subAtom_type = struct.unpack('>I4s', data[offset:offset+8])
                            mdia_subAtom_type = mdia_subAtom_type.decode('utf-8')
                            
                            if mdia_subAtom_type == 'mdhd':
                                mdia_subAtom_type = f"{mdia_subAtom_type}_{track_id}"
                                mdhd_info['type'] = mdia_subAtom_type
                                mdhd_info['size'] = mdia_subAtom_size
                                parse_mdhd_atom(data[offset+8:offset+atom_size], mdhd_info, track_id)
                                mdia_info[mdhd_info['type']]=mdhd_info
                                if track_id == 1:
                                    trak1_info[mdia_info['type']] = mdia_info
                                    atom_info[moov_info['type']]=trak1_info
                                elif track_id ==2:
                                    trak2_info[mdia_info['type']] = mdia_info
                                    atom_info[moov_info['type']]=trak2_info
                                elif track_id == 256:
                                    trak256_info[mdia_info['type']] = mdia_info
                                    atom_info[moov_info['type']]=trak256_info
                                else:
                                    trak512_info[mdia_info['type']] = mdia_info
                                    atom_info[moov_info['type']]=trak512_info

                            elif mdia_subAtom_type == 'hdlr':
                                mdia_subAtom_type = f"{mdia_subAtom_type}_{track_id}"
                                hdlr_info['type'] = mdia_subAtom_type
                                hdlr_info['size'] = mdia_subAtom_size
                                parse_hdlr_atom_in_trak(data[offset+8:offset+atom_size], mdia_subAtom_size-8, hdlr_info, track_id)
                                mdia_info[hdlr_info['type']]=hdlr_info
                                if track_id == 1:
                                    trak1_info[mdia_info['type']] = mdia_info
                                    atom_info[moov_info['type']]=trak1_info
                                elif track_id ==2:
                                    trak2_info[mdia_info['type']] = mdia_info
                                    atom_info[moov_info['type']]=trak2_info
                                elif track_id == 256:
                                    trak256_info[mdia_info['type']] = mdia_info
                                    atom_info[moov_info['type']]=trak256_info
                                else:
                                    trak512_info[mdia_info['type']] = mdia_info
                                    atom_info[moov_info['type']]=trak512_info
                                
                            elif mdia_subAtom_type == 'minf':
                                mdia_subAtom_type = f"{mdia_subAtom_type}_{track_id}"
                                minf_info['type'] = mdia_subAtom_type
                                minf_info['size'] = mdia_subAtom_size
                                parse_minf_atom(data[offset+8:offset+atom_size], minf_info, track_id)
                                mdia_info[minf_info['type']]=minf_info
                                if track_id == 1:
                                    trak1_info[mdia_info['type']] = mdia_info
                                    atom_info[moov_info['type']]=trak1_info
                                elif track_id ==2:
                                    trak2_info[mdia_info['type']] = mdia_info
                                    atom_info[moov_info['type']]=trak2_info
                                elif track_id == 256:
                                    trak256_info[mdia_info['type']] = mdia_info
                                    atom_info[moov_info['type']]=trak256_info
                                else:
                                    trak512_info[mdia_info['type']] = mdia_info
                                    atom_info[moov_info['type']]=trak512_info

                            offset += mdia_subAtom_size
                            mdia_relativeOrder += 1
                        
                else:
                    break
                size -= atom_size
            trak_count += 1
        elif AtomType == 'udta':
            udta_info = {}
            meta_info = {}
            exvr_info = {}
            titl_info = {}
            cprt_info = {}

            udta_info['type'] = AtomType
            udta_info['size'] = AtomSize

            size = AtomSize - 8
            while size > 8:  # Atom header size is 8 bytes (size + type)
                atom_header = video_file.read(8)
                atom_size, atom_type = struct.unpack('>I4s', atom_header)

                try:
                    atom_type = atom_type.decode('utf-8')
                except UnicodeDecodeError:
                    atom_type = 'unknown'

                # If the sub-atom contains sub-atoms, recursively parse them
                if atom_size == 1:
                    extended_size = struct.unpack('>Q', video_file.read(8))[0]
                    atom_size = extended_size

                offset = 0
                if atom_size >= 8:  # At least 8 bytes are required for a valid atom
                    #video_file.seek(atom_size - 8, 1)
                    udta_data = video_file.read(atom_size-8)
                    if atom_type == 'meta':
                        meta_info['type'] = atom_type
                        meta_info['size'] = atom_size   
                        parse_meta_atom(udta_data[offset:offset+atom_size], meta_info)
                        udta_info[meta_info['type']] = meta_info
                    
                    elif atom_type == 'exvr':
                        exvr_info['type'] = atom_type
                        exvr_info['size'] = atom_size
                        udta_data = udta_data.decode('utf-8', errors='ignore')
                        exvr_info['exvr'] = udta_data
                        udta_info[exvr_info['type']] = exvr_info
                    elif atom_type == 'titl':
                        titl_info['type'] = atom_type
                        titl_info['size'] = atom_size
                        movieName = udta_data.decode('utf-8', errors='ignore')
                        movieName = movieName.replace('\u0000','')
                        movieName = movieName.replace('U','')
                        titl_info['movieName'] = movieName
                        udta_info[titl_info['type']] = titl_info
                    elif atom_type == 'cprt':
                        cprt_info['type'] = atom_type
                        cprt_info['size'] = atom_size
                        copyright = udta_data.decode('utf-8', errors = 'ignore')
                        copyright = copyright.replace('\u0000','')
                        copyright = copyright.replace('\u0015','')
                        cprt_info['copyright'] = copyright
                        udta_info[cprt_info['type']] = cprt_info
                    else:
                        udta_info['unknown field'] = udta_data[offset:offset+atom_size]
                else:
                    break
                size -= atom_size
            atom_info[udta_info['type']] = udta_info
        elif AtomType == 'meta':
            meta_info = {}

            meta_data = video_file.read(AtomSize-8)
            meta_info['type'] = AtomType
            meta_info['size'] = AtomSize
            parse_meta_atom(meta_data, meta_info)
            atom_info[meta_info['type']] = meta_info
        else:
            video_file.seek(AtomSize - 8, 1)
        
        
        
        moovAtomSize -= AtomSize