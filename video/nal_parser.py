import os
import sys
import struct

from bitstring import BitStream

def remove_epb(nal_unit):
    removed_nal_unit = bytearray()

    i = 0
    while i < len(nal_unit):
        if i < len(nal_unit) - 2 and nal_unit[i] == 0x00 and nal_unit[i + 1] == 0x00 and nal_unit[i + 2] == 0x03:
            removed_nal_unit.append(nal_unit[i])
            removed_nal_unit.append(nal_unit[i + 1])
            i += 3
        else:
            removed_nal_unit.append(nal_unit[i])
            i += 1

    return bytes(removed_nal_unit)


def get_color_parameters(nal):
    if nal.vui.order["video_signal_type_present_flag"] == 0:
        nal.vui.order["video_full_range_flag"] = 0
        nal.vui.order["colour_primaries"] = 0
        nal.vui.order["transfer_characteristics"] = 0
        nal.vui.order["matrix_coefficients"] = 0
    if nal.vui.order["video_signal_type_present_flag"] == 1 and nal.vui.order["colour_description_present_flag"] == 0:
        nal.vui.order["colour_primaries"] = 0
        nal.vui.order["transfer_characteristics"] = 0
        nal.vui.order["matrix_coefficients"] = 0
class h264_HRD:
    def __init__(self,rbsp_bytes):
        self.s = rbsp_bytes
        self.order = {
            "cpb_cnt_minus1":None,
            "bit_rate_scale":None,
            "cpb_size_scale":None,
            "bit_rate_value_minus1":None,
            "cpb_size_value_minus1":None,
            "cbf_flag":None,
            "initial_cpb_removal_delay_length_minus1":None,
            "cpb_removal_delay_lenth_minus1":None,
            "dpb_output_delay_length_minus1":None,
            "time_offset_length":None
        }
        self.order["bit_rate_value_minus1"] = []
        self.order["cpb_size_value_minus1"] = []
        self.order["cbr_flag"] = []
        self.order["cpb_cnt_minus1"] = self.s.read("ue")
        self.order["bit_rate_scale"] = self.s.read("uint:4")
        self.order["cpb_size_scale"] = self.s.read("uint:4")
        SchedSeldx = 0
        self.order["bit_rate_value_minus1"] = [0] * (self.order["cpb_cnt_minus1"] + 1)
        self.order["cpb_size_value_minus1"] = [0] * (self.order["cpb_cnt_minus1"] + 1)
        self.order["cbr_flag"] = [0] * (self.order["cpb_cnt_minus1"] + 1)
        while SchedSeldx<=self.order["cpb_cnt_minus1"]:
            self.order[f"bit_rate_value_minus1[{SchedSeldx}]"] = self.s.read("ue")
            self.order[f"cpb_size_value_minus1[{SchedSeldx}]"] = self.s.read("ue")
            self.order[f"cbr_flag[{SchedSeldx}]"] = self.s.read("uint:1")
            SchedSeldx += 1
        self.order["initial_cpb_removal_delay_length_minus1"] = self.s.read("uint:5")
        self.order["cpb_removal_delay_length_minus1"] = self.s.read("uint:5")
        self.order["dpb_output_delay_length_minus1"] = self.s.read("uint:5")
        self.order["time_offset_length"] = self.s.read("uint:5")

class h264_VUI:
    def __init__(self, rbsp_bytes):
        self.s = rbsp_bytes
        self.order = {
            "aspect_ratio_info_present_flag":None,
            "aspect_ratio_idc":None,
            "sar_width":None,
            "sar_height":None,
            "overscan_info_present_flag":None,
            "overscan_appropriate_flag":None,
            "video_signal_type_present_flag":None,
            "video_format":None,
            "video_full_range_flag":None,
            "colour_description_present_flag":None,
            "colour_primaries":None,
            "transfer_characteristics":None,
            "matrix_coefficients":None,
            "chroma_loc_info_present_flag":None,
            "chroma_sample_loc_type_top_field":None,
            "chroma_sample_loc_type_bottom_field":None,
            "timing_info_present_flag":None,
            "num_units_in_tick":None,
            "time_scale":None,
            "fixed_frame_rate_flag":None,
            "nal_hrd_parameters_present_flag":None,
            "hrd":None,
            "cpb_cnt_minus1":None,
            "bit_rate_scale":None,
            "cpb_size_scale":None,
            "bit_rate_value_minus1":None,
            "cpb_size_value_minus1":None,
            "cbr_flag":None,
            "initial_cpb_removal_delay_length_minus1":None,
            "cpb_removal_delay_length_minus1":None,
            "dpb_output_delay_length_minus1":None,
            "time_offset_length":None,
            "vcl_hrd_parameters_present_flag":None,
            "low_delay_hrd_flag":None,
            "pic_struct_present_flag":None,
            "bitstream_restriction_flag":None,
            "motion_vectors_over_pic_boundaries_flag":None,
            "max_bytes_per_pic_denom":None,
            "max_bits_per_mb_denom":None,
            "log2_max_mv_length_horizontal":None,
            "log2_max_mv_length_vertical":None,
            "num_reorder_frames":None,
            "max_dec_frame_buffering":None
        }
        
        self.order["aspect_ratio_info_present_flag"] = self.s.read("uint:1")
        if self.order["aspect_ratio_info_present_flag"]:
            self.order["aspect_ratio_idc"] = self.s.read("uint:8")
            if self.order["aspect_ratio_idc"] == 255:
                self.order["sar_width"] = self.s.read("uint:16")
                self.order["sar_height"] = self.s.read("uint:16")
        self.order["overscan_info_present_flag"] = self.s.read("uint:1")
        if self.order["overscan_info_present_flag"]:
            self.order["overscan_appropriate_flag"] = self.s.read("uint:1")
        self.order["video_signal_type_present_flag"] = self.s.read("uint:1")
        if self.order["video_signal_type_present_flag"]:
            self.order["video_format"] = self.s.read("uint:3")
            self.order["video_full_range_flag"] = self.s.read("uint:1")
            self.order["colour_description_present_flag"] = self.s.read("uint:1")
            if self.order["colour_description_present_flag"]:
                self.order["colour_primaries"] = self.s.read("uint:8")
                self.order["transfer_characteristics"] = self.s.read("uint:8")
                self.order["matrix_coefficients"] = self.s.read("uint:8")
        self.order["chroma_loc_info_present_flag"] = self.s.read("uint:1")
        if self.order["chroma_loc_info_present_flag"]:
            self.order["chroma_sample_loc_type_top_field"] = self.s.read("ue")
            self.order["chroma_sample_loc_type_bottom_field"] = self.s.read("ue")
        self.order["timing_info_present_flag"] = self.s.read("uint:1")
        if self.order["timing_info_present_flag"]:
            self.order["num_units_in_tick"] = self.s.read("uint:32")
            self.order["time_scale"] = self.s.read("uint:32")
            self.order["fixed_frame_rate_flag"] = self.s.read("uint:1")
        self.order["nal_hrd_parameters_present_flag"] = self.s.read("uint:1")
        if self.order["nal_hrd_parameters_present_flag"]:
            self.order["hrd"] = h264_HRD(self.s)
        self.order["vcl_hrd_parameters_present_flag"] = self.s.read("uint:1")
        if self.order["vcl_hrd_parameters_present_flag"]:
            self.order['hrd'] = h264_HRD(self.s)
        if self.order["nal_hrd_parameters_present_flag"] or self.order["vcl_hrd_parameters_present_flag"]:
            self.order["low_delay_hrd_flag"] = self.s.read("uint:1")
        self.order["pic_struct_present_flag"] = self.s.read("uint:1")
        self.order["bitstream_restriction_flag"] = self.s.read("uint:1")
        if self.order["bitstream_restriction_flag"]:
            self.order["motion_vectors_over_pic_boundaries_flag"] = self.s.read("uint:1")
            self.order["max_bytes_per_pic_denom"] = self.s.read("ue")
            self.order["max_bits_per_mb_denom"] = self.s.read("ue")
            self.order["log2_max_mv_length_horizontal"] = self.s.read("ue")
            self.order["log2_max_mv_length_vertical"] = self.s.read("ue")
            self.order["num_reorder_frames"] = self.s.read("ue")
            self.order["max_dec_frame_buffering"] = self.s.read("ue")

