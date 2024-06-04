import os
import sys
import math
import json
import struct
import base64
import pandas as pd
from dataclasses import dataclass
from bitstring import BitArray, ConstBitStream

from video.ftyp import *
from video.moof import *
from video.moov import *
from video.moov_subatom import *
from video.nal_parser import *


AtomDict = {}
codec_id = []
codec_check = ""

def videoParsing(video_path, AtomDict, boxSequence):   # return codec
    codec_id = []
    codec_check = ""
    fileName = os.path.basename(video_path)

    with open(video_path, 'rb') as video_file:
        initialByte = 0
        exist_mdat=0
        while True:
            atom_info = {}
            AtomSize = int.from_bytes(video_file.read(4), byteorder='big', signed=False)
            try:
                AtomType = video_file.read(4).decode('utf-8')
            except UnicodeDecodeError:
                break

            # Check for EOF
            if AtomSize == 0:
                break

            # Begin Process ReadAtom if Atomtype is in Atomlist
            ParentAtomlist = ['moov', 'ftyp', 'wide', 'mdat', 'free', 'beam', 'moof']  # Add other Atom types if needed

            if AtomType in ParentAtomlist:
                boxSequence.append(AtomType)
                if AtomSize == 1: # mdat
                    AtomSize = int.from_bytes(video_file.read(8), byteorder='big', signed=False)
                    if AtomType == 'mdat':
                        LabelsValue = video_file.read(AtomSize - 16)
                        atom_info['type'] = AtomType
                        AtomDict[atom_info['type']] = atom_info

                        initialByte += AtomSize
                        exist_mdat += 1
                        continue
                elif AtomSize < 0:
                    print(f"Atom does not match the standard: {AtomType}")
                
                atom_info['type'] = AtomType
                atom_info['size'] = AtomSize
                if AtomType == 'ftyp':
                    get_ftyp_tag(video_file, AtomType, AtomSize, atom_info)
                elif AtomType == 'moov':
                    get_moov_tag(video_file, AtomType, AtomSize, atom_info)
                elif AtomType == 'moof':
                    get_moof_tag(video_file, AtomType, AtomSize, atom_info)       
                else:   # beam, free, atomSize가 4바이트로 표현되는 mdat
                    LabelsValue = video_file.read(AtomSize - 8)  # Subtract 8 bytes for size and type fields
                
                AtomDict[atom_info['type']] = atom_info

                initialByte += AtomSize

            else:
                LabelsValue = video_file.read(AtomSize - 16)
                AtomUnknown = bytes.hex(LabelsValue)  # Store unknown Atom labels
                AtomDict['unknown box'] = AtomUnknown
                break
    track_id = [1, 2, 256, 512]
    audio_id = 0
    for i in track_id:
        try:
            check = AtomDict['moov'][f'trak_{i}'][f'mdia_{i}'][f'hdlr_{i}'].get(f"component_subtype_{i}")
            if check == 'vide':
                video_id = i
            elif check == 'soun':
                audio_id = i
        except KeyError:
            continue
    codec_check = AtomDict['moov'][f'trak_{video_id}'][f'mdia_{video_id}'][f'minf_{video_id}'][f'stbl_{video_id}'][f'stsd_{video_id}'].get(f'entryType_{video_id}')
    return codec_check


