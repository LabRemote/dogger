#

import time
import numpy
import shutil
import os
import sys
#import cv2
import ctypes

import gateway.device as dv
import gateway.runtime as rt
import gateway.metadata as md


class Task:


    def __init__(self):

        self.env = self.get_env()

        
    def get_env(self): 

        config = md.Configure(filepath = self.config_filepath, filename = self.config_filename)
        env = config.get()

        return env


        
class NidaqVoltageIn(Task):


    def __init__(self, sample_rate = 1, samplesPerChan = 1, subSamplesPerChan = 1, minValue = 0, maxValue = 10, IPNumber = "", moduleSlotNumber = 1, moduleChanRange = [0], uniqueChanIndexRange = [0]):

        self.nidaq = dv.NidaqVoltageIn(sample_rate, samplesPerChan, subSamplesPerChan, minValue, maxValue, IPNumber, moduleSlotNumber, moduleChanRange, uniqueChanIndexRange)


    def run(self):

        self.nidaq.InitAcquire()
        while True:
            if self.nidaq.globalErrorCode >= 0:
                self.nidaq.LoopAcquire()
                if self.nidaq.globalErrorCode < 0:
                    self.nidaq.StopAndClearTasks()
                    self.nidaq.InitAcquire()
            else:
                self.nidaq.StopAndClearTasks()
                self.nidaq.InitAcquire()
            time.sleep(10)

class NidaqCurrentIn(Task):


    def __init__(self, sample_rate = 1, samplesPerChan = 1, subSamplesPerChan = 1, minValue = 0, maxValue = 10, IPNumber = "", moduleSlotNumber = 1, moduleChanRange = [0], uniqueChanIndexRange = [0]):

        self.nidaq = daqc.device.NidaqVoltageIn(sample_rate, samplesPerChan, subSamplesPerChan, minValue, maxValue, IPNumber, moduleSlotNumber, moduleChanRange, uniqueChanIndexRange)


    def run(self):

        self.nidaq.InitAcquire()
        while True:
            if self.nidaq.globalErrorCode >= 0:
                self.nidaq.LoopAcquire()
                if self.nidaq.globalErrorCode < 0:
                    self.nidaq.StopAndClearTasks()
                    self.nidaq.InitAcquire()
            else:
                self.nidaq.StopAndClearTasks()
                self.nidaq.InitAcquire()
            time.sleep(10)
            
            
class USBCam(Task):
    

    def __init__(self, config_filepath = None, config_filename = None, channels = None, sample_rate = 1.0, start_delay = 0, video_unit = '/dev/video0', video_res = {800, 600}, video_rate = 10):

        self.config_filepath = config_filepath
        self.config_filename = config_filename
        self.channels = channels
        self.start_delay = start_delay
        self.sample_rate = sample_rate
        self.video_unit = video_unit
        self.video_res = video_res
        self.video_rate = video_rate

        (self.CHANNEL,) = self.channels
        self.capture_filename = 'image_' + str(self.CHANNEL) + '.jpg'
        
        Task.__init__(self)

        
    def read_samples(self):

        try:
            #camera.capture(capture_filename, format='jpeg', quality=10)
            os.system('fswebcam -d ' + self.video_unit + ' -r ' + str(self.video_res[0]) + 'x' + str(self.video_res[1]) + ' --fps ' + str(self.video_rate) + ' -S 1 --jpeg 95 --no-banner --save ' + self.capture_filename)
            #ret, frame = cam.read()
            #cv2.imwrite(capture_filename, frame)
        except PermissionError as e:
            print(e)

            
    def run(self):

        time.sleep(self.start_delay)

        count = 0
        divisor = numpy.int64(1/numpy.float64(self.sample_rate))
        current_time = numpy.float64(time.time())
        current_secs = numpy.int64(current_time)

        #cam = cv2.VideoCapture(-1)

        while True :

            sample_secs = current_secs + numpy.int64( divisor - current_secs % divisor )
            current_time = numpy.float64(time.time())
            current_secs = numpy.int64(current_time)
            if sample_secs > current_secs :
                time.sleep(0.1)
            else :
            
                self.read_samples()

                if self.env['STORE_PATH'] is not None and os.path.exists(self.env['STORE_PATH']):

                    store_filename = self.env['STORE_PATH'] + str(self.CHANNEL) + '_' + str(sample_secs) + '.jpg'
                    archive_filename = self.env['ARCHIVE_PATH'] + str(self.CHANNEL) + '_' + str(sample_secs) + '.jpg'
                    try:
                        shutil.copy(self.capture_filename, store_filename)
                        if self.env['ARCHIVE_PATH'] is not None and os.path.exists(self.env['ARCHIVE_PATH']):
                            pass
                            #shutil.copy(capture_filename, archive_filename)
                    except (FileNotFoundError, PermissionError) as e:
                        rt.logging.exception(e)
                    count = count+1

                    
                    