class h264_SPS:
    """
    Sequence Parameter Set class
    """

    def __init__(self, rbsp_bytes):
        self.s = rbsp_bytes
        self.order = {
            "forbidden_zero_bit":None,
            "nal_ref_idc":None,
            "nal_unit_type":None,
            "profile_idc":None,
            "constraint_set0_flag":None,
            "constraint_set1_flag":None,
            "constraint_set2_flag":None,
            "constraint_set3_flag":None,
            "constraint_set4_flag":None,
            "constraint_set5_flag":None,
            "reserved_zero_2bits":None,
            "level_idc":None,
            "seq_parameter_set_id":None,
            "chroma_format_idc":None,
            "separate_colour_plane_flag":None,
            "bit_depth_luma_minus8":None,
            "bit_depth_chroma_minus8":None,
            "qpprime_y_zero_transform_bypass_flag":None,
            "seq_scaling_matrix_present_flag":None,
            "delta_scale":None,
            "log2_max_frame_num_minus4":None,
            "pic_order_cnt_type":None,
            "log2_max_pic_order_cnt_lsb_minus4":None,
            "delta_pic_order_always_zero_flag":None,
            "offset_for_non_ref_pic":None,
            "offset_for_top_to_bottom_filed":None,
            "num_ref_frames_in_pic_order_cnt_cycle":None,
            "offset_for_ref_frame":None,
            "num_ref_frames":None,
            "gaps_in_frame_num_value_allowed_flag":None,
            "pic_width_in_mbs_minus_1":None,
            "pic_height_in_map_units_minus_1":None,
            "frame_mbs_only_flag":None,
            "mb_adaptive_frame_field_flag":None,
            "direct_8x8_inference_flag":None,
            "frame_cropping_flag":None,
            "frame_crop_left_offset":None,
            "frame_crop_right_offset":None,
            "frame_crop_top_offset":None,
            "frame_crop_bottom_offset":None,
            "vui_parameters_present_flag":None,
            "scalingList4x4":None,
            "useDefaultScalingMatrix4x4Flag":None,
            "scalingList8x8":None,
            "useDefaultScalingMatrix8x8Flag":None
        }
        #super(SPS, self).__init__(rbsp_bytes, verbose, order)

        # initializers
        self.order["offset_for_ref_frame"] = []
        self.order["seq_scaling_list_present_flag"] = []
        self.order["scalingList4x4"] = [0] * 16
        self.order["useDefaultScalingMatrix4x4Flag"] = [0] * 16
        self.order["scalingList8x8"] = [0] * 64
        self.order["useDefaultScalingMatrix8x8Flag"] = [0] * 64
        self.order["delta_scale"] = []


        self.order["forbidden_zero_bit"] = self.s.read("uint:1")
        self.order["nal_ref_idc"] = self.s.read("uint:2")
        self.order["nal_unit_type"] = self.s.read("uint:5")
        self.order["profile_idc"] = self.s.read("uint:8")
        self.order["constraint_set0_flag"] = self.s.read("uint:1")
        self.order["constraint_set1_flag"] = self.s.read("uint:1")
        self.order["constraint_set2_flag"] = self.s.read("uint:1")
        self.order["constraint_set3_flag"] = self.s.read("uint:1")
        self.order["constraint_set4_flag"] = self.s.read("uint:1")
        self.order["constraint_set5_flag"] = self.s.read("uint:1")
        self.order["reserved_zero_2bits"] = self.s.read("uint:2")
        self.order["level_idc"] = self.s.read("uint:8")
        self.order["seq_parameter_set_id"] = self.s.read("ue")

        if self.order["profile_idc"] in [
            100,
            110,
            122,
            244,
            44,
            83,
            86,
            118,
            128,
            138,
            139,
            134,
            135,
        ]:
            self.order["chroma_format_idc"] = self.s.read("ue")
            if self.order["chroma_format_idc"] == 3:
                self.order["separate_colour_plane_flag"] = self.s.read("uint:1")

            self.order["bit_depth_luma_minus8"] = self.s.read("ue")
            self.order["bit_depth_chroma_minus8"] = self.s.read("ue")
            self.order["qpprime_y_zero_transform_bypass_flag"] = self.s.read("uint:1")
            self.order["seq_scaling_matrix_present_flag"] = self.s.read("uint:1")

            if self.order["seq_scaling_matrix_present_flag"]:
                if self.order["chroma_format_idc"] != 3:
                    num_scaling_lists = 8
                else:
                    num_scaling_lists = 12

                self.order["seq_scaling_list_present_flag"] = []
                for i in range(num_scaling_lists):
                    self.order["seq_scaling_list_present_flag"].append(self.s.read("uint:1"))
                    if self.order[f"seq_scaling_list_present_flag"][i]:
                        if i < 6:
                            self.read_scaling_list(self.s, self.order["scalingList4x4"], 16, self.order["useDefaultScalingMatrix4x4Flag"])
                        else:
                            self.read_scaling_list(self.s, self.order["scalingList8x8"], 64, self.order["useDefaultScalingMatrix8x8Flag"])

        self.order["log2_max_frame_num_minus4"] = self.s.read("ue")
        self.order["pic_order_cnt_type"] = self.s.read("ue")

        if self.order["pic_order_cnt_type"] == 0:
            self.order["log2_max_pic_order_cnt_lsb_minus4"] = self.s.read("ue")
        elif self.order["pic_order_cnt_type"] == 1:
            self.order["delta_pic_order_always_zero_flag"] = self.s.read("uint:1")
            self.order["offset_for_non_ref_pic"] = self.s.read("se")
            self.order["offset_for_top_to_bottom_filed"] = self.s.read("se")
            self.order["num_ref_frames_in_pic_order_cnt_cycle"] = self.s.read("ue")
            for i in range(self.order["num_ref_frames_in_pic_order_cnt_cycle"]):
                self.order["offset_for_ref_frame"].append(self.s.read("se"))

        self.order["num_ref_frames"] = self.s.read("ue")
        self.order["gaps_in_frame_num_value_allowed_flag"] = self.s.read("uint:1")
        self.order["pic_width_in_mbs_minus_1"] = self.s.read("ue")
        self.order["pic_height_in_map_units_minus_1"] = self.s.read("ue")
        self.order["frame_mbs_only_flag"] = self.s.read("uint:1")
        if not self.order["frame_mbs_only_flag"]:
            self.order["mb_adaptive_frame_field_flag"] = self.s.read("uint:1")
        self.order["direct_8x8_inference_flag"] = self.s.read("uint:1")
        self.order["frame_cropping_flag"] = self.s.read("uint:1")
        if self.order["frame_cropping_flag"]:
            self.order["frame_crop_left_offset"] = self.s.read("ue")
            self.order["frame_crop_right_offset"] = self.s.read("ue")
            self.order["frame_crop_top_offset"] = self.s.read("ue")
            self.order["frame_crop_bottom_offset"] = self.s.read("ue")
        self.order["vui_parameters_present_flag"] = self.s.read("uint:1")
        if self.order["vui_parameters_present_flag"]:
            self.vui = h264_VUI(self.s)
            
            get_color_parameters(self)
            

    def get_formatProfile(self):
        temp = self.order["level_idc"] * 0.1
        level_idc = round(temp,2)

        if self.order["profile_idc"] == 66 and self.order["constraint_set1_flag"] == 0:
            profile = f'Baseline L{level_idc}'
        elif self.order["profile_idc"] == 66 and self.order["constraint_set1_flag"] == 1:
            profile = f'Constrained Baseline L{level_idc}'
        elif self.order["profile_idc"] == 77:
            profile = f'Main L{level_idc}'
        elif self.order["profile_idc"] == 88:
            profile = f'Extended L{level_idc}'
        elif self.order["profile_idc"] == 100:
            profile = f'High L{level_idc}'
        return profile
    
    def read_scaling_list(self, raw, scalingList, sizeOfScalingList, useDefaultScalingMatrixFlag):
        lastScale = 8
        nextScale = 8
        self.order["delta_scale"] = [0] * sizeOfScalingList
        for j in range(sizeOfScalingList):
            if nextScale != 0:
                self.order[f"delta_scale[{j}]"] = raw.read("se")
                nextScale = (lastScale + self.order[f"delta_scale[{j}]"] + 256) % 256
                useDefaultScalingMatrixFlag = (j==0 and nextScale == 0)
            
            if nextScale == 0:
                scalingList[j] = lastScale
            else:
                scalingList[j] = nextScale
            lastScale = scalingList[j]
            j += 1

class h264_PPS:
    def __init__(self, rbsp_bytes):
        self.s = rbsp_bytes
        self.order = {
            "forbidden_zero_bit":None,
            "nal_ref_idc":None,
            "nal_unit_type":None,
            "pic_parameter_set_id":None,
            "seq_parameter_set_id":None,
            "entropy_coding_mode_flag":None,
            "pic_order_present_flag":None,
            "num_slice_groups_minus1":None,
            "slice_group_map_type":None,
            "run_length_minus1":None,
            "top_left":None,
            "bottom_right":None,
            "slice_group_change_direction_flag":None,
            "slice_group_change_rate_minus1":None,
            "pic_size_in_map_units_minus1":None,
            "slice_group_id":None,
            "num_ref_idx_l0_active_minus1":None,
            "num_ref_idx_l1_active_minus1":None,
            "weighted_pred_flag":None,
            "weighted_bipred_idc":None,
            "pic_init_qp_minus26":None,
            "pic_init_qs_minus26":None,
            "chroma_qp_index_offset":None,
            "deblocking_filter_control_present_flag":None,
            "constrained_intra_pred_flag":None,
            "redundant_pic_cnt_present_flag":None
        }
        #super(PPS, self).__init__(rbsp_bytes, verbose, order)

        self.order["forbidden_zero_bit"] = self.s.read("uint:1")
        self.order["nal_ref_idc"] = self.s.read("uint:2")
        self.order["nal_unit_type"] = self.s.read("uint:5")
        self.order["pic_parameter_set_id"] = self.s.read("ue")
        self.order["seq_parameter_set_id"] = self.s.read("ue")
        self.order["entropy_coding_mode_flag"] = self.s.read("uint:1")
        self.order['pic_order_present_flag'] = self.s.read("uint:1")
        self.order["num_slice_groups_minus1"] = self.s.read("ue")
        if self.order["num_slice_groups_minus1"] > 0:
            self.order["slice_group_map_type"] = self.s.read("ue")
            if self.order["slice_group_map_type"] == 0:
                self.order["run_length_minus1"] = []
                for i_group in range(self.order["num_slice_groups_minus1"] + 1):
                    self.order["run_length_minus1"].append(self.s.read("ue"))
            elif self.order["slice_group_map_type"] == 2:
                self.order["top_left"] = []
                self.order["bottom_right"] = []
                for i_group in range(self.order["num_slice_groups_minus1"] + 1):
                    self.order["top_left"].append(self.s.read("ue"))
                    self.order["bottom_right"].append(self.s.read("ue"))
            elif self.order["slice_group_map_type"] in [3, 4, 5]:
                self.order["slice_group_change_direction_flag"] = self.s.read("uint:1")
                self.order["slice_group_change_rate_minus1"] = self.s.read("ue")
            elif self.order["slice_group_map_type"] == 6:
                self.order["pic_size_in_map_units_minus1"] = self.s.read("ue")
                self.order["slice_group_id"] = []
                for i in range(self.order["pic_size_in_map_units_minus1"] + 1):
                    self.order["slice_group_id"].append(self.s.read("uint:1"))

        self.order["num_ref_idx_l0_active_minus1"] = self.s.read("ue")
        self.order["num_ref_idx_l1_active_minus1"] = self.s.read("ue")
        self.order["weighted_pred_flag"] = self.s.read("uint:1")
        self.order["weighted_bipred_idc"] = self.s.read("uint:2")
        self.order["pic_init_qp_minus26"] = self.s.read("se")
        self.order["pic_init_qs_minus26"] = self.s.read("se")
        self.order["chroma_qp_index_offset"] = self.s.read("se")
        self.order["deblocking_filter_control_present_flag"] = self.s.read("uint:1")
        self.order["constrained_intra_pred_flag"] = self.s.read("uint:1")
        self.order["redundant_pic_cnt_present_flag"] = self.s.read("uint:1")
        while self.s.pos < self.s.len:
            self.order["transform_8x8_mode_flag"] = self.s.read("uint:1")
            self.order["pic_scaling_matrix_present_flag"] = self.s.read("uint:1")
                    