def featureExtraction(video_path, AtomDict, codec_check, boxSequence):
    fileName = os.path.basename(video_path)

    # Codec ID parsing
    if AtomDict['ftyp']['majorBrand'] == 'mp42':
        formatProfile = 'Base Media Version 2'
    elif AtomDict['ftyp']['majorBrand'] == 'qt  ':
        formatProfile = 'QuickTime'
    else:
        formatProfile = 'Base Media'
    
    codec_id.append(AtomDict['ftyp']['majorBrand'])
    codec_id.append(AtomDict['ftyp']['minorBrand'])

    # overall_bitrate parsing
    # (filesize * 8) / (duration * timescale)
    filesize = os.path.getsize(video_path)  # 파일 크기
    mvhd_duration = AtomDict['moov']['mvhd'].get(f"mvhd_duration")
    mvhd_timescale = AtomDict['moov']['mvhd'].get(f"mvhd_timeScale")
    duration = mvhd_duration / mvhd_timescale   # 동영상 재생 시간
    overall_bitrate = (filesize * 8 / duration) * 0.001
    overall_bitrate = round(overall_bitrate)

    # video_id, audio_id parsing
    # video id - moov/trak/mdia/hdlr/@component_subtype=vide 인 track id
    # audio id - moov/trak/mdia/hdlr/@component_subtype=soun 인 track id
    track_id = [1, 2, 256, 512]
    audio_id = 0
    for i in track_id:
        try:
            check = AtomDict['moov'][f'trak_{i}'][f'mdia_{i}'][f'hdlr_{i}'].get(f"component_subtype_{i}")
            if check == 'vide':
                video_id = i
            elif check == 'soun':
                audio_id = i
        except KeyError:
            continue
    if audio_id == 0:   # 음소거 영상
        audio_id = -1

    # video_bitrate parsing
    # video_bitrate = stream_size * 8 * video_timescale / video_duration
    # stream_size += stsz_entrySize
    video_stream_size = 0
    video_sample_count = AtomDict['moov'][f'trak_{video_id}'][f'mdia_{video_id}'][f'minf_{video_id}'][f'stbl_{video_id}'][f'stsz_{video_id}'].get(f'sample_count_{video_id}')
    for i in range(video_sample_count):
        video_stream_size += AtomDict['moov'][f'trak_{video_id}'][f'mdia_{video_id}'][f'minf_{video_id}'][f'stbl_{video_id}'][f'stsz_{video_id}'].get(f'entry_size[{i}]_{video_id}')
    video_timescale = AtomDict['moov'][f'trak_{video_id}'][f'mdia_{video_id}'][f'mdhd_{video_id}'].get(f'timeScale_{video_id}')
    video_duration = AtomDict['moov'][f'trak_{video_id}'][f'mdia_{video_id}'][f'mdhd_{video_id}'].get(f'duration_{video_id}')
    video_bitrate = (video_stream_size * 8 * video_timescale / video_duration) * 0.001
    video_bitrate = round(video_bitrate)

    boxSequence_str = " ".join(boxSequence)
    codecID_str = " ".join(codec_id)
    try:    # Writing_application
        writingApplication = AtomDict['moov']['udta']['meta']['ilst']['Encoder']['data'].get('encoder')
    except KeyError:
        writingApplication = None
    
    try:    # Movie_name
        movieName = AtomDict['moov']['udta']['titl'].get('movieName')
    except KeyError:
        movieName = None

    try:    # Copyright
        copyright = AtomDict['moov']['udta']['cprt'].get('copyright')
    except KeyError:
        copyright = None
    
    # format profile, sps, pps parsing (video_format_settings - entropy_coding_mode_flag(pps), num_ref frames(sps))
    if  codec_check == 'avc1':
        sps = AtomDict['moov'][f'trak_{video_id}'][f'mdia_{video_id}'][f'minf_{video_id}'][f'stbl_{video_id}'][f'stsd_{video_id}']['avc1']['avcC'].get('SPS_unit')
        rbsp = remove_epb(sps)
        rbsp = BitStream(bytes=rbsp)
        sps_rbsp = h264_SPS(rbsp)
        pps = AtomDict['moov'][f'trak_{video_id}'][f'mdia_{video_id}'][f'minf_{video_id}'][f'stbl_{video_id}'][f'stsd_{video_id}']['avc1']['avcC'].get('PPS_unit')
        rbsp = remove_epb(pps)
        rbsp = BitStream(bytes=rbsp)
        pps_rbsp = h264_PPS(rbsp)
        format_profile = sps_rbsp.get_formatProfile()
    else:   # hvc1
        vps = AtomDict['moov'][f'trak_{video_id}'][f'mdia_{video_id}'][f'minf_{video_id}'][f'stbl_{video_id}'][f'stsd_{video_id}']['hvc1']['hvcC']['nalUnits'].get(f'VPS')
        rbsp = remove_epb(vps)
        rbsp = BitStream(bytes=rbsp)
        vps_rbsp = h265_VPS(rbsp)

        sps = AtomDict['moov'][f'trak_{video_id}'][f'mdia_{video_id}'][f'minf_{video_id}'][f'stbl_{video_id}'][f'stsd_{video_id}']['hvc1']['hvcC']['nalUnits'].get(f'SPS')
        rbsp = remove_epb(sps)
        rbsp = BitStream(bytes=rbsp)
        sps_rbsp = h265_SPS(rbsp)
        pps = AtomDict['moov'][f'trak_{video_id}'][f'mdia_{video_id}'][f'minf_{video_id}'][f'stbl_{video_id}'][f'stsd_{video_id}']['hvc1']['hvcC']['nalUnits'].get(f'PPS')
        rbsp = remove_epb(pps)
        rbsp = BitStream(bytes=rbsp)
        pps_rbsp = h265_PPS(rbsp)
        format_profile = sps_rbsp.get_formatProfile()

    if codec_check == 'avc1':
        if sps_rbsp.order["num_ref_frames"] == 0:
            video_format_settings = 0
        else:
            video_format_settings = f'{sps_rbsp.order["num_ref_frames"]} Ref Frames'

        if pps_rbsp.order["entropy_coding_mode_flag"] == 1:
            video_format_settings = "CABAC " + video_format_settings
    else:
        video_format_settings = 0

    # width, height
    width = AtomDict['moov'][f'trak_{video_id}'][f'mdia_{video_id}'][f'minf_{video_id}'][f'stbl_{video_id}'][f'stsd_{video_id}'][f'{codec_check}'].get('width')
    height = AtomDict['moov'][f'trak_{video_id}'][f'mdia_{video_id}'][f'minf_{video_id}'][f'stbl_{video_id}'][f'stsd_{video_id}'][f'{codec_check}'].get('height')

    # title
    video_title = None
    video_title = AtomDict['moov'][f'trak_{video_id}'][f'mdia_{video_id}'][f'hdlr_{video_id}'].get(f'component_name_{video_id}')
    if video_title == "":
        video_title = "no value"
        
    if hasattr(sps_rbsp, 'vui') and sps_rbsp.vui:
        video_color_range = sps_rbsp.vui.order["video_full_range_flag"]
        video_color_primaries = sps_rbsp.vui.order["colour_primaries"]
        video_transfer_characteristics = sps_rbsp.vui.order["transfer_characteristics"]
        video_matrix_coefficients = sps_rbsp.vui.order["matrix_coefficients"]
    else:
        video_color_range = 0
        video_color_primaries = 0
        video_transfer_characteristics = 0
        video_matrix_coefficients = 0

    # video_color_primaries = AtomDict['moov'][f'trak_{video_id}'][f'mdia_{video_id}'][f'minf_{video_id}'][f'stbl_{video_id}'][f'stsd_{video_id}']['avc1']['colr'].get('color_primaries')
    # video_transfer_characteristics = AtomDict['moov'][f'trak_{video_id}'][f'mdia_{video_id}'][f'minf_{video_id}'][f'stbl_{video_id}'][f'stsd_{video_id}']['avc1']['colr'].get('transfer_characteristics')
    # video_matrix_coefficients = AtomDict['moov'][f'trak_{video_id}'][f'mdia_{video_id}'][f'minf_{video_id}'][f'stbl_{video_id}'][f'stsd_{video_id}']['avc1']['colr'].get('matrix_coefficient')

    # audio alternate group, title, bitrate
    # audio_bitrate = stream_size * 8 * audio_timescale / audio_duration
    # stream_size += stsz_entrySize
    audio_alternate_group=0
    audio_bitrate = 0
    if audio_id == -1:
        audio_title = None
        audio_alternate_group = -1
        audio_bitrate = -1
        audio_maxbitrate = 0
    else:
        audio_maxbitrate = AtomDict['moov'][f'trak_{audio_id}'][f'mdia_{audio_id}'][f'minf_{audio_id}'][f'stbl_{audio_id}'][f'stsd_{audio_id}']['mp4a']['esds'].get('max_bitrate')
        audio_stream_size = 0
        audio_sample_count = AtomDict['moov'][f'trak_{audio_id}'][f'mdia_{audio_id}'][f'minf_{audio_id}'][f'stbl_{audio_id}'][f'stsz_{audio_id}'].get(f'sample_count_{audio_id}')
        for i in range(audio_sample_count):
            audio_stream_size += AtomDict['moov'][f'trak_{audio_id}'][f'mdia_{audio_id}'][f'minf_{audio_id}'][f'stbl_{audio_id}'][f'stsz_{audio_id}'].get(f'entry_size[{i}]_{audio_id}')
        audio_timescale = AtomDict['moov'][f'trak_{audio_id}'][f'mdia_{audio_id}'][f'mdhd_{audio_id}'].get(f'timeScale_{audio_id}')
        audio_duration = AtomDict['moov'][f'trak_{audio_id}'][f'mdia_{audio_id}'][f'mdhd_{audio_id}'].get(f'duration_{audio_id}')
        audio_bitrate = (audio_stream_size * 8 * audio_timescale / audio_duration) * 0.001
        audio_bitrate = round(audio_bitrate)
        audio_title = None
        audio_title = AtomDict['moov'][f'trak_{audio_id}'][f'mdia_{audio_id}'][f'hdlr_{audio_id}'].get(f'component_name_{audio_id}')
        if audio_title == "":
            audio_title = "no value"
        audio_alternate_group = AtomDict['moov'][f'trak_{audio_id}'][f'tkhd_{audio_id}'].get(f'alternateGroup_{audio_id}')
    
    result = {'file_name': f'{fileName}', 'Format_profile': f'{formatProfile}', 'Codec_ID':f'{codecID_str}', 'Overall_bitrate':f'{overall_bitrate}', 'Writing_application':f'{writingApplication}','Movie_name':f'{movieName}', 'Copyright':f'{copyright}', 
              'Video_ID':f'{video_id}', 'Video_Format_profile':f'{format_profile}', 'Video_Format_settings':f'{video_format_settings}', 'Video_Bitrate':f'{video_bitrate}', 'Video_Width(Pixels)':f'{width}', 'Video_Height(Pixels)':f'{height}', 'Video_Title': f'{video_title}', 'Video_Color_range':f'{video_color_range}', 'Video_Color_primaries': f'{video_color_primaries}', 'Video_Transfer_characteristics':f'{video_transfer_characteristics}', 'Video_Matrix_coefficients': f'{video_matrix_coefficients}',
              'Audio_ID':f'{audio_id}', 'Audio_Bitrate':f'{audio_bitrate}', 'Audio_Title': f'{audio_title}', 'Audio_Alternate_group': f'{audio_alternate_group}', 'BOX_Sequence': f'{boxSequence_str}'}
    df = pd.DataFrame(result, index=[0])
    
    return df

