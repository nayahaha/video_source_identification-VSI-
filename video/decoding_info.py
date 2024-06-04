import struct
from bitstring import BitArray, ConstBitStream

def H264_sample_description(sample_data, sample_size, atom_info):
    avc_info = {}
    pasp_info = {}
    colr_info = {}
    reserved1 = struct.unpack('>6B', sample_data[0:6])[0]
    data_reference_index = struct.unpack('>H', sample_data[6:8])[0]
    pre_defined1 = struct.unpack('>H', sample_data[8:10])[0]
    reserved2 = struct.unpack('>H', sample_data[10:12])[0]
    pre_defined2 = struct.unpack('>3I', sample_data[12:24])[0]
    width = struct.unpack('>H', sample_data[24:26])[0]
    height = struct.unpack('>H', sample_data[26:28])[0]
    Horizresolution = sample_data[28:32]
    Horizresolution = bytes.hex(Horizresolution)
    Vertiresolution = sample_data[32:36]
    Vertiresolution = bytes.hex(Vertiresolution)
    reserved3 = struct.unpack('>I', sample_data[36:40])[0]
    frame_count = struct.unpack('>H', sample_data[40:42])[0]    # sample 당 frame 개수
    compressor_name = struct.unpack('>32s', sample_data[42:74])[0]
    compressor_name = compressor_name.decode('utf-8')
    depth = struct.unpack('>H', sample_data[74:76])[0]
    pre_defined3 = struct.unpack('>h', sample_data[76:78])[0]

    atom_info['reserved1'] = reserved1
    atom_info['data_reference_index'] = data_reference_index
    atom_info['pre_defined1'] = pre_defined1
    atom_info['reserved2'] = reserved2
    atom_info['pre_defined2'] = pre_defined2
    atom_info['width'] = width
    atom_info['height'] = height
    atom_info['Horizresolution'] = Horizresolution
    atom_info['Vertiresolution'] = Vertiresolution
    atom_info['reserved3'] = reserved3
    atom_info['frame_count'] = frame_count
    atom_info['compressor_name'] = compressor_name
    atom_info['depth'] = depth
    atom_info['pre_defined3'] = pre_defined3

    size = (sample_size-8) - 78 #avc1 atom header size(8bytes)만큼 빼기
    sub_data = sample_data[78:78+size]
    offset = 0
    while size > 8:  # Atom header size is 8 bytes (size + type)
        atom_size, atom_type = struct.unpack('>I4s', sub_data[offset:offset+8])
        atom_type = atom_type.decode('utf-8')
        if atom_size >= 8:
            if atom_type == 'avcC':
                avc_info['type'] = atom_type
                avc_info['size'] = atom_size
                parse_avcc(sub_data[offset+8:offset+atom_size], avc_info)
                atom_info[avc_info['type']]=avc_info
            elif atom_type == 'pasp':
                pasp_info['type'] = atom_type
                pasp_info['size'] = atom_size   
                atom_info[pasp_info['type']] = pasp_info
            elif atom_type == 'colr':
                colr_info['type'] = atom_type
                colr_info['size'] = atom_size
                parse_colr(sub_data[offset+8:offset+8+atom_size], colr_info)
                atom_info[colr_info['type']] = colr_info
            else:
                atom_info['unknown field'] = sub_data[offset:offset+atom_size]
        else:
            break
        offset += atom_size
        size -= atom_size

    # temp = sample_size - 8 - (86+avcc_boxSize-8)
    # if temp > 0:
    #     sub_boxSize, subType = struct.unpack('>I4s', sample_data[86+avcc_boxSize-8:86+avcc_boxSize-4])
    #     if subType == 'pasp':
    #         pasp_info['type']=subType
    #         pasp_info['size'] = sub_boxSize
    
def  sample_description(sample_data, atom_info):
    esds_info = {}

    reserved1 = struct.unpack('>6B', sample_data[0:6])[0]
    data_reference_index = struct.unpack('>H', sample_data[6:8])[0]
    reserved2 = struct.unpack('>8B', sample_data[8:16])[0]
    reserved3 = struct.unpack('>H', sample_data[16:18])[0]
    reserved4 = struct.unpack('>H', sample_data[18:20])[0]
    reserved5 = struct.unpack('>I', sample_data[20:24])[0]
    timeScale = struct.unpack('>H', sample_data[24:26])[0]
    reserved6 = struct.unpack('>H', sample_data[26:28])[0]

    atom_info['reserved1'] = reserved1
    atom_info['data_reference_index'] = data_reference_index
    atom_info['reserved2'] = reserved2
    atom_info['reserved3'] = reserved3
    atom_info['reserved4'] = reserved4
    atom_info['reserved5'] = reserved5
    atom_info['timeScale'] = timeScale
    atom_info['reserved6'] = reserved6

    offset = 28
    while offset < len(sample_data):
        subAtom_size, subAtom_type = struct.unpack('>I4s', sample_data[offset:offset+8])
        subAtom_type = subAtom_type.decode('utf-8')

        if subAtom_type == 'esds':
            esds_info['type'] = subAtom_type
            esds_info['size'] = subAtom_size
            parse_esds(sample_data[offset+8:offset+subAtom_size], esds_info)
            atom_info[esds_info['type']] = esds_info
            break
        else:
            offset += 8


