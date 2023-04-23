import os
import re

DIR='../../TestVector/avs3_core'
FRM=10
LCU=25
W_LCU=5
W_FRM = 3840
H_FRM = 2112
TV=DIR+'/tv'
ADDR=TV+'/addr_map.txt'
LIBPIC=0
I_PERIOD = 5

#将ddr中的地址按照32字节对齐
def align32(address):
    if address%32==0:
        return address
    else:
        return (address//32+1)*32

#根据dcp cpr基地址将dcp cpr各个地址写进reg_config文件中
def write_dcp_cpr_address(f_reg_config, dcp_base_addr, cpr_base_addr):
    f_reg_config.write("Write_reg(dcp_ref_frm_addr_y_1, " + "{0:}".format(hex(dcp_base_addr)) + ");\n")
    dcp_base_addr = align32(dcp_base_addr + W_FRM * H_FRM)
    f_reg_config.write("Write_reg(dcp_ref_aux_addr_y_1, " + "{0:}".format(hex(dcp_base_addr)) + ");\n")
    dcp_base_addr = align32(dcp_base_addr + LCU * 64)
    f_reg_config.write("Write_reg(dcp_ref_frm_addr_u_1, " + "{0:}".format(hex(dcp_base_addr)) + ");\n")
    dcp_base_addr = align32(dcp_base_addr + W_FRM * H_FRM)
    f_reg_config.write("Write_reg(dcp_ref_aux_addr_u_1, " + "{0:}".format(hex(dcp_base_addr)) + ");\n")
    dcp_base_addr = align32(dcp_base_addr + LCU * 64)
    f_reg_config.write("Write_reg(dcp_ref_frm_addr_v_1, " + "{0:}".format(hex(dcp_base_addr)) + ");\n")
    dcp_base_addr = align32(dcp_base_addr + W_FRM * H_FRM)
    f_reg_config.write("Write_reg(dcp_ref_aux_addr_v_1, " + "{0:}".format(hex(dcp_base_addr)) + ");\n")

    f_reg_config.write("Write_reg(cpr_ref_frm_addr_y_1, " + "{0:}".format(hex(cpr_base_addr)) + ");\n")
    cpr_base_addr = align32(cpr_base_addr + W_FRM * H_FRM)
    f_reg_config.write("Write_reg(cpr_ref_aux_addr_y_1, " + "{0:}".format(hex(cpr_base_addr)) + ");\n")
    cpr_base_addr = align32(cpr_base_addr + LCU * 64)
    f_reg_config.write("Write_reg(cpr_ref_frm_addr_u_1, " + "{0:}".format(hex(cpr_base_addr)) + ");\n")
    cpr_base_addr = align32(cpr_base_addr + W_FRM * H_FRM)
    f_reg_config.write("Write_reg(cpr_ref_aux_addr_u_1, " + "{0:}".format(hex(cpr_base_addr)) + ");\n")
    cpr_base_addr = align32(cpr_base_addr + LCU * 64)
    f_reg_config.write("Write_reg(cpr_ref_frm_addr_v_1, " + "{0:}".format(hex(cpr_base_addr)) + ");\n")
    cpr_base_addr = align32(cpr_base_addr + W_FRM * H_FRM)
    f_reg_config.write("Write_reg(cpr_ref_aux_addr_v_1, " + "{0:}".format(hex(cpr_base_addr)) + ");\n")

'''
 0 | dcp |     | cpr 
 1 | cpr |     | dcp
 2 | dcp | cpr |
 3 | cpr | dcp |
 4 | dcp | cpr |
 5 | cpr | dcp |
 6 | cpr |     | dcp
 7 | dcp | cpr |
 8 | cpr | dcp |
 9 | dcp | cpr |
10 | cpr | dcp |
11 | dcp |     | cpr
'''
def dcp_cpr_memory_offset_libpic(f_reg_config):
    if count == 0 or count == 2 * I_PERIOD + 1:
        dcp_base_addr = 0x90000000
        cpr_base_addr = 0x94000000
        write_dcp_cpr_address(f_reg_config, dcp_base_addr, cpr_base_addr)   
        count = 0
    elif count <= 2 * I_PERIOD and count > 0:
        #参考libpic图像
        if count % I_PERIOD == 1:
            dcp_base_addr = 0x94000000
            cpr_base_addr = 0x90000000
            write_dcp_cpr_address(f_reg_config, dcp_base_addr, cpr_base_addr)
        #P帧中除去参考libpic外的单数帧
        elif count % I_PERIOD != 1 and count % 2 == 1:
            dcp_base_addr = 0x92000000
            cpr_base_addr = 0x90000000
            write_dcp_cpr_address(f_reg_config, dcp_base_addr, cpr_base_addr)
        elif count % I_PERIOD != 1 and count % 2 == 0:
            dcp_base_addr = 0x90000000
            cpr_base_addr = 0x92000000
            write_dcp_cpr_address(f_reg_config, dcp_base_addr, cpr_base_addr)
    count += 1

def dcp_cpr_memory_offset(f_reg_config, frm):
    if frm % 2 == 1:
        dcp_base_addr = 0x90000000
        cpr_base_addr = 0x92000000
        write_dcp_cpr_address(f_reg_config, dcp_base_addr, cpr_base_addr)
    else :
        dcp_base_addr = 0x92000000
        cpr_base_addr = 0x90000000
        write_dcp_cpr_address(f_reg_config, dcp_base_addr, cpr_base_addr)

#将dat文件中的寄存器offset信息写入到addr.txt中
def f_addr_write():
    f_addr = open(ADDR, "w")
    f_addr.write("sync_start 0x0\n")
    f_addr.write("lcu_count_clear 0x14\n")
    filtered_files = ["./json/"+file for file in os.listdir("json") if file.endswith(".dat")]
    #filtered_files = ["./json/" + x for x in filtered_files]
    for name in filtered_files:
        with open(name) as f:
            for line in f:
                re.sub(r"data_axi_V", "bs_data", name)
                f_addr.write(line)
    f_addr.close()

def sed_ctx_map(ddr_map_dict):
    ddr_map_dict["ctx_map_mv"] = ddr_map_dict["ctx_map_map_mv"]
    ddr_map_dict["ctx_map_scu"] = ddr_map_dict["ctx_map_map_scu"]
    ddr_map_dict["ctx_map_refi"] =  ddr_map_dict["ctx_map_map_refi"]
    ddr_map_dict["ctx_map_cu_mode"] = ddr_map_dict["ctx_map_map_cu_mode"]
    ddr_map_dict["list_ptr_0_skip"] = ddr_map_dict["list_ptr_0"]
    ddr_map_dict["ctx_pinter_refp_map_mv_0"] = ddr_map_dict["ctx_pinter_refp_map_mv_0_skip"]
    ddr_map_dict["ctx_pinter_refp_map_refi_0"] = ddr_map_dict["ctx_pinter_refp_map_refi_0_skip"]

if __name__ == '__main__':
    global count
    count = 0
    #1. 将dat文件中的寄存器offset信息写入到addr.txt中
    f_addr_write()

    if LIBPIC == 1:
        frm = 0
    else :
        frm = 1

    while frm < FRM:
        REG_CONFIG = DIR+'/reg_config_'+str(frm)+'.txt'
        ADDR_MAP = DIR+'/addr_map_'+str(frm)+'.txt' 
        DDR_MAP = TV+'/ddr_map.txt'
        print(REG_CONFIG)
        print(ADDR_MAP)
        print(DDR_MAP)
        f_addr_map = open(ADDR_MAP, 'w')
        f_addr = open(ADDR, 'r')
        f_addr_map.write(f_addr.read())
        f_addr.close()

        lcu = LCU - 1
        offset = 0x80000000
        #过滤出每一帧最后一个lcu所有mem的文件名
        vegetables = "put_mem_"
        #if vegetables in file
        putmem = [file for file in os.listdir(TV) if vegetables in file]
        putmem = list(filter(lambda x: x.endswith('.txt'), putmem))
        vegetables = "_" + str(frm) + "_" + str(lcu)
        print(vegetables)
        putmem = [putmem_node for putmem_node in putmem if vegetables in putmem_node]
        putmem.append("input_mem_imgY_org_ap_V_" + str(frm) + "_0.txt")
        putmem.append("input_mem_imgU_org_ap_V_" + str(frm) + "_0.txt")
        putmem.append("input_mem_imgV_org_ap_V_" + str(frm) + "_0.txt")
        putmem = [TV +"/" + file for file in putmem ]
        print(putmem)

        f_ddr_map = open(DDR_MAP, 'w+')
        #将各个memory的地址放入到DDR MAP 中
        for file in putmem:
            with open(file, 'r') as f_putmem:
                first_line = f_putmem.readline()
                if "bs_data" in first_line:
                    print("skip bs data")
                else:
                    first_line_split = first_line.split()
                    output_to_ddr_map = first_line_split[0] + " " + "{0:}".format(hex(offset))
                    f_ddr_map.write(output_to_ddr_map + "\n")
                    bit = int(first_line_split[1])
                    depth = int(first_line_split[2])
                    offset += align32(bit * depth)
            f_putmem.close()
        output_to_ddr_map = "bs_data" + " " + "{0:}".format(hex(offset))
        f_ddr_map.write(output_to_ddr_map + "\n")
        print("grep")

        #替换ctx 输入 输出相同地址
        ddr_map_dict = {}
        f_ddr_map.seek(0, 0)
        for f_ddr_map_line in f_ddr_map.readlines():
            key, value = f_ddr_map_line.split()
            ddr_map_dict[key] = value
        f_ddr_map.close()
        sed_ctx_map(ddr_map_dict)

        print(ddr_map_dict)
        f_ddr_map = open(DDR_MAP, 'w')   #偏移到文件头
        for raw in ddr_map_dict.keys():
            f_addr_map.write(raw + ' ' + ddr_map_dict[raw] + "\n")
            f_ddr_map.write(raw + ' ' + ddr_map_dict[raw] + "\n")
        f_addr_map.close()
        f_ddr_map.close()

        lcu = 0
        f_reg_config = open(REG_CONFIG, 'w')
        #f_mem_config = open(MEM_CONFIG, 'w')
        while lcu < LCU:

            f_reg_config.write("Wait_irq_pos(0)\n")
            if lcu == 0:
                f_reg_config.write("Write_reg(lcu_count_clear, 0x7);\n")
                f_reg_config.write("Write_reg(clear_offset, 0x1);\n")
                
            input_reg = TV + "/input_reg_" + str(frm) + "_" + str(lcu) + ".txt"
            f_input_reg = open(input_reg, 'r')
            for line in f_input_reg.readlines():
                reg_name = line.split()[0]
                reg_value = line.split()[1]
                #reg_name, reg_value = line.split()
                f_reg_config.write("Write_reg(" + reg_name + ", " + reg_value + ");\n")
            f_input_reg.close()

            f_ddr_map = open(DDR_MAP, 'r')
            for line in f_ddr_map.readlines():
                ddr_name, ddr_value = line.split()
                f_reg_config.write("Write_reg(" + ddr_name + "_offset, " + ddr_value + ");\n")
            f_ddr_map.close()

            #生成mem_config.txt，在reg_config.txt中添加write_mem
            input_mem = [file for file in os.listdir(TV) if "input_mem_" in file]
            #input_mem = list(filter(lambda x: x.endswith('.txt'), input_mem))
            vegetables = "_" + str(frm) + "_" + str(lcu) + ".txt"
            print(vegetables)
            input_mem = [inputmem_node for inputmem_node in input_mem if vegetables in inputmem_node]
            input_mem = [TV + "/" + item for item in input_mem]

            for file in input_mem:
                f_input_mem = open(file, 'r')
                first_line = f_input_mem.readline()
                first_line = first_line.split()
                if first_line[0] == "imgY_org_ap_V" or first_line[0] == "imgU_org_ap_V" or first_line[0] == "imgV_org_ap_V":
                    first_line[1] = "8"
                if "ctx_map" in first_line[0] and lcu == 0:
                    f_reg_config.write("Write_mem(" + first_line[0] + ", " + first_line[2] + ");\n")
                    '''
                    f_mem_config.write("Base:" + first_line[0] + " format:hex bits:" + first_line[1]\n)
                    for line in f_input_mem.readlines():
                        f_mem_config.write(line)
                    f_mem_config.write("#Next Batch\n")
                    '''
                elif "ctx_map" not in first_line[0]:
                    f_reg_config.write("Write_mem(" + first_line[0] + ", " + first_line[2] + ");\n")
                    '''
                    f_mem_config.write("Base:" + first_line[0] + " format:hex bits:" + first_line[1] + "\n")
                    for line in f_input_mem.readlines():
                        f_mem_config.write(line)
                    f_mem_config.write("#Next Batch\n")
                    '''
            #dcp cpr memory offset
            if lcu == 0 :
                f_reg_config.write("Write_reg(cpr_rfc_enable, 0x1);\n")
                f_reg_config.write("Write_reg(dcp_rfc_enable, 0x1);\n")
                f_reg_config.write("Write_reg(cpr_bit_switch, 0x0);\n")
                f_reg_config.write("Write_reg(dcp_bit_switch, 0x0);\n")

                if LIBPIC:
                    dcp_cpr_memory_offset_libpic(f_reg_config)
                else:
                    dcp_cpr_memory_offset(f_reg_config, frm)

            f_reg_config.write("Write_reg(sync_start, 0x01);\n\n")

            # read mem check
            output_mem = [file for file in os.listdir(TV) if "output_mem_" in file]
            vegetables = "_" + str(frm) + "_" + str(lcu) + ".txt"
            output_mem = [outputmem_node for outputmem_node in output_mem if vegetables in outputmem_node]
            print(output_mem)
            output_mem = [TV + "/" + item for item in output_mem]
            f_reg_config.write("Wait_irq_pos(1)\n")
            for file in output_mem:
                f_output_mem = open(file, 'r')
                first_line = f_output_mem.readline()
                first_line = first_line.split()
                f_reg_config.write("Read_mem_check(" + first_line[0] + ", " + first_line[2] + ");\n")
            f_reg_config.write("\n")

            lcu += 1
            
        #f_mem_config.close()
        f_reg_config.close()
        frm += 1

    