class h265_HRD:
    def __init__(self, rbsp_bytes, commonInfPresentFlag, maxNumSubLayersMinus1):
        self.s = rbsp_bytes
        self.order = {
            "nal_hrd_parameters_present_flag":None,
            "vcl_hrd_parameters_present_flag":None,
            "sub_pic_hrd_params_present_flag":None,
            "tick_divisor_minus2":None,
            "du_cpb_removal_delay_increment_length_minus1":None,
            "sub_pic_cpb_params_in_pic_timing_sei_flag":None,
            "dpb_output_delay_du_length_minus1":None,
            "bit_rate_scale":None,
            "cpb_size_scale":None,
            "cpb_size_du_scale":None,
            "initial_cpb_removal_delay_length_minus1":None,
            "au_cpb_removal_delay_length_minus1":None,
            "dpb_output_delay_length_minus1":None,
            "fixed_pic_rate_general_flag":None,
            'fixed_pic_rate_within_cvs_flag':None,
            "elemental_duration_in_tc_minus1":None,
            "low_delay_hrd_flag":None,
            "cpb_cnt_minus1":None,
            "bit_rate_value_minus1":None,
            "cpb_size_value_minus1":None,
            "cpb_size_du_value_minus1":None,
            "bit_rate_du_value_minus1":None,
            "cbr_flag":None
        }

        self.order["fixed_pic_rate_general_flag"] = []
        self.order["fixed_pic_rate_within_cvs_flag"] = []
        self.order["elemental_duration_in_tc_minus1"] = []
        self.order["low_delay_hrd_flag"] = []
        self.order["cpb_cnt_minus1"] = []

        if commonInfPresentFlag:
            self.order["nal_hrd_parameters_present_flag"] = self.s.read("uint:1")
            self.order["vcl_hrd_parameters_present_flag"] = self.s.read("uint:1")
            if self.order["nal_hrd_parameters_present_flag"] or self.order["vcl_hrd_parameters_present_flag"]:
                self.order["sub_pic_hrd_params_present_flag"] = self.s.read("uint:1")
                if self.order["sub_pic_hrd_params_present_flag"]:
                    self.order["tick_divisor_minus2"] = self.s.read("uint:8")
                    self.order["du_cpb_removal_delay_increment_length_minus1"] = self.s.read("uint:5")
                    self.order["sub_pic_cpb_params_in_pic_timing_sei_flag"] = self.s.read("uint:1")
                    self.order["dpb_output_delay_du_length_minus1"] = self.s.read("uint:5")
                self.order["bit_rate_scale"] = self.s.read("uint:4")
                self.order["cpb_size_scale"] = self.s.read("uint:4")
                if self.order["sub_pic_hrd_params_present_flag"]:
                    self.order["cpb_size_du_scale"] = self.s.read("uint:4")
                self.order["initial_cpb_removal_delay_length_minus1"] = self.s.read("uint:5")
                self.order["au_cpb_removal_delay_length_minus1"] = self.s.read("uint:5")
                self.order["dpb_output_delay_length_minus1"] = self.s.read("uint:5")
        for i in range(maxNumSubLayersMinus1):
            self.order["fixed_pic_rate_general_flag"].append(self.s.read("uint:1"))
            if self.order[f"fixed_pic_rate_general_flag[{i}]"] == 0:
                self.order["fixed_pic_rate_within_cvs_flag"].append(self.s.read("uint:1"))
            if self.order[f"fixed_pic_rate_within_cvs_flag[{i}]"]:
                self.order["elemental_duration_in_tc_minus1"].append("ue")
            else:
                self.order["low_delay_hrd_flag"].append(self.s.read("uint:1"))
            if self.order["low_delay_hrd_flag"] == 0:
                self.order["cpb_cnt_minus1"].append(self.s.read("ue"))
            if self.order["nal_hrd_parameters_present_flag"]:
                self.sub_layer_hrd_parameters(i)
            if self.order["vcl_hrd_parameters_present_flag"]:
                self.sub_layer_hrd_parameters(i)

    def sub_layer_hrd_parameters(self, subLayerId):
        self.order["bit_rate_value_minus1"] = []
        self.order["cpb_size_value_minus1"] = []
        self.order["cpb_size_du_value_minus1"] = []
        self.order["bit_rate_du_value_minus1"] = []
        self.order["cbr_flag"] = []

        CpbCnt = self.order[f"cpb_cnt_minus1[{subLayerId}]"] + 1
        for i in range(CpbCnt):
            self.order["bit_rate_value_minus1"].append(self.s.read("ue"))
            self.order["cpb_size_value_minus1"].append(self.s.read("ue"))
            if self.order["sub_pic_hrd_params_present_flag"]:
                self.order["cpb_size_du_value_minus1"].append(self.s.read("ue"))
                self.order["bit_rate_du_value_minus1"].append(self.s.read("ue"))
            self.order["cbr_flag"].append(self.s.read("uint:1"))

class h265_VUI:
    def __init__(self, rbsp_bytes, sps_max_sub_layers_minus1):
        self.s = rbsp_bytes
        self.order = {
            "aspect_ratio_info_present_flag":None,
            "aspect_ratio_idc":None,
            "sar_width":None,
            "sar_height":None,
            "overscan_info_present_flag":None,
            "overscan_appropriate_flag":None,
            "video_signal_type_present_flag":None,
            "video_format":None,
            "video_full_range_flag":None,
            "colour_description_present_flag":None,
            "colour_primaries":None,
            "transfer_characteristics":None,
            "matrix_coefficients":None,
            "chroma_loc_info_present_flag":None,
            "chroma_sample_loc_type_top_field":None,
            "chroma_sample_loc_type_bottom_field":None,
            "neutral_chroma_indication_flag":None,
            "field_seq_flag":None,
            "frame_field_info_present_flag":None,
            "default_display_window_flag":None,
            "def_disp_win_left_offset":None,
            "def_disp_win_right_offset":None,
            "def_disp_win_top_offset":None,
            "def_disp_win_bottom_offset":None,
            "vui_timing_info_present_flag":None,
            "vui_num_units_in_tick":None,
            "vui_time_scale":None,
            "vui_poc_proportional_to_timing_flag":None,
            "vui_num_ticks_poc_diff_one_minus1":None,
            "vui_hrd_parameters_present_flag":None,
            "bitstream_restriction_flag":None,
            "tiles_fixed_structure_flag":None,
            "motion_vectors_over_pic_boundaries_flag":None,
            "restricted_ref_pic_lists_flag":None,
            "min_spatial_segmentation_idc":None,
            "max_bytes_per_pic_denom":None,
            "max_bits_per_min_cu_denom":None,
            "log2_max_mv_length_horizontal":None,
            "log2_max_mv_length_vertical":None
        }

        self.order["aspect_ratio_info_present_flag"] = self.s.read("uint:1")
        if self.order["aspect_ratio_info_present_flag"]:
            self.order["aspect_ratio_idc"] = self.s.read("uint:8")
            if self.order["aspect_ratio_idc"] == 255:
                self.order["sar_width"] = self.s.read("uint:16")
                self.order["sar_height"] = self.s.read("uint:16")
        self.order["overscan_info_present_flag"] = self.s.read("uint:1")
        if self.order["overscan_info_present_flag"]:
            self.order["overscan_appropriate_flag"] = self.s.read("uint:1")
        self.order["video_signal_type_present_flag"] = self.s.read("uint:1")
        if self.order["video_signal_type_present_flag"]:
            self.order["video_format"] = self.s.read("uint:3")
            self.order["video_full_range_flag"] = self.s.read("uint:1")
            self.order["colour_description_present_flag"] = self.s.read("uint:1")
            if self.order["colour_description_present_flag"]:
                self.order["colour_primaries"] = self.s.read("uint:8")
                self.order["transfer_characteristics"] = self.s.read("uint:8")
                self.order["matrix_coefficients"] = self.s.read("uint:8")
        self.order["chroma_loc_info_present_flag"] = self.s.read("uint:1")
        if self.order["chroma_loc_info_present_flag"]:
            self.order["chroma_sample_loc_type_top_field"] = self.s.read("ue")
            self.order["chroma_sample_loc_type_bottom_field"] = self.s.read("ue")
        self.order["neutral_chroma_indication_flag"] = self.s.read("uint:1")
        self.order["field_seq_flag"] = self.s.read("uint:1")
        self.order["frame_field_info_present_flag"] = self.s.read("uint:1")
        self.order["default_display_window_flag"] = self.s.read("uint:1")
        if self.order["default_display_window_flag"]:
            self.order["def_disp_win_left_offset"] = self.s.read("ue")
            self.order["def_disp_win_right_offset"] = self.s.read("ue")
            self.order["def_disp_win_top_offset"] = self.s.read("ue")
            self.order["def_disp_win_bottom_offset"] = self.s.read("ue")
        self.order["vui_timing_info_present_flag"] = self.s.read("uint:1")
        if self.order["vui_timing_info_present_flag"]:
            self.order["vui_num_units_in_tick"] = self.s.read("uint:32")
            self.order["vui_time_scale"] = self.s.read("uint:32")
            self.order["vui_poc_proportional_to_timing_flag"] = self.s.read("uint:1")
            if self.order["vui_poc_proportional_to_timing_flag"]:
                self.order["vui_num_ticks_poc_diff_one_minus1"] = self.s.read("ue")
            self.order["vui_hrd_parameters_present_flag"] = self.s.read("uint:1")
            if self.order["vui_hrd_parameters_present_flag"]:
                self.hrd = h265_HRD(self.s, 1, sps_max_sub_layers_minus1)
        self.order["bitstream_restriction_flag"] = self.s.read("uint:1")
        if self.order["bitstream_restriction_flag"]:
            self.order["tiles_fixed_structure_flag"] = self.s.read("uint:1")
            self.order["motion_vectors_over_pic_boundaries_flag"] = self.s.read("uint:1")
            self.order["restricted_ref_pic_lists_flag"] = self.s.read("uint:1")
            self.order["min_spatial_segmentation_idc"] = self.s.read("ue")
            self.order["max_bytes_per_pic_denom"] = self.s.read("ue")
            self.order["max_bits_per_min_cu_denom"] = self.s.read("ue")
            self.order["log2_max_mv_length_horizontal"] = self.s.read("ue")
            self.order["log2_max_mv_length_vertical"] = self.s.read("ue")