def parse_avcc(avcc_data, atom_info):
    configuration_version = struct.unpack('>B', avcc_data[0:1])[0]
    avcProfileIndication = struct.unpack('>B', avcc_data[1:2])[0]
    profile_compatibility = struct.unpack('>B', avcc_data[2:3])[0]
    avcLevelIndication = struct.unpack('>B', avcc_data[3:4])[0]
    bit = BitArray(uint=avcc_data[4], length=8).bin
    reserved_0 = int(bit[0:6], 2)
    length_size_minus_one = int(bit[6:8], 2)
    bit = BitArray(uint=avcc_data[5], length=8).bin
    reserved_1 = int(bit[0:3], 2)
    numOfSPS = int(bit[3:8], 2)
    for _ in range(numOfSPS):
        SPS_length = struct.unpack('>h', avcc_data[6:8])[0]
        SPS_unit = avcc_data[8:8+SPS_length]    # type: byte
        # SPS_unit = bytes.hex(SPS_unit)
    
    SPSend = 8+SPS_length
    numOfPPS = struct.unpack('>b', avcc_data[SPSend:SPSend+1])[0]
    for _ in range(numOfPPS):
        PPS_length = struct.unpack('>h', avcc_data[SPSend+1:SPSend+3])[0]
        PPS_unit = avcc_data[SPSend+3:SPSend+3+PPS_length]
        # PPS_unit = bytes.hex(PPS_unit)
    

    atom_info['configuration_version'] = configuration_version
    atom_info['avc_profile_indication'] = avcProfileIndication
    atom_info['profile_compatibility'] = profile_compatibility
    atom_info['avc_level_indication'] = avcLevelIndication
    atom_info['reserved_0'] = reserved_0
    atom_info['length_size_minus_one'] = length_size_minus_one
    atom_info['reserved_1'] = reserved_1
    atom_info['numOfSPS'] = numOfSPS
    atom_info['SPS_length'] = SPS_length
    atom_info['SPS_unit'] = SPS_unit
    atom_info['numOfPPS'] = numOfPPS
    atom_info['PPS_length'] = PPS_length
    atom_info['PPS_unit'] = PPS_unit

def parse_esds(esds_data, atom_info):
    version = struct.unpack('>B', esds_data[0:1])[0]
    flags = struct.unpack('>3B', esds_data[1:4])
    tag_objectDescriptor = struct.unpack('>B', esds_data[4:5])[0]
    if struct.unpack('>3s', esds_data[5:8])[0] == b'\x80\x80\x80':
        include_80_1 = struct.unpack('>3s', esds_data[5:8])[0]
        length = struct.unpack('>B', esds_data[8:9])[0]
        ES_ID = struct.unpack('>2B', esds_data[9:11])[0]
        flags_etc = struct.unpack('>B', esds_data[11:12])[0]
        tag_ES_Descriptor = struct.unpack('>B', esds_data[12:13])[0]
        include_80_2 = struct.unpack('>3s', esds_data[13:16])[0]
        ESD_length = struct.unpack('>B', esds_data[16:17])[0]
        MPEG_audio = struct.unpack('>B', esds_data[17:18])[0]
        bit = BitArray(uint=esds_data[18], length=8).bin
        streamType = int(bit[0:6], 2)
        ESD_flags = int(bit[6:8], 2)
        reserved = struct.unpack('>3B', esds_data[19:22])[0]
        maxBitrate = struct.unpack('>I', esds_data[22:26])[0]
        avgBitrate = struct.unpack('>I', esds_data[26:30])[0]
        temp = maxBitrate * 0.001
        maxBitrate = round(temp, 1)
        temp = avgBitrate * 0.001
        avgBitrate = (temp, 1)
    else:
        length = struct.unpack('>B', esds_data[5:6])[0]
        ES_ID = struct.unpack('>2B', esds_data[6:8])[0]
        flags_etc = struct.unpack('>B', esds_data[8:9])[0]
        tag_ES_Descriptor = struct.unpack('>B', esds_data[9:10])[0]
        ESD_length = struct.unpack('>B', esds_data[10:11])[0]
        MPEG_audio = struct.unpack('>B', esds_data[11:12])[0]
        bit = BitArray(uint=esds_data[12], length=8).bin
        streamType = int(bit[0:6], 2)
        ESD_flags = int(bit[6:8], 2)
        reserved = struct.unpack('>3B', esds_data[13:16])[0]
        maxBitrate = struct.unpack('>I', esds_data[16:20])[0]
        avgBitrate = struct.unpack('>I', esds_data[20:24])[0]
        temp = maxBitrate * 0.001
        maxBitrate = round(temp, 1)
        temp = avgBitrate * 0.001
        avgBitrate = (temp, 1)
    # ...
    atom_info['max_bitrate'] = maxBitrate
    atom_info['avg_bitrate'] = avgBitrate

