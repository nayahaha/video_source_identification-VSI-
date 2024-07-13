import struct

def get_ftyp_tag(video_file, AtomType, ftypAtomSize, atom_info):
    ftyp_data = video_file.read(ftypAtomSize - 8)

    
    major_brand, minor_version = struct.unpack('>4sI', ftyp_data[:8])
    major_brand = major_brand.decode('utf-8')
    minorBrands = []

    num_minor_brands = (len(ftyp_data) - 8) // 4
    minor_brands = [struct.unpack('>4s', ftyp_data[i:i+4])[0] for i in range(8, len(ftyp_data), 4)]

    Path = ''
    for brand in minor_brands:

        minorBrands = brand.decode('utf-8')
        Path += minorBrands + ' '
    atom_info['majorBrand'] = major_brand
    atom_info['minorVersion'] = minor_version
    atom_info['minorBrand'] = Path