def getNALU(AtomDict, codec_check):
    # Video ID parsing
    track_id = [1, 2, 256, 512]
    audio_id = 0
    for i in track_id:
        try:
            check = AtomDict['moov'][f'trak_{i}'][f'mdia_{i}'][f'hdlr_{i}'].get(f"component_subtype_{i}")
            if check == 'vide':
                video_id = i
            elif check == 'soun':
                audio_id = i
        except KeyError:
            continue
    
    if  codec_check == 'avc1':
        sps = AtomDict['moov'][f'trak_{video_id}'][f'mdia_{video_id}'][f'minf_{video_id}'][f'stbl_{video_id}'][f'stsd_{video_id}']['avc1']['avcC'].get('SPS_unit')
        rbsp = remove_epb(sps)
        rbsp = BitStream(bytes=rbsp)
        sps_rbsp = h264_SPS(rbsp)
        pps = AtomDict['moov'][f'trak_{video_id}'][f'mdia_{video_id}'][f'minf_{video_id}'][f'stbl_{video_id}'][f'stsd_{video_id}']['avc1']['avcC'].get('PPS_unit')
        rbsp = remove_epb(pps)
        rbsp = BitStream(bytes=rbsp)
        pps_rbsp = h264_PPS(rbsp)

        return sps_rbsp, pps_rbsp
    else:   # hvc1
        vps = AtomDict['moov'][f'trak_{video_id}'][f'mdia_{video_id}'][f'minf_{video_id}'][f'stbl_{video_id}'][f'stsd_{video_id}']['hvc1']['hvcC']['nalUnits'].get(f'VPS')
        rbsp = remove_epb(vps)
        rbsp = BitStream(bytes=rbsp)
        vps_rbsp = h265_VPS(rbsp)

        sps = AtomDict['moov'][f'trak_{video_id}'][f'mdia_{video_id}'][f'minf_{video_id}'][f'stbl_{video_id}'][f'stsd_{video_id}']['hvc1']['hvcC']['nalUnits'].get(f'SPS')
        rbsp = remove_epb(sps)
        rbsp = BitStream(bytes=rbsp)
        sps_rbsp = h265_SPS(rbsp)
        pps = AtomDict['moov'][f'trak_{video_id}'][f'mdia_{video_id}'][f'minf_{video_id}'][f'stbl_{video_id}'][f'stsd_{video_id}']['hvc1']['hvcC']['nalUnits'].get(f'PPS')
        rbsp = remove_epb(pps)
        rbsp = BitStream(bytes=rbsp)
        pps_rbsp = h265_PPS(rbsp)
        
        return vps_rbsp, sps_rbsp, pps_rbsp


# Usage
# video_path = sys.argv[1]
# codec_check = videoParsing(video_path, AtomDict)
# featureExtraction(video_path, AtomDict, codec_check)