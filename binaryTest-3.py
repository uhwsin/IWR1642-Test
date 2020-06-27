import struct
import os

#FileName = "xwr16xx_processed_stream_2020_06_23T14_48_29_159.dat"
FileName = "xwr16xx_processed_stream_2020_06_26T08_39_03_999.dat"
pkt_length = 224
CurrFilePtr = 0
#----------------------------------header---------------------------------
magicWord_Size = 2*4
version_size = 4
totalPacketLen_size = 4
platform_size = 4
frameNumber_size = 4
timeCpuCycles_size = 4
numDetectedObj_size = 4
numTLVs_size = 4
subFrameNumber_size = 4
Header_TotalSize =  magicWord_Size +\
                    version_size +\
                    totalPacketLen_size +\
                    platform_size + \
                    frameNumber_size + \
                    timeCpuCycles_size + \
                    numDetectedObj_size + \
                    numTLVs_size + \
                    subFrameNumber_size
#----------------------------------headerData---------------------------------
frameNumber  =0
numDetectedObj = 0
numTLVs  = 0
totalPacketLen = 0
#----------------------------------Tlv MmwDemo_output_message_tl_t---------------------------------
MmwDemo_outputTl_typeSize = 4
MmwDemo_outputTl_lengthSize = 4
# MmwDemo_outputTl_type = 0
# MmwDemo_outputTl_length = 0
MmwDemo_outputTl_TotalSize = MmwDemo_outputTl_typeSize + MmwDemo_outputTl_lengthSize

#----------------------------------Tlv DPIF_PointCloudCartesian
f_x_size = f_y_size = f_z_size = f_veloc_size = 4
f_x = 0.0
f_y = 0.0
f_z = 0.0
f_veloc = 0.0
DPIF_PointCloudCartesian_size = f_x_size + f_y_size + f_z_size + f_veloc_size
#----------------------------------Tlv DPIF_PointCloudSideInfo
snr_size = noise_size = 2
DPIF_PointCloudSideInfo_Size = snr_size + noise_size
#
# print("File Name :" + FileName)
# print("header size: " + str(Header_TotalSize) + "\n")
def GetFileSize(InputFileName):
  with open(InputFileName, "rb") as f: 
    f.seek(0,2)
    result = f.tell()
    #print("filesize: "+ str(result) )   
  return result

def Read_Header(InputFileName,inputFilePtr):
  global totalPacketLen
  global numDetectedObj
  global numTLVs
  
  #print("Read_Header :  " + InputFileName)
  #print("header size: " + str(Header_TotalSize) + "\n")  
  with open(InputFileName, "rb") as f:
    f.seek(inputFilePtr,0)
    byteString = f.read(40)
    fmt = "<4HIIIIIIII"
    header_tuple = struct.unpack_from(fmt, byteString[0:40])
    totalPacketLen = header_tuple[5]
    frameNumber =   header_tuple[7]
    numDetectedObj  =   header_tuple[9]
    numTLVs =   header_tuple[10]
    
    print("Frame Num : " + str(frameNumber) + " DetectedObjs : " + str(numDetectedObj) + " numTLVs: " + str(numTLVs))
    print("totalPacketLen : " + str(totalPacketLen))
    return Header_TotalSize


def Read_Tlv(InputFileName,FilePtr,ptk_size):
    global numTLVs
    resultSize = 0
    TempFilePtr = FilePtr
    ptk_size = ptk_size - 40 #header
    
    tempTlvNum = numTLVs

    with open(InputFileName, "rb") as f:
        # print("Read_Tlv  TempFilePtr: " + str(TempFilePtr) +" Read_size " +str(Read_size)+" tempTlvNum  "+ str(tempTlvNum))
        f.seek(TempFilePtr,0)
        
        byteArray = f.read(ptk_size)
        Read_size = len(byteArray)
        tempList1 = []
        tempList2 = []
        tempList3 = []
        while Read_size > 0 and tempTlvNum > 0:              
            fmt='<II'
            tlv_type, tlv_len =  struct.unpack_from(fmt,byteArray[0:8]) 
            byteArray = byteArray[8:]
            Read_size -= 8 #MmwDemo_outputTl_TotalSize
            
            print("Read_Tlv " + str(Read_size)+" tlv_type " + str(tlv_type)+" tlv_len "+str(tlv_len))  
            if(tlv_type == 1):
                for x in range( 0 , numDetectedObj ) :
                    fmt='<ffff'
                    l = struct.calcsize(fmt)
                    # DPIF_PointCloudCartesianData = struct.unpack(fmt,byteString[0:l])
                    DPIF_PointCloudCartesianData = struct.unpack_from(fmt,byteArray[0:l])
                    tempList1.append ( list(DPIF_PointCloudCartesianData))#list( struct.unpack('<ffff',byteString)) )
                    byteArray = byteArray[l:]
                            
            elif(tlv_type == 7):
                for x in range( 0 , numDetectedObj ):
                    fmt='<hh'
                    l = struct.calcsize(fmt)
                    # DPIF_PointCloudSideInfoData = struct.unpack(fmt,byteString[0:l])
                    DPIF_PointCloudSideInfoData = struct.unpack_from(fmt,byteArray[0:l])
                    tempList2.append ( list(DPIF_PointCloudSideInfoData))#list( struct.unpack('<ffff',byteString)) )
                    byteArray = byteArray[l:]
            else:
                byteArray = byteArray[tlv_len:] 
            Read_size -= tlv_len
            tempTlvNum -= 1

        for j in range( 0 , numDetectedObj ):
            tempList3.append([tempList1[j],tempList2[j]])     
        for j in tempList3:
            print(j)


      
    return resultSize


TotalPtr = 0
TotalSize = GetFileSize(FileName)
print("filesize: "+ str(TotalSize) )  



while TotalPtr < TotalSize:
#print("0.CurrFilePtr "+str(CurrFilePtr) + " pkt_length "+str(TotalPtr) + " totalPacketLen "+str(totalPacketLen)  )
    CurrFilePtr = TotalPtr
    resultSize = Read_Header(FileName,CurrFilePtr)
    CurrFilePtr += 40
    pkt_length -= resultSize
    #print("1.CurrFilePtr "+str(CurrFilePtr) + " pkt_length "+str(TotalPtr) + " totalPacketLen "+str(totalPacketLen)  )
    CurrFilePtr += Read_Tlv(FileName,CurrFilePtr,totalPacketLen)
    TotalPtr += totalPacketLen
    # os.system("pause")