def profile_tier_level(nal, profilePresentFlag, maxNumSubLayersMinus1):
    nal.order["general_profile_compatibility_flag"] = []
    nal.order["sub_layer_profile_present_flag"] = []
    nal.order["sub_layer_level_present_flag"] = []
    nal.order["reserved_zero_2bits"] = []
    nal.order["sub_layer_profile_space"] = []
    nal.order["sub_layer_tier_flag"] = []
    nal.order["sub_layer_profile_idc"] = []
    nal.order["sub_layer_profile_compatibility_flag"] = [[]]
    nal.order["sub_layer_progressive_source_flag"] = []
    nal.order["sub_layer_interlaced_source_flag"] = []
    nal.order["sub_layer_non_packed_constraint_flag"] = []
    nal.order["sub_layer_frame_only_constraint_flag"] = []
    nal.order["sub_layer_max_12bit_constraint_flag"] = []
    nal.order["sub_layer_max_10bit_constraint_flag"] = []
    nal.order["sub_layer_max_8bit_constraint_flag"] = []
    nal.order["sub_layer_max_422chroma_constraint_flag"] = []
    nal.order["sub_layer_max_420chroma_constraint_flag"] = []
    nal.order["sub_layer_max_monochrome_constraint_flag"] = []
    nal.order["sub_layer_intra_constraint_flag"] = []
    nal.order["sub_layer_one_picture_only_constraint_flag_1"] = []
    nal.order["sub_layer_one_picture_only_constraint_flag_2"] = []
    nal.order["sub_layer_lower_bit_rate_constraint_flag"] = []
    nal.order["sub_layer_max_14bit_constraint_flag"] = []
    nal.order["sub_layer_reserved_zero_33bits"] = []
    nal.order["sub_layer_reserved_zero_34bits"] = []
    nal.order["sub_layer_reserved_zero_7bits"] = []
    nal.order["sub_layer_reserved_zero_35bits"] = []
    nal.order["sub_layer_reserved_zero_43bits"] = []
    nal.order["sub_layer_inbld_flag"] = []
    nal.order["sub_layer_reserved_zero_bit"] = []
    nal.order["sub_layer_level_idc"] = []

    if profilePresentFlag:
        nal.order["general_profile_space"] = nal.s.read("uint:2")
        nal.order["general_tier_flag"] = nal.s.read("uint:1")
        nal.order["general_profile_idc"] = nal.s.read("uint:5")
        for i in range(0, 32):
            nal.order["general_profile_compatibility_flag"].append(nal.s.read("uint:1"))

        nal.order["general_progressive_source_flag"] = nal.s.read("uint:1")
        nal.order["general_interlaced_source_flag"] = nal.s.read("uint:1")
        nal.order["general_non_packed_constraint_flag"] = nal.s.read("uint:1")
        nal.order["general_frame_only_constraint_flag"] = nal.s.read("uint:1")
        
        if nal.order["general_profile_idc"] in range(4,12) or any(nal.order[f"general_profile_compatibility_flag"][i] == 1 for i in range(4, 12)):
            nal.order["general_max_12bit_constraint_flag"] = nal.s.read("uint:1")
            nal.order["general_max_10bit_constraint_flag"] = nal.s.read("uint:1")
            nal.order["general_max_8bit_constraint_flag"] = nal.s.read("uint:1")
            nal.order["general_max_422chroma_constraint_flag"] = nal.s.read("uint:1")
            nal.order["general_max_420chroma_constraint_flag"] = nal.s.read("uint:1")
            nal.order["general_max_monochrome_constraint_flag"] = nal.s.read("uint:1")
            nal.order["general_intra_constraint_flag"] = nal.s.read("uint:1")
            nal.order["general_one_picture_only_constraint_flag_1"] = nal.s.read("uint:1")
            nal.order["general_lower_bit_rate_constraint_flag"] = nal.s.read("uint:1")
            if nal.order["general_profile_idc"] in [5,9,10,11] or any(nal.order[f"general_profile_compatibility_flag[{i}]"] == 1 for i in [5,9,10,11]):
                nal.order["general_max_14bit_constraint_flag"] = nal.s.read("uint:1")
                nal.order["general_reserved_zero_33bits"] = nal.s.read("uint:33")
            else:
                nal.order["general_reserved_zero_34bits"] = nal.s.read("uint:34")
        elif nal.order["general_profile_idc"] == 2 or nal.order["general_profile_compatibility_flag"][2]:
            nal.order["general_reserved_zero_7bits"] = nal.s.read("uint:7")
            nal.order["general_one_picture_only_constraint_flag_2"] = nal.s.read("uint:1")
            nal.order["general_reserved_zero_35bits"] = nal.s.read("uint:35")
        else:
            nal.order["general_reserved_zero_43bits"] = nal.s.read("uint:43")
        
        if nal.order["general_profile_idc"] in [1,2,3,4,5,9,11] or any(nal.order[f"general_profile_compatibility_flag[{i}]"] == 1 for i in [1,2,3,4,5,9,11]):
            nal.order["general_inbld_flag"] = nal.s.read("uint:1")
        else:
            nal.order["general_reserved_zero_bit"] = nal.s.read("uint:1")
    
    nal.order["general_level_idc"] = nal.s.read("uint:8")
    for i in range(0, maxNumSubLayersMinus1):
        nal.order["sub_layer_profile_present_flag"].append(nal.s.read("uint:1"))
        nal.order["sub_layer_level_present_flag"].append(nal.s.read("uint:1"))
    
    if maxNumSubLayersMinus1 > 0:
        for i in range(maxNumSubLayersMinus1, 8):
            nal.order["reserved_zero_2bits"].append(nal.s.read("uint:2"))
    rows = maxNumSubLayersMinus1
    cols = 32
    nal.order["sub_layer_profile_compatibility_flag"] = [[] for _ in range(rows)]
    for row in nal.order["sub_layer_profile_compatibility_flag"]:
        row.extend([0] * cols)
    for i in range(0, maxNumSubLayersMinus1):
        if nal.order["sub_layer_profile_present_flag"][i]:
            nal.order["sub_layer_profile_space"].append(nal.s.read("uint:2"))
            nal.order["sub_layer_tier_flag"].append(nal.s.read("uint:1"))
            nal.order["sub_layer_profile_idc"].append(nal.s.read("uint:5"))
            for j in range(0,32):
                nal.order["sub_layer_profile_compatibility_flag"][i][j] = nal.s.read("uint:1") ##
            nal.order["sub_layer_progressive_source_flag"].append(nal.s.read("uint:1"))
            nal.order["sub_layer_interlaced_source_flag"].append(nal.s.read("uint:1"))
            nal.order["sub_layer_non_packed_constraint_flag"].append(nal.s.read("uint:1"))
            nal.order["sub_layer_frame_only_constraint_flag"].append(nal.s.read("uint:1"))
            if nal.order["sub_layer_profile_idc"][i] in range(4,12) or any(nal.order[f"sub_layer_profile_compatibility_flag[{i}][{j}]"] == 1 for j in range(4,12)):
                nal.order["sub_layer_max_12bit_constraint_flag"].append(nal.s.read("uint:1"))
                nal.order["sub_layer_max_10bit_constraint_flag"].append(nal.s.read("uint:1"))
                nal.order["sub_layer_max_8bit_constraint_flag"].append(nal.s.read("uint:1"))
                nal.order["sub_layer_max_422chroma_constraint_flag"].append(nal.s.read("uint:1"))
                nal.order["sub_layer_max_420chroma_constraint_flag"].append(nal.s.read("uint:1"))
                nal.order["sub_layer_max_monochrome_constraint_flag"].append(nal.s.read("uint:1"))
                nal.order["sub_layer_intra_constraint_flag"].append(nal.s.read("uint:1"))
                nal.order["sub_layer_one_picture_only_constraint_flag_1"].append(nal.s.read("uint:1"))
                nal.order["sub_layer_lower_bit_rate_constraint_flag"].append(nal.s.read("uint:1"))
                if nal.order["sub_layer_profile_idc"][i] in [5,9,10,11] or any(nal.order[f"sub_layer_profile_compatibility_flag[{i}][{j}]"] == 1 for j in [5,9,10,11]):
                    nal.order["sub_layer_max_14bit_constraint_flag"].append(nal.s.read("uint:1"))
                    nal.order["sub_layer_reserved_zero_33bits"].append(nal.s.read("uint:33"))
                else:
                    nal.order["sub_layer_reserved_zero_34bits"].append(nal.s.read("uint:34"))
            elif nal.order["sub_layer_profile_idc"][i] == 2 or nal.order["sub_layer_profile_compatibility_flag"][i][2]:
                nal.order["sub_layer_reserved_zero_7bits"].append(nal.s.read("uint:7"))
                nal.order["sub_layer_one_picture_only_constraint_flag_2"] = nal.s.read("uint:1")
                nal.order["sub_layer_reserved_zero_35bits"] = nal.s.read("uint:35")
            else:
                nal.order["sub_layer_reserved_zero_43bits"].append(nal.s.read("uint:43"))
            
            if nal.order["sub_layer_profile_idc"][i] in [1,2,3,4,5,9,11] or any(nal.order[f"sub_layer_profile_compatibility_flag[{i}][{j}]"] == 1 for j in [1,2,3,4,5,9,11]):
                nal.order["sub_layer_inbld_flag"].append(nal.s.read("uint:1"))
            else:
                nal.order["sub_layer_reserved_zero_bit"].append(nal.s.read("uint:1"))
        
        if nal.order["sub_layer_level_present_flag"][i]:
            nal.order["sub_layer_level_idc"].append(nal.s.read("uint:8"))


class h265_VPS:
    def __init__(self, rbsp_bytes):
        self.s = rbsp_bytes
        self.order = {
            "forbidden_zero_bit":None,
            "nal_unit_type":None,
            "nuh_layer_id":None,
            "nuh_temporal_id_plus1":None,
            "vps_video_parameter_set_id":None,
            "vps_base_layer_internal_flag":None,
            "vps_base_layer_available_flag":None,
            "vps_max_layers_minus1":None,
            "vps_max_sub_layers_minus1":None,
            "vps_temporalid_nesting_flag":None,
            "vps_reserved_0xffff_16bits":None,

            "general_profile_space":None,
            "general_tier_flag":None,
            "general_profile_idc":None,
            "general_profile_compatibility_flag":None,
            "general_progressive_source_flag":None,
            "general_interlaced_source_flag":None,
            "general_non_packed_constraint_flag":None,
            "general_frame_only_constraint_flag":None,
            "general_max_12bit_constraint_flag":None,
            "general_max_10bit_constraint_flag":None,
            "general_max_8bit_constraint_flag":None,
            "general_max_422chroma_constraint_flag":None,
            "general_max_420chroma_constraint_flag":None,
            "general_max_monochrome_constraint_flag":None,
            "general_intra_constraint_flag":None,
            "general_one_picture_only_constraint_flag_1":None,
            "general_lower_bit_rate_constraint_flag":None,
            "general_max_14bit_constraint_flag":None,
            "general_reserved_zero_33bits":None,
            "general_reserved_zero_34bits":None,
            "general_reserved_zero_7bits":None,
            "general_one_picture_only_constraint_flag_2":None,
            "general_reserved_zero_35bits":None,
            "general_reserved_zero_43bits":None,
            "general_inbld_flag":None,
            "general_reserved_zero_bit":None,
            "general_level_idc":None,
            "sub_layer_profile_present_flag":None,
            "sub_layer_level_present_flag":None,
            "reserved_zero_2bits":None,
            "sub_layer_profile_space":None,
            "sub_layer_tier_flag":None,
            "sub_layer_profile_idc":None,
            "sub_layer_profile_compatibility_flag":None,
            "sub_layer_progressive_source_flag":None,
            "sub_layer_interlaced_source_flag":None,
            "sub_layer_non_packed_constraint_flag":None,
            "sub_layer_frame_only_constraint_flag":None,
            "sub_layer_max_12bit_constraint_flag":None,
            "sub_layer_max_10bit_constraint_flag":None,
            "sub_layer_max_8bit_constraint_flag":None,
            "sub_layer_max_422chroma_constraint_flag":None,
            "sub_layer_max_420chroma_constraint_flag":None,
            "sub_layer_max_monochrome_constraint_flag":None,
            "sub_layer_intra_constraint_flag":None,
            "sub_layer_one_picture_only_constraint_flag_1":None,
            "sub_layer_lower_bit_rate_constraint_flag":None,
            "sub_layer_max_14bit_constraint_flag":None,
            "sub_layer_reserved_zero_33bits":None,
            "sub_layer_reserved_zero_34bits":None,
            "sub_layer_reserved_zero_7bits":None,
            "sub_layer_one_picture_only_constraint_flag_2":None,
            "sub_layer_reserved_zero_35bits":None,
            "sub_layer_reserved_zero_43bits":None,
            "sub_layer_inbld_flag":None,
            "sub_layer_reserved_zero_bit":None,
            "sub_layer_level_idc":None,
            
            "vps_sub_layer_ordering_info_present_flag":None,
            "vps_max_dec_pic_buffering_minus1":None,
            "vps_max_num_reorder_pics":None,
            "vps_max_latency_increase_plus1":None,
            "vps_max_layer_id":None,
            "vps_num_layer_sets_minus1":None,
            "layer_id_included_flag":None,
            "vps_timing_info_present_flag":None,
            "vps_num_units_in_tick":None,
            "vps_time_scale":None,
            "vps_poc_proportional_to_timing_flag":None,
            "vps_num_ticks_poc_diff_one_minus1":None,
            "vps_num_hrd_parameters":None,
            "hrd_layer_set_idx":None,
            "hrd":None,
            "cprms_present_flag":None,
            "vps_extension_flag":None,
            #"vps_extension_data_flag":None
        }
        self.order["vps_max_dec_pic_buffering_minus1"] = []
        self.order["vps_max_num_reorder_pics"] = []
        self.order["vps_max_latency_increase_plus1"] = []
        self.order["layer_id_included_flag"] = [[]]
        self.order["hrd_layer_set_idx"] = []
        self.order["cprms_present_flag"] = []

        self.order["forbidden_zero_bit"] = self.s.read("uint:1")
        self.order["nal_unit_type"] = self.s.read("uint:6")
        self.order["nuh_layer_id"] = self.s.read("uint:6")
        self.order["nuh_temporal_id_plus1"] = self.s.read("uint:3")
        self.order["vps_video_parameter_set_id"] = self.s.read("uint:4")
        self.order["vps_base_layer_internal_flag"] = self.s.read("uint:1")
        self.order["vps_base_layer_available_flag"] = self.s.read("uint:1")
        self.order["vps_max_layers_minus1"] = self.s.read("uint:6")
        self.order["vps_max_sub_layers_minus1"] = self.s.read("uint:3")
        self.order["vps_temporal_id_nesting_flag"] = self.s.read("uint:1")
        self.order["vps_reserved_0xffff_16bits"] = self.s.read("uint:16")
        profile_tier_level(self, 1, self.order["vps_max_sub_layers_minus1"])
        self.order["vps_sub_layer_ordering_info_present_flag"] = self.s.read("uint:1")
        start_value = 0 if self.order["vps_sub_layer_ordering_info_present_flag"] else self.order["vps_max_sub_layers_minus1"]
        
        for i in range(start_value, self.order["vps_max_sub_layers_minus1"] + 1):
            self.order["vps_max_dec_pic_buffering_minus1"].append(self.s.read("ue"))
            self.order["vps_max_num_reorder_pics"].append(self.s.read("ue"))
            self.order["vps_max_latency_increase_plus1"].append(self.s.read("ue"))
        self.order["vps_max_layer_id"] = self.s.read("uint:6")
        self.order["vps_num_layer_sets_minus1"] = self.s.read("ue")

        rows = self.order["vps_num_layer_sets_minus1"]
        cols = self.order["vps_max_layer_id"] + 1
        self.order["layer_id_included_flag"] = [[] for _ in range(rows)]
        for row in self.order["layer_id_included_flag"]:
            row.extend([0] * cols)

        for i in range(1,self.order["vps_num_layer_sets_minus1"] + 1):
            for j in range(self.order["vps_max_layer_id"] + 1):
                self.order["layer_id_included_flag"][i][j] = self.s.read("uint:1")
        self.order["vps_timing_info_present_flag"] = self.s.read("uint:1")
        if self.order["vps_timing_info_present_flag"]:
            self.order["vps_num_units_in_tick"] = self.s.read("uint:32")
            self.order["vps_time_scale"] = self.s.read("uint:32")
            self.order["vps_poc_proportional_to_timing_flag"] = self.s.read("uint:1")
            if self.order["vps_poc_proportional_to_timing_flag"]:
                self.order["vps_num_ticks_poc_diff_one_minus1"] = self.s.read("ue")
            self.order["vps_num_hrd_parameters"] = self.s.read("ue")
            self.order["cprms_present_flag"] = [0] * self.order["vps_num_hrd_parameters"]
            for i in range(self.order["vps_num_hrd_parameters"]):
                self.order["hrd_layer_set_idx"].append(self.s.read("ue"))
                if i > 0:
                    self.order["cprms_present_flag"][i] = self.s.read("uint:1")
                self.order["hrd"] = h265_HRD(self.s, self.order["cprms_present_flag"][i], self.order["vps_max_sub_layers_minus1"])
        self.order["vps_extension_flag"] = self.s.read("uint:1")
        if self.order["vps_extension_flag"]: # Todo
            while(self.s):
                self.order["vps_extension_data_flag"] = self.s.read("uint:1")