def hevc_sample_description(sample_data, atom_info):
    hvc_info = {}
    reserved1 = struct.unpack('>6B', sample_data[0:6])[0]
    data_reference_index = struct.unpack('>H', sample_data[6:8])[0]
    pre_defined1 = struct.unpack('>H', sample_data[8:10])[0]
    reserved2 = struct.unpack('>H', sample_data[10:12])[0]
    pre_defined2 = struct.unpack('>3I', sample_data[12:24])[0]
    width = struct.unpack('>H', sample_data[24:26])[0]
    height = struct.unpack('>H', sample_data[26:28])[0]
    Horizresolution = sample_data[28:32]
    Horizresolution = bytes.hex(Horizresolution)
    Vertiresolution = sample_data[32:36]
    Vertiresolution = bytes.hex(Vertiresolution)
    reserved3 = struct.unpack('>I', sample_data[36:40])[0]
    frame_count = struct.unpack('>H', sample_data[40:42])[0]    # sample 당 frame 개수
    compressor_name = struct.unpack('>32s', sample_data[42:74])[0]
    compressor_name = compressor_name.decode('utf-8')
    depth = struct.unpack('>H', sample_data[74:76])[0]
    pre_defined3 = struct.unpack('>h', sample_data[76:78])[0]

    atom_info['reserved1'] = reserved1
    atom_info['data_reference_index'] = data_reference_index
    atom_info['pre_defined1'] = pre_defined1
    atom_info['reserved2'] = reserved2
    atom_info['pre_defined2'] = pre_defined2
    atom_info['width'] = width
    atom_info['height'] = height
    atom_info['Horizresolution'] = Horizresolution
    atom_info['Vertiresolution'] = Vertiresolution
    atom_info['reserved3'] = reserved3
    atom_info['frame_count'] = frame_count
    atom_info['compressor_name'] = compressor_name
    atom_info['depth'] = depth
    atom_info['pre_defined3'] = pre_defined3


    hvcc_boxSize, hvccType = struct.unpack('>I4s', sample_data[78:86])
    hvccType = hvccType.decode('utf-8')
    hvc_info['type'] = hvccType
    hvc_info['size'] = hvcc_boxSize
    parse_hvcc(sample_data[86:], hvc_info)
    atom_info[hvc_info['type']] = hvc_info

