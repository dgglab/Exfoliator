import wpf
import clr
import System
clr.AddReference("FUTEK USB DLL")
clr.AddReferenceByPartialName("IronPython")
import FUTEK_USB_DLL
from FUTEK_USB_DLL import USB_DLL
from System.Windows import Application, Window
from IronPython.Compiler import CallTarget0

class MyWindow(Window):
    def __init__(self):
        wpf.LoadComponent(self, 'USB_Example_Python.xaml')
        self.Title = "IronPython Example Using FUTEK USB DLL " + System.Reflection.Assembly.GetAssembly(type(FUTEK_USB_DLL.USB_DLL)).GetName().Version.ToString()
        self.oFUTEKUSBDLL = FUTEK_USB_DLL.USB_DLL()
        self.SerialNumber = ""
        self.DeviceHandle = ""
        self.Temp = ""
        self.OffsetValue = 0
        self.FullscaleValue = 0
        self.FullScaleLoad = 0
        self.DecimalPoint = 0
        self.UnitCode = 0
        self.Tare = 0.0
        self.NormalData = 0
        self.CalculatedReading = 0.0
        self.OpenedConnection = False
        self.dispatcherTimer = System.Windows.Threading.DispatcherTimer()
        return
        
    def StartButton_Click(self, sender, e):
        self.SerialNumber = self.SerialNumberTextBox.Text

        if self.OpenedConnection == True:
            return
 
        self.oFUTEKUSBDLL.Open_Device_Connection(self.SerialNumberTextBox.Text)

        if self.oFUTEKUSBDLL.DeviceStatus == "0":
            pass
        else:
            System.Windows.MessageBox.Show("Device Error " + self.oFUTEKUSBDLL.DeviceStatus)
            return
        
        self.DeviceHandle = self.oFUTEKUSBDLL.DeviceHandle

        self.OpenedConnection = True

        self.GetOffsetValue()
        self.GetFullscaleValue()
        self.GetFullscaleLoad()
        self.GetDecimalPoint()
        self.GetUnitCode()
        self.FindUnits()

        self.dispatcherTimer.Interval = System.TimeSpan(0,0,0,0,100)
        self.dispatcherTimer.Tick += self.dispatcherTimer_Tick
        self.dispatcherTimer.Start()
        return
    
    def StopButton_Click(self, sender, e):
        self.dispatcherTimer.Stop()
        if self.OpenedConnection:
            pass
        else:
            return

        self.oFUTEKUSBDLL.Close_Device_Connection(self.DeviceHandle)
        if self.oFUTEKUSBDLL.DeviceStatus == "0":
            pass
        else:
            System.Windows.MessageBox.Show("Device Error " + self.oFUTEKUSBDLL.DeviceStatus)
            return

        self.OpenedConnection = False
        self.Tare = 0
        return
    
    def TareButton_Click(self, sender, e):
        self.Tare = self.CalculatedReading
        return
    
    def GrossButton_Click(self, sender, e):
        self.Tare = 0
        return

        # <summary>
        # Gets the offset value by using the FUTEK DLL Method and
        # check if it's numeric and then parse it into integer
        # then store it into the memory
        # </summary>    
    def GetOffsetValue(self):
        while True:
            self.Temp = self.oFUTEKUSBDLL.Get_Offset_Value(self.DeviceHandle)
            if self.Temp.isnumeric():
                break
        self.OffsetValue = int(self.Temp)
        return

        # <summary>
        # Gets the fullscale value by using the FUTEK DLL Method and
        # check if it's numeric and then parse it into integer
        # then store it into the memory
        # </summary>
    def GetFullscaleValue(self):
        while True:
            self.Temp = self.oFUTEKUSBDLL.Get_Fullscale_Value(self.DeviceHandle)
            if self.Temp.isnumeric():
                break
        self.FullscaleValue = int(self.Temp)
        return

        # <summary>
        # Gets the fullscale load by using the FUTEK DLL Method and
        # check if it's numeric and then parse it into integer
        # then store it into the memory
        # </summary>
    def GetFullscaleLoad(self):
        while True:
            self.Temp = self.oFUTEKUSBDLL.Get_Fullscale_Load(self.DeviceHandle)
            if self.Temp.isnumeric():
                break
        self.FullScaleLoad = int(self.Temp)
        return

        # <summary>
        # Gets the number of decimal places by using the FUTEK 
        # DLL Method and check if it's numeric and then parse
        # it into integer then store it into the memory
        # </summary>
    def GetDecimalPoint(self):
        while True:
            self.Temp = self.oFUTEKUSBDLL.Get_Decimal_Point(self.DeviceHandle)
            if self.Temp.isnumeric():
                break
        self.DecimalPoint = int(self.Temp)
        if self.DecimalPoint > 3:
            self.DecimalPoint = 0
        return

        # <summary>
        # Gets the unit code to later find unit needed for the device
        # by using the FUTEK DLL Method and check if it's numeric and
        # then parse it into integer and then store it into the memory
        # </summary>
    def GetUnitCode(self):
        while True:
            self.Temp = self.oFUTEKUSBDLL.Get_Unit_Code(self.DeviceHandle)
            if self.Temp.isnumeric():
                break
        self.UnitCode = int(self.Temp)
        return

        # <summary>
        # Uses the UnitCode from the memory to find the correct
        # unit for the device
        # </summary>
        # <remarks>
        # For more information about unit code visit:
        # http://www.futek.com/files/docs/API/FUTEK_USB_DLL/webframe.html#UnitCodes.html
        # </remarks>
    def FindUnits(self):
        units = {
            0 : "atm", 1 : "bar", 2 : "dyn", 3 : "ft-H20", 4 : "ft-lb", 5 : "g", 6 : "g-cm", 7 : "g-mm", 8 : "in-H20", 9 : "in-lb",
            10 : "in-oz", 11 : "kdyn", 12 : "kg", 13 : "kg-cm", 14 : "kg/cm2", 15 : "kg-m", 16 : "klbs", 17 : "kN", 18 : "kPa", 19 : "kpsi",
            20 : "lbs", 21 : "Mdyn", 22 : "mmHG", 23 : "mN-m", 24 : "MPa", 25 : "MT", 26 : "N", 27 : "N-cm", 28 : "N-m", 29 : "N-mm",
            30 : "oz", 31 : "psi", 32 : "Pa", 33 : "T", 34 : "mV/V", 35 : "µA", 36 : "mA", 37 : "A", 38 : "mm", 39 : "cm",
            40 : "dm", 41 : "m", 42 : "km", 43 : "in", 44 : "ft", 45 : "yd", 46 : "mi", 47 : "µg", 48 : "mg", 49 : "LT",
            50 : "mbar", 51 : "˚C", 52 : "˚F", 53 : "K", 54 : "˚Ra", 55 : "kN-m", 56 : "g-m", 57 : "nV", 58 : "µV", 59 : "mV",
            60 : "V", 61 : "kV", 62 : "NONE"
            }
        self.UnitsTextBox.Text = units.get(self.UnitCode, "Undefined")
        return

    def dispatcherTimer_Tick(self, sender, e):
        if self.OpenedConnection:
            while True:
                self.Temp = self.oFUTEKUSBDLL.Normal_Data_Request(self.DeviceHandle)
                if self.Temp.isnumeric():
                    break
            self.NormalData = int(self.Temp)
            self.CalculatedReading = self.NormalData - self.OffsetValue
            self.CalculatedReading /= float(self.FullscaleValue - self.OffsetValue) 
            self.CalculatedReading *= self.FullScaleLoad 
            self.CalculatedReading /= float(pow(10, self.DecimalPoint))
            self.CalculatedReadingTextBox.Text = "{0:.3f}".format(self.CalculatedReading - self.Tare)
        return

if __name__ == '__main__':
    Application().Run(MyWindow())