class h265_SPS:
    def __init__(self, rbsp_bytes):
        self.s = rbsp_bytes
        self.order = {
            "forbidden_zero_bit":None,
            "nal_unit_type":None,
            "nuh_layer_id":None,
            "nuh_temporal_id_plus1":None,
            "sps_video_parameter_set_id":None,
            "sps_max_sub_layers_minus1":None,
            "sps_temporal_id_nesting_flag":None,
            "general_profile_space":None,
            "general_tier_flag":None,
            "general_profile_idc":None,
            "general_profile_compatibility_flag":None,
            "general_progressive_source_flag":None,
            "general_interlaced_source_flag":None,
            "general_non_packed_constraint_flag":None,
            "general_frame_only_constraint_flag":None,
            "general_max_12bit_constraint_flag":None,
            "general_max_10bit_constraint_flag":None,
            "general_max_8bit_constraint_flag":None,
            "general_max_422chroma_constraint_flag":None,
            "general_max_420chroma_constraint_flag":None,
            "general_max_monochrome_constraint_flag":None,
            "general_intra_constraint_flag":None,
            "general_one_picture_only_constraint_flag_1":None,
            "general_lower_bit_rate_constraint_flag":None,
            "general_max_14bit_constraint_flag":None,
            "general_reserved_zero_33bits":None,
            "general_reserved_zero_34bits":None,
            "general_reserved_zero_7bits":None,
            "general_one_picture_only_constraint_flag_2":None,
            "general_reserved_zero_35bits":None,
            "general_reserved_zero_43bits":None,
            "general_inbld_flag":None,
            "general_reserved_zero_bit":None,
            "general_level_idc":None,
            "sub_layer_profile_present_flag":None,
            "sub_layer_level_present_flag":None,
            "reserved_zero_2bits":None,
            "sub_layer_profile_space":None,
            "sub_layer_tier_flag":None,
            "sub_layer_profile_idc":None,
            "sub_layer_profile_compatibility_flag":None,
            "sub_layer_progressive_source_flag":None,
            "sub_layer_interlaced_source_flag":None,
            "sub_layer_non_packed_constraint_flag":None,
            "sub_layer_frame_only_constraint_flag":None,
            "sub_layer_max_12bit_constraint_flag":None,
            "sub_layer_max_10bit_constraint_flag":None,
            "sub_layer_max_8bit_constraint_flag":None,
            "sub_layer_max_422chroma_constraint_flag":None,
            "sub_layer_max_420chroma_constraint_flag":None,
            "sub_layer_max_monochrome_constraint_flag":None,
            "sub_layer_intra_constraint_flag":None,
            "sub_layer_one_picture_only_constraint_flag_1":None,
            "sub_layer_lower_bit_rate_constraint_flag":None,
            "sub_layer_max_14bit_constraint_flag":None,
            "sub_layer_reserved_zero_33bits":None,
            "sub_layer_reserved_zero_34bits":None,
            "sub_layer_reserved_zero_7bits":None,
            "sub_layer_one_picture_only_constraint_flag_2":None,
            "sub_layer_reserved_zero_35bits":None,
            "sub_layer_reserved_zero_43bits":None,
            "sub_layer_inbld_flag":None,
            "sub_layer_reserved_zero_bit":None,
            "sub_layer_level_idc":None,

            "sps_seq_parameter_set_id":None,
            "chroma_format_idc":None,
            "separate_colour_plane_flag":None,
            "pic_width_in_luma_samples":None,
            "pic_height_in_luma_samples":None,
            "conformance_window_flag":None,
            "conf_win_left_offset":None,
            "conf_win_right_offset":None,
            "conf_win_top_offset":None,
            "conf_win_bottom_offset":None,
            "bit_depth_luma_minus8":None,
            "bit_depth_chroma_minus8":None,
            "log2_max_pic_order_cnt_lsb_minus4":None,
            "sps_sub_layer_ordering_info_present_flag":None,
            "sps_max_dec_pic_buffering_minus1":None,
            "sps_max_num_reorder_pics":None,
            "sps_max_latency_increase_plus1":None,
            "log2_min_luma_coding_block_size_minus3":None,
            "log2_diff_max_min_luma_coding_block_size":None,
            "log2_min_luma_transform_block_size_minus2":None,
            "log2_diff_max_min_luma_transform_block_size":None,
            "max_transform_hierarchy_depth_inter":None,
            "max_transform_hierarchy_depth_intra":None,
            "scaling_list_enabled_flag":None,
            "sps_scaling_list_data_present_flag":None,

            "scaling_list_pred_mode_flag":None,
            "scaling_list_pred_matrix_id_delta":None,
            "scaling_list_dc_coef_minus8":None,
            "scaling_list_delta_coef":None,

            "amp_enabled_flag":None,
            "sample_adaptive_offset_enabled_flag":None,
            "pcm_enabled_flag":None,
            "pcm_sample_bit_depth_luma_minus1":None,
            "pcm_cample_bit_depth_chroma_minus1":None,
            "log2_min_pcm_luma_coding_block_size_minus3":None,
            "log2_diff_max_min_pcm_luma_coding_block_size":None,
            "pcm_loop_filter_disabled_flag":None,
            "num_short_term_ref_pic_sets":None,

            "inter_ref_pic_set_prediction_flag":None,
            "delta_idx_minus1":None,
            "delta_rps_sign":None,
            "abs_delta_rps_minus1":None,
            "used_by_curr_pic_flag":None,
            "use_delta_flag":None,
            "num_negative_pics":None,
            "num_positive_pics":None,
            "delta_poc_s0_minus1":None,
            "used_by_curr_pic_s0_flag":None,
            "delta_poc_s1_minus1":None,
            "used_by_curr_pic_s1_flag":None,



            "long_term_ref_pics_present_flag":None,
            "num_long_term_ref_pics_sps":None,
            "lt_ref_pic_poc_lsb_sps":None,
            "used_by_curr_pic_lt_sps_flag":None,
            "sps_temporal_mvp_enabled_flag":None,
            "strong_intra_smoothing_enabled_flag":None,
            "vui_parameters_present_flag":None,
            "vui":None,
            "sps_extension_present_flag":None,
            "sps_range_extension_flag":None,
            "sps_multilayer_extension_flag":None,
            "sps_scc_extension_flag":None,
            "sps_extension_4bits":None,
            "transform_skip_rotation_enabled_flag":None,
            "transform_skip_content_enabled_flag":None,
            "implicit_rdpcm_enabled_flag":None,
            "explicit_rdpcm_enabled_flag":None,
            "intra_smoothing_disabled_flag":None,
            "high_precision_offsets_enabled_flag":None,
            "persistent_rice_adaptation_enabled_flag":None,
            "cabac_bypass_alignment_enabled_flag":None,
            "inter_view_mv_vert_constraint_flag":None,
            "sps_3d_extension_flag":None,
            "iv_di_mc_enabled_flag":None,
            "iv_mv_scal_enabled_flag":None,
            "log2_ivmc_sub_pb_size_minus3":None,
            "iv_res_pred_enabled_flag":None,
            "depth_ref_enabled_flag":None,
            "vsp_mc_enabled_flag":None,
            "dbbp_enabled_flag":None,
            "tex_mc_enabled_flag":None,
            "log2_texmc_sub_pb_size_minus3":None,
            "intra_contour_enabled_flag":None,
            "intra_dc_only_wedge_enabled_flag":None,
            "cqt_cu_part_pred_enabled_flag":None,
            "inter_dc_only_enabled_flag":None,
            "skip_intra_enabled_flag":None,
            "sps_curr_pic_ref_enabled_flag":None,
            "palette_mode_enabled_flag":None,
            "palette_max_size":None,
            "delta_palette_max_predictor_size":None,
            "sps_palette_predictor_initializers_present_flag":None,
            "sps_num_palette_predictor_initializers_minus1":None,
            "sps_palette_predictor_initializer":None,
            "motion_vector_resolution_control_idc":None,
            "intra_boundary_filtering_disabled_flag":None,
            "sps_extension_data_flag":None
        }

        
        self.order["sps_max_dec_pic_buffering_minus1"] = []
        self.order["sps_max_num_reorder_pics"] = []
        self.order["sps_max_latency_increase_plus1"] = []
        self.order["scaling_list_pred_mode_flag"] = [[]]
        self.order["scaling_list_pred_matrix_id_delta"] = [[]]
        self.order["scaling_list_dc_coef_minus8"] = [[]]
        self.order["lt_ref_pic_poc_lsb_sps"] = []
        self.order["used_by_curr_pic_lt_sps_flag"] = []

        self.order["forbidden_zero_bit"] = self.s.read("uint:1")
        self.order["nal_unit_type"] = self.s.read("uint:6")
        self.order["nuh_layer_id"] = self.s.read("uint:6")
        self.order["nuh_temporal_id_plus1"] = self.s.read("uint:3")
        self.order["sps_video_parameter_set_id"] = self.s.read("uint:4")
        self.order["sps_max_sub_layers_minus1"] = self.s.read("uint:3")
        self.order["sps_temporal_id_nesting_flag"] = self.s.read("uint:1")
        profile_tier_level(self, 1, self.order["sps_max_sub_layers_minus1"])
        self.order["sps_seq_parameter_set_id"] = self.s.read("ue")
        self.order["chroma_format_idc"] = self.s.read("ue")
        if self.order["chroma_format_idc"] == 3:
            self.order["separate_colour_plane_flag"] = self.s.read("uint:1")
        self.order["pic_width_in_luma_samples"] = self.s.read("ue")
        self.order["pic_height_in_luma_amples"] = self.s.read("ue")
        self.order["conformance_window_flag"] = self.s.read("uint:1")
        if self.order["conformance_window_flag"]:
            self.order["conf_win_left_offset"] = self.s.read("ue")
            self.order["conf_win_right_offset"] = self.s.read("ue")
            self.order["conf_win_top_offset"] = self.s.read("ue")
            self.order["conf_win_bottom_offset"] = self.s.read("ue")
        self.order["bit_depth_luma_minus8"] = self.s.read("ue")
        self.order["bit_depth_chroma_minus8"] = self.s.read("ue")
        self.order["log2_max_pic_order_cnt_lsb_minus4"] = self.s.read("ue")
        self.order["sps_sub_layer_ordering_info_present_flag"] = self.s.read("uint:1")
        if self.order["sps_sub_layer_ordering_info_present_flag"]:
            i=0
        else:
            i = self.order["sps_max_sub_layers_minus1"]
        while i <= self.order["sps_max_sub_layers_minus1"]:
            self.order["sps_max_dec_pic_buffering_minus1"].append(self.s.read("ue"))
            self.order["sps_max_num_reorder_pics"].append(self.s.read("ue"))
            self.order["sps_max_latency_increase_plus1"].append(self.s.read("ue"))
            i += 1
        self.order["log2_min_luma_coding_block_size_minus3"] = self.s.read("ue")
        self.order["log2_diff_max_min_luma_coding_block_size"] = self.s.read("ue")
        self.order["log2_min_luma_transform_block_size_minus2"] = self.s.read("ue")
        self.order["log2_diff_max_min_luma_transform_block_size"] = self.s.read("ue")
        self.order["max_transform_hierarchy_depth_inter"] = self.s.read("ue")
        self.order["max_transform_hierarchy_depth_intra"] = self.s.read("ue")
        self.order["scaling_list_enabled_flag"] = self.s.read("uint:1")
        if self.order["scaling_list_enabled_flag"]:
            self.order["sps_scaling_list_data_present_flag"] = self.s.read("uint:1")
            if self.order["sps_scaling_list_data_present_flag"]:
                self.order["scaling_list_data"]()
        self.order["amp_enabled_flag"] = self.s.read("uint:1")
        self.order["sample_adaptive_offset_enabled_flag"] = self.s.read("uint:1")
        self.order["pcm_enabled_flag"] = self.s.read("uint:1")
        if self.order["pcm_enabled_flag"]:
            self.order["pcm_sample_bit_depth_luma_minus1"] = self.s.read("uint:4")
            self.order["pcm_sample_bit_depth_chroma_minus1"] = self.s.read("uint:4")
            self.order["log2_min_pcm_luma_coding_block_size_minus3"] = self.s.read("ue")
            self.order["log2_diff_max_min_pcm_luma_coding_block_size"] = self.s.read("ue")
            self.order["pcm_loop_filter_disabled_flag"] = self.s.read("uint:1")
        self.order["num_short_term_ref_pic_sets"] = self.s.read("ue")

        short_term_ref_pic_set = [0] * self.order["num_short_term_ref_pic_sets"]

        for i in range(self.order["num_short_term_ref_pic_sets"]):
            self.st_ref_pic_set(i, short_term_ref_pic_set)
        self.order["long_term_ref_pics_present_flag"] = self.s.read("uint:1")
        if self.order["long_term_ref_pics_present_flag"]:
            self.order["num_long_term_ref_pics_sps"] = self.s.read("ue")
            for i in range(self.order["num_long_term_ref_pics_sps"]):
                bitNum = self.order["log2_max_pic_order_cnt_lsb_minus4"] + 4
                self.order["lt_ref_pic_poc_lsb_sps"].append(self.s.read(f"{bitNum}"))
                self.order["used_by_curr_pic_lt_sps_flag"].append(self.s.read("uint:1"))
        self.order["sps_temporal_mvp_enabled_flag"] = self.s.read("uint:1")
        self.order["strong_intra_smoothing_enabled_flag"] = self.s.read("uint:1")
        self.order["vui_parameters_present_flag"] = self.s.read("uint:1")
        if self.order["vui_parameters_present_flag"]:
            self.vui = h265_VUI(self.s, self.order["sps_max_sub_layers_minus1"])
            get_color_parameters(self)
        self.order["sps_extension_present_flag"] = self.s.read("uint:1")
        if self.order["sps_extension_present_flag"]:
            self.order["sps_range_extension_flag"] = self.s.read("uint:1")
            self.order["sps_multilayer_extension_flag"] = self.s.read("uint:1")
            self.order["sps_3d_extension_flag"] = self.s.read("uint:1")
            self.order["sps_scc_extension_flag"] = self.s.read("uint:1")
            self.order["sps_extension_4bits"] = self.s.read("uint:4")
            if self.order["sps_range_extension_flag"]:
                self.order["transform_skip_rotation_enabled_flag"] = self.s.read("uint:1")
                self.order["transform_skip_content_enabled_flag"] = self.s.read("uint:1")
                self.order["implicit_rdpcm_enabled_flag"] = self.s.read("uint:1")
                self.order["explicit_rdpcm_enabled_flag"] = self.s.read("uint:1")
                self.order["extended_precision_processing_flag"] = self.s.read("uint:1")
                self.order["intra_smoothing_disabled_flag"] = self.s.read("uint:1")
                self.order["high_precision_offsets_enabled_flag"] = self.s.read("uint:1")
                self.order["persistent_rice_adaptation_enabled_flag"] = self.s.read("uint:1")
                self.order["cabac_bypass_alignment_enabled_flag"] = self.s.read("uint:1")
            if self.order["sps_multilayer_extension_flag"]:
                self.order["inter_view_mv_vert_constraint_flag"] = self.s.read("uint:1")
            if self.order["sps_3d_extension_flag"]:
                self.order["iv_di_mc_enabled_flag"] = []
                self.order["iv_mv_scal_enabled_flag"] = []
                self.order["log2_ivmc_sub_pb_size_minus3"] = []
                self.order["iv_res_pred_enabled_flag"] = []
                self.order["depth_ref_enabled_flag"] = []
                self.order["vsp_mc_enabled_flag"] = []
                self.order["dbbp_enabled_flag"] = []
                self.order["tex_mc_enabled_flag"] = []
                self.order["log2_texmc_sub_pb_size_minus3"] = []
                self.order["intra_contour_enabled_flag"] = []
                self.order["intra_dc_only_wedge_enabled_flag"] = []
                self.order["cqt_cu_part_pred_enabled_flag"] = []
                self.order["inter_dc_only_enabled_flag"] = []
                self.order["skip_intra_enabled_flag"] = []

                for d in range(2):
                    self.order["iv_di_mc_enabled_flag"].append(self.s.read("uint:1"))
                    self.order["iv_mv_scal_enabled_flag"].append(self.s.read("uint:1"))
                    if d == 0:
                        self.order["log2_ivmc_sub_pb_size_minus3"].append(self.s.read("ue"))
                        self.order["iv_res_pred_enabled_flag"].append(self.s.read("uint:1"))
                        self.order["depth_ref_enabled_flag"].append(self.s.read("uint:1"))
                        self.order["vsp_mc_enabled_flag"].append(self.s.read("uint:1"))
                        self.order["dbbp_enabled_flag"].append(self.s.read("uint:1"))
                    else:
                        self.order["tex_mc_enabled_flag"].append(self.s.read("uint:1"))
                        self.order["log2_texmc_sub_pb_size_minus3"].append(self.s.read("ue"))
                        self.order["intra_contour_enabled_flag"].append(self.s.read("uint:1"))
                        self.order["intra_dc_only_wedge_enabled_flag"].append(self.s.read("uint:1"))
                        self.order["cqt_cu_part_pred_enabled_flag"].append(self.s.read("uint:1"))
                        self.order["inter_dc_only_enabled_flag"].append(self.s.read("uint:1"))
                        self.order["skip_intra_enabled_flag"].append(self.s.read("uint:1"))
            if self.order["sps_scc_extension_flag"]:
                self.order["sps_curr_pic_ref_enabled_flag"] = self.s.read("uint:1")
                self.order["palette_mode_enabled_flag"] = self.s.read("uint:1")
                if self.order["palette_mode_enabled_flag"]:
                    self.order["palette_max_size"] = self.s.read("ue")
                    self.order["delta_palette_max_predictor_size"] = self.s.read("ue")
                    self.order["sps_palette_predictor_initializers_present_flag"] = self.s.read("uint:1")
                    self.order["motion_vector_resolution_control_idc"] = self.s.read("uint:2")
                    self.order["intra_boundary_filtering_disabled_flag"] = self.s.read("uint:1")
            if self.order["sps_extension_4bits"]:
                while(self.s):
                    self.order["sps_extension_data_flag"] = self.s.read("uint:1")
                    
    def scaling_list_data(self):
        ScalingList = [[[]]]
        rows = 4
        cols = 6
        self.order["scaling_list_pred_mode_flag"] = [[] for _ in range(rows)]
        for row in self.order["scaling_list_pred_mode_flag"]:
            row.extend([0] * cols)

        self.order["scaling_list_pred_matrix_id_delta"] = [[] for _ in range(rows)]
        for row in self.order["scaling_list_pred_matrix_id_delta"]:
            row.extend([0] * cols)

        rows = 2
        cols = 6
        self.order["scaling_list_dc_coef_minus8"] = [[] for _ in range(rows)]
        for row in self.order["scaling_list_dc_coef_minus8"]:
            row.extend([0] * cols)

        for sizeId in range(4):
            matrixId = 0
            while matrixId < 6:
                self.order[f"scaling_list_pred_mode_flag[{sizeId}][{matrixId}]"] = self.s.read("uint:1")
                if self.order["scaling_list_pred_mode_flag"] == 0:
                    self.order[f"scaling_list_pred_matrix_id_delta[{sizeId}][{matrixId}]"] = self.s.read("ue")
                else:
                    nextCoef = 8
                    coefNum = min(64, (1 << (4+(sizeId << 1))))
                    if sizeId > 1:
                        self.order[f"scaling_list_dc_coef_minus8[{sizeId}-2][{matrixId}]"] = self.s.read("se")
                        nextCoef = self.order[f"scaling_list_dc_coef_minus8[{sizeId}-2][{matrixId}]"] + 8
                    for i in range(coefNum):
                        self.order["scaling_list_delta_coef"] = self.s.read("se")
                        nextCoef = (nextCoef + self.order["scaling_list_delta_coef"] + 256) % 256
                        ScalingList.append = nextCoef

    def get_formatProfile(self):
        if self.order["general_profile_space"] == 0:
            if self.order["general_profile_idc"] == 1:
                profile = 'Main'
            elif self.order["general_profile_idc"] == 2:
                profile = 'Main 10'
            elif self.order["general_profile_idc"] == 3:
                profile = 'Main Still'
            elif self.order["general_profile_idc"] == 4:
                profile = 'Format Range'
            elif self.order["general_profile_idc"] == 5:
                profile = 'High Throughput'
            elif self.order["general_profile_idc"] == 6:
                profile = 'Multiview Main'
            elif self.order["general_profile_idc"] == 7:
                profile = 'Scalable Main'
            elif self.order["general_profile_idc"] == 8:
                profile = '3D Main'
            elif self.order["general_profile_idc"] == 9:
                profile = 'Screen Content'
            elif self.order["general_profile_idc"] == 10:
                profile = 'Scalable Format Range'

            if self.order["general_level_idc"]:
                level_tmp = float(self.order["general_level_idc"]) / 30
                if self.order["general_level_idc"] % 10 != 0:
                    level = round(level_tmp,1)
                else:
                    level = round(level_tmp)
            profile = profile + f' {level}'

        return profile
    def st_ref_pic_set(self, stRpsIdx, refPicSets):
        self.order["delta_poc_s0_minus1"] = []
        self.order["used_by_curr_pic_s0_flag"] = []
        self.order["delta_poc_s1_minus1"] = []
        self.order["used_by_curr_pic_s1_flag"] = []

        self.order["inter_ref_pic_set_prediction_flag"] = 0
        self.order["delta_idx_minus1"] = 0
        if stRpsIdx != 0:
            self.order["inter_ref_pic_set_prediction_flag"] = self.s.read("uint:1")
        if self.order["inter_ref_pic_set_prediction_flag"]:
            if stRpsIdx == self.order["num_short_term_ref_pic_sets"]:
                self.order["delta_idx_minus1"] = self.s.read("ue")
            self.order["delta_rps_sign"] = self.s.read("uint:1")
            self.order["abs_delta_rps_minus1"] = self.s.read("ue")
            RefRpsIdx = stRpsIdx - (self.order["delta_idx_minus1"] + 1)

            # if refPicSets[RefRpsIdx]: # TODO
        else:
            self.order["num_negative_pics"] = self.s.read("ue")
            self.order["num_positive_pics"] = self.s.read("ue")
            for i in range(self.order["num_negative_pics"]):
                self.order["delta_poc_s0_minus1"].append(self.s.read("ue"))
                self.order["used_by_curr_pic_s0_flag"].append(self.s.read("uint:1"))
            for i in range(self.order["num_positive_pics"]):
                self.order["delta_poc_s1_minus1"].append(self.s.read("ue"))
                self.order["used_by_curr_pic_s1_flag"].append(self.s.read("uint:1"))

    