class AcquireCurrent(Task):

    """ Adapted from https://scipy-cookbook.readthedocs.io/items/Data_Acquisition_with_NIDAQmx.html."""

    
    def __init__(self, config_filepath = None, config_filename = None):


        self.config_filepath = config_filepath
        self.config_filename = config_filename

        Task.__init__(self)
        
        self.nidaq = None
        if sys.platform.startswith('win32') : 
            self.nidaq = ctypes.windll.nicaiu

        self.uInt8 = ctypes.c_ubyte
        self.int32 = ctypes.c_long
        self.uInt32 = ctypes.c_ulong
        self.uInt64 = ctypes.c_ulonglong
        self.float64 = ctypes.c_double
        self.bool32 = ctypes.c_bool
        self.TaskHandle = self.uInt32
        self.pointsWritten = self.uInt32()
        self.pointsRead = self.uInt32()
        self.null = ctypes.POINTER(ctypes.c_int)()
        self.value = self.uInt32()

        self.DAQmx_Val_Cfg_Default = self.int32(-1)
        self.DAQmx_Val_Auto = self.int32(-1)
        self.DAQmx_Val_Internal = self.int32(10200)
        self.DAQmx_Val_Volts = self.int32(10348)
        self.DAQmx_Val_Rising = self.int32(10280)
        self.DAQmx_Val_Falling = self.int32(10171)
        self.DAQmx_Val_CountUp = self.int32(10128)
        self.DAQmx_Val_FiniteSamps = self.int32(10178)
        self.DAQmx_Val_GroupByChannel = self.int32(0)
        self.DAQmx_Val_ChanForAllLines = self.int32(1)
        self.DAQmx_Val_RSE = self.int32(10083)
        self.DAQmx_Val_Diff = self.int32(10106)
        self.DAQmx_Val_Amps = self.int32(10342)
        self.DAQmx_Val_ContSamps = self.int32(10123)
        self.DAQmx_Val_GroupByScanNumber = self.int32(1)
        self.DAQmx_Val_Task_Reserve = self.int32(4)
        self.DAQmx_Val_ChanPerLine = self.int32(0)

        self.SAMPLE_RATE = 1000
        self.SAMPLES_PER_CHAN = 1000

        self.taskCurrent = self.TaskHandle(0)

        self.minCurrent = self.float64(-0.02)
        self.maxCurrent = self.float64(0.02)
        self.bufferSize = self.uInt32(self.SAMPLES_PER_CHAN)
        self.pointsToRead = self.bufferSize
        self.pointsRead = self.uInt32()
        self.sampleRate = self.float64(self.SAMPLE_RATE)
        self.samplesPerChan = self.uInt64(self.SAMPLES_PER_CHAN)
        self.clockSource = ctypes.create_string_buffer(b"OnboardClock")
        self.IPnumber2 = ctypes.create_string_buffer(b"169.254.254.253")
        self.defaultModuleName22 = ctypes.create_string_buffer(b"cDAQ9188-1AD0C2FMod2")
        self.timeout = self.float64(100.0)

        self.device2NameOut = ctypes.create_string_buffer(100)
        self.device2NameOutBufferSize = self.uInt32(100)
        self.device2ModuleNamesOut = ctypes.create_string_buffer(1000)
        self.device2ModuleNamesOutBufferSize = self.uInt32(1000)
        self.module21ChansOut = ctypes.create_string_buffer(2000)
        self.module21ChansOutBufferSize = self.uInt32(2000)
        self.module22ChansOut = ctypes.create_string_buffer(2000)
        self.module22ChansOutBufferSize = self.uInt32(2000)

        self.data = numpy.zeros((1000,),dtype=numpy.float64)

        self.global_error_code = 0


    def CHK(self, err):
        """a simple error checking routine"""
        global global_error_code
        global_error_code = err
        if err < 0:
            buf_size = 1000
            buf = ctypes.create_string_buffer(b"\000" * buf_size)
            self.nidaq.DAQmxGetErrorString(err,ctypes.byref(buf),buf_size)
            #raise RuntimeError('nidaq call failed with error %d: %s'%(err,repr(buf.value)))
            print('nidaq call failed with error %d: %s'%(err,repr(buf.value)))


    def scale_cond_transmitter(self, I_cond):
        #return I_cond
        return ( I_cond * 1000.0 - 4.0 ) / 16.0 * 10e-6

    def scale_Opto_22_AD3_SATT_ETT45_0101(self, I_temp):
        return ( I_temp * 1000.0 - 4.0 ) / 16.0 * 50.0

    def downsample(self, y, size):
        y_reshape = y.reshape(size, int(len(y)/size))
        y_downsamp = y_reshape.mean(axis=1)
        return y_downsamp

    # Create Task and Voltage Channel and Configure Sample Clock
    def SetupTasks(self):
        self.device2NameOut = b"cDAQ9188-1AD0C2F"

        self.CHK( self.nidaq.DAQmxGetDevChassisModuleDevNames(self.device2NameOut, self.device2ModuleNamesOut, self.device2ModuleNamesOutBufferSize) )
        print("device2ModuleNamesOut: ", repr(self.device2ModuleNamesOut.value))
        self.CHK( self.nidaq.DAQmxGetDevAIPhysicalChans(self.defaultModuleName22, self.module22ChansOut, 2000) )
        print("module22ChansOut: ", repr(self.module22ChansOut.value))
        self.CHK(self.nidaq.DAQmxCreateTask("",ctypes.byref(self.taskCurrent)))
        self.CHK(self.nidaq.DAQmxCreateAICurrentChan(self.taskCurrent,self.module22ChansOut,"",self.DAQmx_Val_RSE,self.minCurrent,self.maxCurrent,self.DAQmx_Val_Amps,self.DAQmx_Val_Internal,None,None))
        self.CHK(self.nidaq.DAQmxCfgSampClkTiming(self.taskCurrent, self.clockSource, self.sampleRate, self.DAQmx_Val_Rising, self.DAQmx_Val_ContSamps, self.samplesPerChan))
        #CHK(nidaq.DAQmxCfgInputBuffer(taskCurrent,200000))


    def ReserveTasks(self):
        self.CHK(self.nidaq.DAQmxTaskControl(self.taskCurrent, self.DAQmx_Val_Task_Reserve))

    def StartTasks(self):
        self.CHK(self.nidaq.DAQmxStartTask(self.taskCurrent))

    def ReadCurrent(self):
        self.pointsToRead = self.bufferSize
        self.data = numpy.zeros((16*self.bufferSize.value,),dtype=numpy.float64)
        if global_error_code >= 0:
            self.CHK(self.nidaq.DAQmxReadAnalogF64(self.taskCurrent,self.pointsToRead,self.timeout,self.DAQmx_Val_GroupByChannel,self.data.ctypes.data,self.uInt32(16*self.bufferSize.value),ctypes.byref(self.pointsRead),None))
        return self.data

    def StopAndClearTasks(self):
        if self.taskCurrent.value != 0:
            self.CHK( self.nidaq.DAQmxStopTask(self.taskCurrent) )
            self.CHK( self.nidaq.DAQmxClearTask(self.taskCurrent) )

    def InitAcquire(self):
        self.SetupTasks()
        self.ReserveTasks()
        self.StartTasks()


    def LoopAcquire(self):

        while (global_error_code >= 0):

            current = 0.0
            try:
                current = self.ReadCurrent()
            except OSError as e:
                print(e)

            if self.env['STORE_PATH'] is not None and os.path.exists(self.env['STORE_PATH']):

                acq_finish_time = numpy.float64(time.time())
                acq_finish_secs = numpy.int64(acq_finish_time)
                acq_finish_microsecs = numpy.int64(acq_finish_time * 1e6)
                acq_microsec_part = acq_finish_microsecs - numpy.int64(acq_finish_secs)*1e6
                if acq_microsec_part > 990000 :
                    time.sleep(0.03)
                if acq_microsec_part < 10000 :
                    time.sleep(0.87)

                for channel_index in range(0, 16):
                    current_array = current[self.SAMPLES_PER_CHAN*(channel_index+0):self.SAMPLES_PER_CHAN*(channel_index+1)]
                    if channel_index == 0 : current_array = self.scale_cond_transmitter(current_array)
                    if channel_index == 1 : current_array = self.scale_Opto_22_AD3_SATT_ETT45_0101(current_array)
                    current_avg = self.downsample(current_array, 1)
                    current_array = numpy.concatenate(([0.0], acq_microsec_part, current_array), axis=None)
                    current_array[0] = current_avg
                    try:
                        filename_current = repr(97+channel_index) + "_" + repr(acq_finish_secs)
                        numpy.save(self.env['STORE_PATH']+filename_current, current_array)
                    except PermissionError as e:
                        print(e)


    def run(self):

        self.InitAcquire()
        while True:
            if global_error_code >= 0:
                self.LoopAcquire()
                if global_error_code < 0:
                    self.StopAndClearTasks()
                    self.InitAcquire()
            else:
                self.StopAndClearTasks()
                self.InitAcquire()
            time.sleep(10)


            
class AcquireMaster:


    def __init__(self):
        pass

        
class AcquireVoltage:

    def __init__(self):
        pass