hevc_nal_type_name = [
    "TRAIL_N", # HEVC_NAL_TRAIL_N
    "TRAIL_R", # HEVC_NAL_TRAIL_R
    "TSA_N", # HEVC_NAL_TSA_N
    "TSA_R", # HEVC_NAL_TSA_R
    "STSA_N", # HEVC_NAL_STSA_N
    "STSA_R", # HEVC_NAL_STSA_R
    "RADL_N", # HEVC_NAL_RADL_N
    "RADL_R", # HEVC_NAL_RADL_R
    "RASL_N", # HEVC_NAL_RASL_N
    "RASL_R", # HEVC_NAL_RASL_R
    "RSV_VCL_N10", # HEVC_NAL_VCL_N10
    "RSV_VCL_R11", # HEVC_NAL_VCL_R11
    "RSV_VCL_N12", # HEVC_NAL_VCL_N12
    "RSV_VLC_R13", # HEVC_NAL_VCL_R13
    "RSV_VCL_N14", # HEVC_NAL_VCL_N14
    "RSV_VCL_R15", # HEVC_NAL_VCL_R15
    "BLA_W_LP", # HEVC_NAL_BLA_W_LP
    "BLA_W_RADL", # HEVC_NAL_BLA_W_RADL
    "BLA_N_LP", # HEVC_NAL_BLA_N_LP
    "IDR_W_RADL", # HEVC_NAL_IDR_W_RADL
    "IDR_N_LP", # HEVC_NAL_IDR_N_LP
    "CRA_NUT", # HEVC_NAL_CRA_NUT
    "RSV_IRAP_VCL22", # HEVC_NAL_RSV_IRAP_VCL22
    "RSV_IRAP_VCL23", # HEVC_NAL_RSV_IRAP_VCL23
    "RSV_VCL24", # HEVC_NAL_RSV_VCL24
    "RSV_VCL25", # HEVC_NAL_RSV_VCL25
    "RSV_VCL26", # HEVC_NAL_RSV_VCL26
    "RSV_VCL27", # HEVC_NAL_RSV_VCL27
    "RSV_VCL28", # HEVC_NAL_RSV_VCL28
    "RSV_VCL29", # HEVC_NAL_RSV_VCL29
    "RSV_VCL30", # HEVC_NAL_RSV_VCL30
    "RSV_VCL31", # HEVC_NAL_RSV_VCL31
    "VPS", # HEVC_NAL_VPS
    "SPS", # HEVC_NAL_SPS
    "PPS", # HEVC_NAL_PPS
    "AUD", # HEVC_NAL_AUD
    "EOS_NUT", # HEVC_NAL_EOS_NUT
    "EOB_NUT", # HEVC_NAL_EOB_NUT
    "FD_NUT", # HEVC_NAL_FD_NUT
    "SEI_PREFIX", # HEVC_NAL_SEI_PREFIX
    "SEI_SUFFIX", # HEVC_NAL_SEI_SUFFIX
    "RSV_NVCL41", # HEVC_NAL_RSV_NVCL41
    "RSV_NVCL42", # HEVC_NAL_RSV_NVCL42
    "RSV_NVCL43", # HEVC_NAL_RSV_NVCL43
    "RSV_NVCL44", # HEVC_NAL_RSV_NVCL44
    "RSV_NVCL45", # HEVC_NAL_RSV_NVCL45
    "RSV_NVCL46", # HEVC_NAL_RSV_NVCL46
    "RSV_NVCL47", # HEVC_NAL_RSV_NVCL47
    "UNSPEC48", # HEVC_NAL_UNSPEC48
    "UNSPEC49", # HEVC_NAL_UNSPEC49
    "UNSPEC50", # HEVC_NAL_UNSPEC50
    "UNSPEC51", # HEVC_NAL_UNSPEC51
    "UNSPEC52", # HEVC_NAL_UNSPEC52
    "UNSPEC53", # HEVC_NAL_UNSPEC53
    "UNSPEC54", # HEVC_NAL_UNSPEC54
    "UNSPEC55", # HEVC_NAL_UNSPEC55
    "UNSPEC56", # HEVC_NAL_UNSPEC56
    "UNSPEC57", # HEVC_NAL_UNSPEC57
    "UNSPEC58", # HEVC_NAL_UNSPEC58
    "UNSPEC59", # HEVC_NAL_UNSPEC59
    "UNSPEC60", # HEVC_NAL_UNSPEC60
    "UNSPEC61", # HEVC_NAL_UNSPEC61
    "UNSPEC62", # HEVC_NAL_UNSPEC62
    "UNSPEC63", # HEVC_NAL_UNSPEC63
]