class h265_PPS:
    def __init__(self, rbsp_bytes):
        self.s = rbsp_bytes
        self.order = {
            "forbidden_zero_bit":None,
            "nal_unit_type":None,
            "nuh_layer_id":None,
            "nuh_temporal_id_plus1":None,
            "pps_pic_parameter_set_id":None,
            "pps_seq_parameter_set_id":None,
            "dependent_slice_segments_enabled_flag":None,
            "output_flag_present_flag":None,
            "num_extra_slice_header_bits":None,
            "sign_data_hiding_enabled_flag":None,
            "cabac_init_present_flag":None,
            "num_ref_idx_l0_default_active_minus1":None,
            "num_ref_idx_l1_default_active_minus1":None,
            "init_qp_minus26":None,
            "constrained_intra_pred_flag":None,
            "transform_skip_enabled_flag":None,
            "cu_qp_delta_enabled_flag":None,
            "diff_cu_qp_delta_depth":None,
            "pps_cb_qp_offset":None,
            "pps_cr_qp_offset":None,
            "pps_slice_chroma_qp_offsets_present_flag":None,
            "weighted_pred_flag":None,
            "weighted_bipred_flag":None,
            "transquant_bypass_enabled_flag":None,
            "tiles_enabled_flag":None,
            "entropy_coding_sync_enabled_flag":None,
            "num_tile_columns_minus1":None,
            "num_tile_rows_minus1":None,
            "uniform_spacing_flag":None,
            "column_width_minus1":None,
            "row_height_minus1":None,
            "loop_filter_across_tiles_enabled_flag":None,
            "pps_loop_filter_across_slices_enabled_flag":None,
            "deblocking_filter_control_present_flag":None,
            "deblocking_filter_override_enabled_flag":None,
            "pps_deblocking_filter_disabled_flag":None,
            "pps_beta_offset_div2":None,
            "pps_tc_offset_div2":None,
            "pps_scaling_list_data_present_flag":None,
            "lists_modification_present_flag":None,
            "log2_parallel_merge_level_minus2":None,
            "slice_segment_header_extension_present_flag":None,
            "pps_extension_present_flag":None,
            "pps_range_extension_flag":None,
            "pps_multilayer_extension_flag":None,
            "pps_3d_extension_flag":None,
            "pps_scc_extension_flag":None,
            "pps_extension_4bits":None,

            "log2_max_transform_skip_block_size_minus2":None,
            "cross_component_prediction_enabled_flag":None,
            "chroma_qp_offset_list_enabled_flag":None,
            "diff_cu_chroma_qp_offset_depth":None,
            "chroma_qp_offset_list_len_minus1":None,
            "cb_qp_offset_list":None,
            "cr_qp_offset_list":None,
            "log2_sao_offset_scale_luma":None,
            "log2_sao_offset_scale_chroma":None,
            "poc_reset_info_present_flag":None,
            "pps_infer_scaling_list_flag":None,
            "pps_scaling_list_ref_layer_id":None,
            "num_ref_loc_offsets":None,
            "ref_loc_offset_layer_id":None,
            "scaled_ref_layer_offset_present_flag":None,
            "scaled_ref_layer_left_offset":None,
            "scaled_ref_layer_top_offset":None,
            "scaled_ref_layer_right_offset":None,
            "scaled_ref_layer_bottom_offset":None,
            "ref_region_offset_present_flag":None,
            "ref_region_left_offset":None,
            "ref_region_top_offset":None,
            "ref_region_right_offset":None,
            "ref_region_bottom_offset":None,
            "resample_phase_set_present_flag":None,
            "phase_hor_luma":None,
            "phase_ver_luma":None,
            "phase_hor_chroma_plus8":None,
            "phase_ver_chroma_plus8":None,
            "colour_mapping_enabled_flag":None,
            "num_cm_ref_layers_minus1":None,
            "cm_ref_layer_id":None,
            "cm_octant_depth":None,
            "cm_y_part_num_log2":None,
            "luma_bit_depth_cm_input_minus8":None,
            "chroma_bit_depth_cm_input_minus8":None,
            "luma_bit_depth_cm_output_minus8":None,
            "chroma_bit_depth_cm_output_minus8":None,
            "cm_res_quant_bits":None,
            "cm_delta_flc_bits_minus1":None,
            "cm_adapt_threshold_u_delta":None,
            "cm_adapt_threshold_v_delta":None,
            "dlts_present_flag":None,
            "pps_depth_layers_minus1":None,
            "pps_bit_depth_for_depth_layers_minus8":None,
            "dlt_flag":None,
            "dlt_pred_flag":None,
            "dlt_val_flags_present_flag":None,
            "dlt_value_flag":None,
            "num_val_delta_dlt":None,
            "max_diff":None,
            "min_diff_minus1":None,
            "delta_dlt_val0":None,
            "delta_val_diff_minus_min":None,

            "pps_extension_data_flag":None
        }

        self.order["forbidden_zero_bit"] = self.s.read("uint:1")
        self.order["nal_unit_type"] = self.s.read("uint:6")
        self.order["nuh_layer_id"] = self.s.read("uint:6")
        self.order["nuh_temporal_id_plus1"] = self.s.read("uint:3")
        self.order["pps_pic_parameter_set_id"] = self.s.read("ue")
        self.order["pps_seq_parameter_set_id"] = self.s.read("ue")
        self.order["dependent_slice_segments_enabled_flag"] = self.s.read("uint:1")
        self.order["output_flag_present_flag"] = self.s.read("uint:1")
        self.order["num_extra_slice_header_bits"] = self.s.read("uint:3")
        self.order["sign_data_hiding_enabled_flag"] = self.s.read("uint:1")
        self.order["cabac_init_present_flag"] = self.s.read("uint:1")
        self.order["num_ref_idxl0_default_active_minus1"] = self.s.read("ue")
        self.order["num_ref_idxl1_default_active_minus1"] = self.s.read("ue")
        self.order["init_qp_minus26"] = self.s.read("se")
        self.order["constrained_intra_pred_flag"] = self.s.read("uint:1")
        self.order["transform_skip_enabled_flag"] = self.s.read("uint:1")
        self.order["cu_qp_delta_enabled_flag"] = self.s.read("uint:1")
        if self.order["cu_qp_delta_enabled_flag"]:
            self.order["diff_cu_qp_delta_depth"] = self.s.read("ue")
        self.order["pps_cb_qp_offset"] = self.s.read("se")
        self.order["pps_cr_qp_offset"] = self.s.read("se")
        self.order["pps_slice_chroma_qp_offsets_present_flag"] = self.s.read("uint:1")
        self.order["weighted_pred_flag"] = self.s.read("uint:1")
        self.order["weighted_bipred_flag"] = self.s.read("uint:1")
        self.order["transquant_bypass_enabled_flag"] = self.s.read("uint:1")
        self.order["tiles_enabled_flag"] = self.s.read("uint:1")
        self.order["entropy_coding_sync_enabled_flag"] = self.s.read("uint:1")
        if self.order["tiles_enabled_flag"]:
            self.order["num_tile_columns_minus1"] = self.s.read("ue")
            self.order["num_tile_rows_minus1"] = self.s.read("ue")
            self.order["uniform_spacing_flag"] = self.s.read("uint:1")
            if self.order["uniform_spacing_flag"] == 0:
                self.order["column_width_minus1"] = []
                self.order["column_height_minus1"] = []
                for i in range(self.order["num_tile_columns_minus1"]):
                    self.order["column_width_minus1"].append(self.s.read("ue"))
                for i in range(self.order["num_tile_rows_minus1"]):
                    self.order["column_height_minus1"].append(self.s.read("ue"))
            self.order["loop_filter_across_tiles_enabled_flag"] = self.s.read("uint:1")
        self.order["pps_loop_filter_across_slices_enabled_flag"] = self.s.read("uint:1")
        self.order["deblocking_filter_control_present_flag"] = self.s.read("uint:1")
        if self.order["deblocking_filter_control_present_flag"]:
            self.order["deblocking_filter_override_enabled_flag"] = self.s.read("uint:1")
            self.order["pps_deblocking_filter_disabled_flag"] = self.s.read("uint:1")
            if self.order["pps_deblocking_filter_disabled_flag"] == 0:
                self.order["pps_beta_offset_div2"] = self.s.read("se")
                self.order["pps_tc_offset_div2"] = self.s.read("se")
        self.order["pps_scaling_list_data_present_flag"] = self.s.read("uint:1")
        if self.order["pps_scaling_list_data_present_flag"]:
            self.scaling_list_data()
        self.order["lists_modification_present_flag"] = self.s.read("uint:1")
        self.order["log2_parallel_merge_level_minus2"] = self.s.read("ue")
        self.order["slice_segment_header_extension_present_flag"] = self.s.read("uint:1")
        self.order["pps_extension_present_flag"] = self.s.read("uint:1")
        if self.order["pps_extension_present_flag"]:
            self.order["pps_range_extension_flag"] = self.s.read("uint:1")
            self.order["pps_multilayer_extension_flag"] = self.s.read("uint:1")
            self.order["pps_3d_extension_flag"] = self.s.read("uint:1")
            self.order["pps_scc_extension_flag"] = self.s.read("uint:1")
            self.order["pps_extension_4bits"] = self.s.read("uint:4")
            if self.order["pps_range_extension_flag"]:
                if self.order["transform_skip_enabled_flag"]:
                    self.order["log2_max_transform_skip_block_size_minus2"] = self.s.read("ue")
                self.order["cross_component_prediction_enabled_flag"] = self.s.read("uint:1")
                self.order["chroma_qp_offset_list_enabled_flag"] = self.s.read("uint:1")
                if self.order["chroma_qp_offset_list_enabled_flag"]:
                    self.order["cb_qp_offset_list"] = []
                    self.order["cr_qp_offset_list"] = []
                    self.order["diff_cu_chroma_qp_offset_depth"] = self.s.read("ue")
                    self.order["chroma_qp_offset_list_len_minus1"] = self.s.read("ue")
                    for i in range(self.order["chroma_qp_offset_list_len_minus1"] + 1):
                        self.order["cb_qp_offset_list"].append(self.s.read("se"))
                        self.order["cr_qp_offset_list"].append(self.s.read("se"))
                self.order["log2_sao_offset_scale_luma"] = self.s.read("ue")
                self.order["log2_sao_offset_scale_chroma"] = self.s.read("ue")
            if self.order["pps_multilayer_extension_flag"]:
                self.order["ref_loc_offset_layer_id"] = []
                self.order["scaled_ref_layer_offset_present_flag"] = []
                self.order["scaled_ref_layer_left_offset"] = []
                self.order["scaled_ref_layer_top_offset"] = []
                self.order["scaled_ref_layer_right_offset"] = []
                self.order["scaled_ref_layer_bottom_offset"] = []
                self.order["ref_region_offset_present_flag"] = []
                self.order["ref_region_left_offset"] = []
                self.order["ref_region_top_offset"] = []
                self.order["ref_region_right_offset"] = []
                self.order["ref_region_bottom_offset"] = []
                self.order["resample_phase_set_present_flag"] = []
                self.order["phase_hor_luma"] = []
                self.order["phase_ver_luma"] = []
                self.order["phase_hor_chroma_plus8"] = []
                self.order["phase_ver_chroma_plus8"] = []

                self.order["poc_reset_info_present_flag"] = self.s.read("uint:1")
                self.order["pps_infer_scaling_list_flag"] = self.s.read("uint:1")
                if self.order["pps_infer_scaling_list_flag"]:
                    self.order["pps_scaling_list_ref_layer_id"] = self.s.read("uint:6")
                self.order["num_ref_loc_offsets"] = self.s.read("ue")
                for i in range(self.order["num_ref_loc_offsets"]):
                    self.order["ref_loc_offset_layer_id"].append(self.s.read("uint:6"))
                    self.order["scaled_ref_layer_offset_present_flag"].append(self.s.read("uint:1"))
                    if self.order[f"scaled_ref_layer_offset_present_flag[{i}]"]:
                        self.order["scaled_ref_layer_left_offset"].append(self.s.read("se"))
                        self.order["scaled_ref_layer_top_offset"].append(self.s.read("se"))
                        self.order["scaled_ref_layer_right_offset"].append(self.s.read("se"))
                        self.order["scaled_ref_layer_bottom_offset"].append(self.s.read("se"))
                    self.order["ref_region_offset_present_flag"] = self.s.read("uint:1")
                    if self.order["ref_region_offset_present_flag"]:
                        self.order["ref_region_left_offset"].append(self.s.read("se"))
                        self.order["ref_region_top_offset"].append(self.s.read("se"))
                        self.order["ref_region_right_offset"].append(self.s.read("se"))
                        self.order["ref_region_bottom_offset"].append(self.s.read("se"))
                    self.order["resample_phase_set_present_flag"] = self.s.read("uint:1")
                    if self.order["resample_phase_set_present_flag"]:
                        self.order["phase_hor_luma"].append(self.s.read("ue"))
                        self.order["phase_ver_luma"].append(self.s.read("ue"))
                        self.order["phase_hor_chroma_plus8"].append(self.s.read("ue"))
                        self.order["phase_ver_chroma_plus8"].append(self.s.read("ue"))
                self.order["colour_mapping_enabled_flag"] = self.s.read("uint:1")
                if self.order["colour_mapping_enabled_flag"]:
                    self.order["colour_mapping_table"]()
            if self.order["pps_3d_extension_flag"]:
                self.order["dlt_flag"] = []
                self.order["dlt_pred_flag"] = []
                self.order["dlt_val_flags_present_flag"] = []
                self.order["dlt_value_flag"] = [[]]

                depthMaxValue = (1 << (self.order["pps_bit_depth_for_depth_layers_minus8"] + 8)) - 1
                rows = self.order["pps_depth_layers_minus1"]
                cols = depthMaxValue
                self.order["dlt_value_flag"] = [[] for _ in range(rows)]
                for row in self.order["dlt_value_flag"]:
                    row.extend([0] * cols)

                self.order["dlts_present_flag"] = self.s.read("uint:1")
                if self.order["dlts_present_flag"]:
                    self.order["pps_depth_layers_minus1"] = self.s.read("uint:6")
                    self.order["pps_bit_depth_for_depth_layers_minus8"] = self.s.read("uint:4")
                    for i in range(self.order["pps_depth_layers_minus1"] + 1):
                        self.order["dlt_flag"].append(self.s.read("uint:1"))
                        if self.order["dlt_flag"][i]:
                            self.order["dlt_pred_flag"].append(self.s.read("uint:1"))
                            if self.order["dlt_pred_flag"][i] == 0:
                                self.order["dlt_val_flags_present_flag"].append(self.s.read("uint:1"))
                            if self.order["dlt_val_flags_present_flag"][i]:
                                for j in range(depthMaxValue + 1):
                                    self.order["dlt_value_flag"][i][j] = self.s.read("uint:1")
                            else:
                                self.order["delta_dlt"](i)
            if self.order["pps_extension_4bits"]:
                while(self.s):
                    self.order["pps_extension_data_flag"] = self.s.read("uint:1")
                

    
    def scaling_list_data(self):
        ScalingList = [[[]]]
        rows = 4
        cols = 6
        self.order["scaling_list_pred_mode_flag"] = [[] for _ in range(rows)]
        for row in self.order["scaling_list_pred_mode_flag"]:
            row.extend([0] * cols)

        self.order["scaling_list_pred_matrix_id_delta"] = [[] for _ in range(rows)]
        for row in self.order["scaling_list_pred_matrix_id_delta"]:
            row.extend([0] * cols)

        rows = 2
        cols = 6
        self.order["scaling_list_dc_coef_minus8"] = [[] for _ in range(rows)]
        for row in self.order["scaling_list_dc_coef_minus8"]:
            row.extend([0] * cols)

        for sizeId in range(4):
            matrixId = 0
            while matrixId < 6:
                self.order[f"scaling_list_pred_mode_flag[{sizeId}][{matrixId}]"] = self.s.read("uint:1")
                if self.order["scaling_list_pred_mode_flag"] == 0:
                    self.order[f"scaling_list_pred_matrix_id_delta[{sizeId}][{matrixId}]"] = self.s.read("ue")
                else:
                    nextCoef = 8
                    coefNum = min(64, (1 << (4+(sizeId << 1))))
                    if sizeId > 1:
                        self.order[f"scaling_list_dc_coef_minus8[{sizeId}-2][{matrixId}]"] = self.s.read("se")
                        nextCoef = self.order[f"scaling_list_dc_coef_minus8[{sizeId}-2][{matrixId}]"] + 8
                    for i in range(coefNum):
                        self.order["scaling_list_delta_coef"] = self.s.read("se")
                        nextCoef = (nextCoef + self.order["scaling_list_delta_coef"] + 256) % 256
                        ScalingList.append = nextCoef
    
    def colour_mapping_table(self):
        self.order["cm_ref_layer_id"] = []
        self.order["num_cm_ref_layers_minus1"] = self.s.read("ue")
        for i in range(self.order["num_cm_ref_layers_minus1"] + 1):
            self.order["cm_ref_layer_id"].append(self.s.read("uint:6"))
        self.order["cm_octant_depth"] = self.s.read("uint:2")
        self.order["cm_y_part_num_log2"] = self.s.read("uint:2")
        self.order["luma_bit_depth_cm_input_minus8"] = self.s.read("ue")
        self.order["chroma_bit_depth_cm_input_minus8"] = self.s.read("ue")
        self.order["luma_bit_depth_cm_output_minus8"] = self.s.read("ue")
        self.order["chroma_bit_depth_cm_output_minus8"] = self.s.read("ue")
        self.order["cm_res_quant_bits"] = self.s.read("uint:2")
        self.order["cm_delta_flc_bits_minus1"] = self.s.read("uint:2")
        if self.order["cm_octant_depth"] == 1:
            self.order["cm_adapt_threshold_u_delta"] = self.s.read("se")
            self.order["cm_adapt_threshold_v_delta"] = self.s.read("se")
    
    def delta_dlt(self, i):
        length = self.order["pps_bit_depth_for_depth_layers_minus8"] + 8
        self.order["num_val_delta_dlt"] = self.s.read(f"{length}")
        if self.order["num_val_delta_dlt"] > 0:
            if self.order["num_val_delta_dlt"] > 1:
                self.order["max_diff"] = self.s.read(f"{length}")