def parse_hvcc(hvcc_data, atom_info):
    configuration_version = struct.unpack('>B', hvcc_data[0:1])[0]
    bit = BitArray(uint=hvcc_data[1], length = 8).bin
    general_profile_space = int(bit[0:2],2)
    general_tier_flag = int(bit[2], 2)
    general_profile_idc = int(bit[3:8], 2)
    general_profile_compatibility_flags = struct.unpack('>I', hvcc_data[2:6])[0]
    general_constraint_indicator_flags = struct.unpack('>6B', hvcc_data[6:12])[0]
    general_level_idc = struct.unpack('>B', hvcc_data[12:13])[0]
    two_bytes = hvcc_data[13:15]
    two_bytes = int.from_bytes(two_bytes, byteorder='big')
    bit = BitArray(uint=two_bytes, length = 16).bin
    reserved_0 = int(bit[0:4], 2)
    min_spatial_segmentation_idc = int(bit[4:16], 2)
    bit = BitArray(uint=hvcc_data[15], length=8).bin
    reserved_1 = int(bit[0:6], 2)
    parallelismType = int(bit[6:8], 2)
    bit = BitArray(uint=hvcc_data[16], length=8).bin
    reserved_2 = int(bit[0:6], 2)
    chroma_format_idc = int(bit[6:8], 2)
    bit = BitArray(uint=hvcc_data[17], length=8).bin
    reserved_3 = int(bit[0:5], 2)
    bit_depth_luma_minus8 = int(bit[5:8], 2)
    bit = BitArray(uint=hvcc_data[18], length=8).bin
    reserved_4 = int(bit[0:5], 2)
    bit_depth_chroma_minus8 = int(bit[5:8], 2)
    avgFramRate = struct.unpack('>H', hvcc_data[19:21])[0]
    bit = BitArray(uint=hvcc_data[21], length=8).bin
    constantFrameRate = int(bit[0:2], 2)
    numTemporalLayers = int(bit[2:5], 2)
    temporalIdNested = int(bit[5], 2)
    lengthSizeMinusOne = int(bit[6:8], 2)
    numOfArrays = struct.unpack('>B', hvcc_data[22:23])[0]

    atom_info['configurationVersion'] = configuration_version
    atom_info['general_profile_space'] = general_profile_space
    atom_info['general_tier_flag'] = general_tier_flag
    atom_info['general_profile_idc'] = general_profile_idc
    atom_info['general_profile_compatibility_flags'] = general_profile_compatibility_flags
    atom_info['general_constraint_indicator_flags'] = general_constraint_indicator_flags
    atom_info['general_level_idc'] = general_level_idc
    atom_info['reserved_0'] = reserved_0
    atom_info['min_spatial_segmentation_idc'] = min_spatial_segmentation_idc
    atom_info['reserved_1'] = reserved_1
    atom_info['parallelismType'] = parallelismType
    atom_info['reserved_2'] = reserved_2
    atom_info['chroma_format_idc'] = chroma_format_idc
    atom_info['reserved_3'] = reserved_3
    atom_info['bit_depth_luma_minus8'] = bit_depth_luma_minus8
    atom_info['reserved_4'] = reserved_4
    atom_info['bit_depth_chroma_minus8'] = bit_depth_chroma_minus8
    atom_info['avgFrameRate'] = avgFramRate
    atom_info['constantFrameRate'] = constantFrameRate
    atom_info['numTemporalLayers'] = numTemporalLayers
    atom_info['temporalIdNested'] = temporalIdNested
    atom_info['lengthSizeMinusOne'] = lengthSizeMinusOne
    atom_info['numOfArrays'] = numOfArrays

    arrays_info = {}
    count=0
    i=0
    for i in range(numOfArrays):
        bit = BitArray(uint=hvcc_data[23+count], length=8).bin
        array_completeness = int(bit[0], 2)
        reserved = int(bit[1], 2)
        NAL_unit_type = int(bit[2:8], 2)
        name = hevc_nal_type_name[NAL_unit_type]
        numNalus = struct.unpack('>H', hvcc_data[24+count:26+count])[0]
        arrays_info[f'array_completeness_{i}'] = array_completeness
        arrays_info[f'reserved_{i}'] = reserved
        arrays_info[f'NAL_unit_type_{i}'] = NAL_unit_type
        for _ in range(numNalus):
            nalUnitLength = struct.unpack('>H', hvcc_data[26+count:28+count])[0]
            nalUnit =  hvcc_data[28+count:28+count+nalUnitLength]
            #nalUnit = bytes.hex(nalUnit)
            arrays_info[f'nalUnitLength_{i}'] = nalUnitLength
            arrays_info[f'{name}'] = nalUnit
            count = 5+nalUnitLength+count   # 5는 nalUnitType(1) + numNalus(2) + nalUnitLength(2)
        
    atom_info['nalUnits'] = arrays_info

def parse_colr(colr_data, atom_info):
    color_parameter_type = struct.unpack('>4s', colr_data[0:4])[0]
    color_parameter_type = color_parameter_type.decode('utf-8')
    primary_index = struct.unpack('>H', colr_data[4:6])[0]
    transferFunction_index = struct.unpack('>H', colr_data[6:8])[0]
    colorMatrix_index = struct.unpack('>H', colr_data[8:10])[0]

    atom_info['color_parameter_type'] = color_parameter_type
    atom_info['color_primaries'] = primary_index
    atom_info['transfer_characteristics'] = transferFunction_index
    atom_info['matrix_coefficient'] = colorMatrix_index