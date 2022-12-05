using System;
using System.Windows.Forms;
using FUTEK_USB_DLL;

namespace USBExample
{

    public partial class FormMain : Form
    {

        public FUTEK_USB_DLL.USB_DLL oFUTEKUSBDLL;

        public string SerialNumber;
        public string DeviceHandle;
        public string Temp;

        public Int32 OffsetValue;
        public Int32 FullscaleValue;

        public Int32 FullScaleLoad;
        public Int32 DecimalPoint;
        public Int32 UnitCode;
        public double Tare;

        public Int32 NormalData;
        public double CalculatedReading;

        public Boolean OpenedConnection;


        public FormMain()
        {
            InitializeComponent();
        }

        private void FormMain_Load(object sender, EventArgs e)
        {
            oFUTEKUSBDLL = new FUTEK_USB_DLL.USB_DLL();

            Text = "Microsoft Visual C# Example Using FUTEK USB DLL " + 
                   System.Reflection.Assembly.GetAssembly(typeof(FUTEK_USB_DLL.USB_DLL)).GetName().Version.ToString();

            SerialNumber = "";
            TextBoxSerialNumber.Text = "Enter Here";

            DeviceHandle = "0";
            OffsetValue = 0;
            FullscaleValue = 0;
            FullScaleLoad = 0;
            DecimalPoint = 0;
            UnitCode = 0;
            Tare = 0;

            NormalData = 0;
            CalculatedReading = 0;

            OpenedConnection = false;
        }

        private void FormMain_Disposed(object sender, EventArgs e)
        {

            TimerReading.Enabled = false;

            if (OpenedConnection == true) { }
            else
            { return; }

            oFUTEKUSBDLL.Close_Device_Connection(DeviceHandle);
            if (oFUTEKUSBDLL.DeviceStatus == "0") { }
            else
            {
                MessageBox.Show("Device Error " + oFUTEKUSBDLL.DeviceStatus);
                return;
            }

            OpenedConnection = false;
        }

        /// <summary>
        /// The function checks the object whether it contains all numeric or not
        /// </summary>
        /// <param name="Expression"></param>
        /// <returns>System.Boolean</returns>
        public static System.Boolean IsNumeric(System.Object expression)
        {
            if (expression == null || expression is DateTime)
                return false;

            if (expression is Int16 || expression is Int32 || expression is Int64 || expression is Decimal || expression is Single || expression is Double || expression is Boolean)
                return true;

            try
            {
                if (expression is string)
                    Double.Parse(expression as string);
                else
                    Double.Parse(expression.ToString());
                return true;
            }
            catch { } // just dismiss errors but return false
            return false;
        }

        private void ButtonStart_Click(object sender, EventArgs e)
        {
            SerialNumber = TextBoxSerialNumber.Text;

            if (OpenedConnection == false) { }
            else
            { return; }

            oFUTEKUSBDLL.Open_Device_Connection(SerialNumber);

            if (oFUTEKUSBDLL.DeviceStatus == "0") { }
            else
            {
                MessageBox.Show("Device Error " + oFUTEKUSBDLL.DeviceStatus);
                return;
            }

            DeviceHandle = oFUTEKUSBDLL.DeviceHandle;

            OpenedConnection = true;

            GetOffsetValue();
            GetFullscaleValue();
            GetFullscaleLoad();
            GetDecimalPoint();
            GetUnitCode();
            FindUnits();

            TimerReading.Interval = 500;
            TimerReading.Enabled = true;
        }

        private void ButtonStop_Click(object sender, EventArgs e)
        {
            TimerReading.Enabled = false;

            if (OpenedConnection == true) { }
            else
            { return; }

            oFUTEKUSBDLL.Close_Device_Connection(DeviceHandle);
            if (oFUTEKUSBDLL.DeviceStatus == "0") { }
            else
            {
                MessageBox.Show("Device Error " + oFUTEKUSBDLL.DeviceStatus);
                return;
            }

            OpenedConnection = false;
            Tare = 0;
        }

        private void ButtonTare_Click(object sender, EventArgs e)
        {
            Tare = CalculatedReading;
        }

        private void ButtonGross_Click(object sender, EventArgs e)
        {
            Tare = 0;
        }

        /// <summary>
        /// Gets the offset value by using the FUTEK DLL Method and
        /// check if it's numeric and then parse it into integer
        /// then store it into the memory
        /// </summary>
        private void GetOffsetValue()
        {
            do
            {
                Temp = oFUTEKUSBDLL.Get_Offset_Value(DeviceHandle);
            } while (IsNumeric(Temp) == false);

            try {
                OffsetValue = Int32.Parse(Temp);
            } catch { }
        }

        /// <summary>
        /// Gets the fullscale value by using the FUTEK DLL Method and
        /// check if it's numeric and then parse it into integer
        /// then store it into the memory
        /// </summary>
        private void GetFullscaleValue()
        {
            do
            {
                Temp = oFUTEKUSBDLL.Get_Fullscale_Value(DeviceHandle);
            } while (IsNumeric(Temp) == false);

            try {
                FullscaleValue = Int32.Parse(Temp);
            } catch { }
        }

        /// <summary>
        /// Gets the fullscale load by using the FUTEK DLL Method and
        /// check if it's numeric and then parse it into integer
        /// then store it into the memory
        /// </summary>
        private void GetFullscaleLoad()
        {
            do
            {
                Temp = oFUTEKUSBDLL.Get_Fullscale_Load(DeviceHandle);
            } while (IsNumeric(Temp) == false);

            try {
                FullScaleLoad = Int32.Parse(Temp);
            } catch { }
        }

        /// <summary>
        /// Gets the number of decimal places by using the FUTEK 
        /// DLL Method and check if it's numeric and then parse
        /// it into integer then store it into the memory
        /// </summary>
        private void GetDecimalPoint()
        {
            do
            {
                Temp = oFUTEKUSBDLL.Get_Decimal_Point(DeviceHandle);
            } while (IsNumeric(Temp) == false);
            try {
                DecimalPoint = Int32.Parse(Temp);
            } catch { }
            if (DecimalPoint > 3)
            { DecimalPoint = 0; }
        }

        /// <summary>
        /// Gets the unit code to later find unit needed for the device
        /// by using the FUTEK DLL Method and check if it's numeric and
        /// then parse it into integer and then store it into the memory
        /// </summary>
        private void GetUnitCode()
        {
            do
            {
                Temp = oFUTEKUSBDLL.Get_Unit_Code(DeviceHandle);
            } while (IsNumeric(Temp) == false);

            try {
                UnitCode = Int32.Parse(Temp);
            } catch { }
        }

        /// <summary>
        /// Uses the UnitCode from the memory to find the correct
        /// unit for the device
        /// </summary>
        /// <remarks>
        /// For more information about unit code visit:
        /// http://www.futek.com/files/docs/API/FUTEK_USB_DLL/webframe.html#UnitCodes.html
        /// </remarks>
        private void FindUnits()
        {
            switch (UnitCode)
            {
                case 0:
                    TextBoxUnits.Text = "atm";
                    break;
                case 1:
                    TextBoxUnits.Text = "bar";
                    break;
                case 2:
                    TextBoxUnits.Text = "dyn";
                    break;
                case 3:
                    TextBoxUnits.Text = "ft-H2O";
                    break;
                case 4:
                    TextBoxUnits.Text = "ft-lb";
                    break;
                case 5:
                    TextBoxUnits.Text = "g";
                    break;
                case 6:
                    TextBoxUnits.Text = "g-cm";
                    break;
                case 7:
                    TextBoxUnits.Text = "g-mm";
                    break;
                case 8:
                    TextBoxUnits.Text = "in-H2O";
                    break;
                case 9:
                    TextBoxUnits.Text = "in-lb";
                    break;
                case 10:
                    TextBoxUnits.Text = "in-oz";
                    break;
                case 11:
                    TextBoxUnits.Text = "kdyn";
                    break;
                case 12:
                    TextBoxUnits.Text = "kg";
                    break;
                case 13:
                    TextBoxUnits.Text = "kg-cm";
                    break;
                case 14:
                    TextBoxUnits.Text = "kg/cm2";
                    break;
                case 15:
                    TextBoxUnits.Text = "kg-m";
                    break;
                case 16:
                    TextBoxUnits.Text = "klbs";
                    break;
                case 17:
                    TextBoxUnits.Text = "kN";
                    break;
                case 18:
                    TextBoxUnits.Text = "kPa";
                    break;
                case 19:
                    TextBoxUnits.Text = "kpsi";
                    break;
                case 20:
                    TextBoxUnits.Text = "lbs";
                    break;
                case 21:
                    TextBoxUnits.Text = "Mdyn";
                    break;
                case 22:
                    TextBoxUnits.Text = "mmHG";
                    break;
                case 23:
                    TextBoxUnits.Text = "mN-m";
                    break;
                case 24:
                    TextBoxUnits.Text = "MPa";
                    break;
                case 25:
                    TextBoxUnits.Text = "MT";
                    break;
                case 26:
                    TextBoxUnits.Text = "N";
                    break;
                case 27:
                    TextBoxUnits.Text = "N-cm";
                    break;
                case 28:
                    TextBoxUnits.Text = "N-m";
                    break;
                case 29:
                    TextBoxUnits.Text = "N-mm";
                    break;
                case 30:
                    TextBoxUnits.Text = "oz";
                    break;
                case 31:
                    TextBoxUnits.Text = "psi";
                    break;
                case 32:
                    TextBoxUnits.Text = "Pa";
                    break;
                case 33:
                    TextBoxUnits.Text = "T";
                    break;
                case 34:
                    TextBoxUnits.Text = "mV/V";
                    break;
                case 35:
                    TextBoxUnits.Text = "µA";
                    break;
                case 36:
                    TextBoxUnits.Text = "mA";
                    break;
                case 37:
                    TextBoxUnits.Text = "A";
                    break;
                case 38:
                    TextBoxUnits.Text = "mm";
                    break;
                case 39:
                    TextBoxUnits.Text = "cm";
                    break;
                case 40:
                    TextBoxUnits.Text = "dm";
                    break;
                case 41:
                    TextBoxUnits.Text = "m";
                    break;
                case 42:
                    TextBoxUnits.Text = "km";
                    break;
                case 43:
                    TextBoxUnits.Text = "in";
                    break;
                case 44:
                    TextBoxUnits.Text = "ft";
                    break;
                case 45:
                    TextBoxUnits.Text = "yd";
                    break;
                case 46:
                    TextBoxUnits.Text = "mi";
                    break;
                case 47:
                    TextBoxUnits.Text = "µg";
                    break;
                case 48:
                    TextBoxUnits.Text = "mg";
                    break;
                case 49:
                    TextBoxUnits.Text = "LT";
                    break;
                case 50:
                    TextBoxUnits.Text = "mbar";
                    break;
                case 51:
                    TextBoxUnits.Text = "˚C";
                    break;
                case 52:
                    TextBoxUnits.Text = "˚F";
                    break;
                case 53:
                    TextBoxUnits.Text = "K";
                    break;
                case 54:
                    TextBoxUnits.Text = "˚Ra";
                    break;
                case 55:
                    TextBoxUnits.Text = "kN-m";
                    break;
                case 56:
                    TextBoxUnits.Text = "g-m";
                    break;
                case 57:
                    TextBoxUnits.Text = "nV";
                    break;
                case 58:
                    TextBoxUnits.Text = "µV";
                    break;
                case 59:
                    TextBoxUnits.Text = "mV";
                    break;
                case 60:
                    TextBoxUnits.Text = "V";
                    break;
                case 61:
                    TextBoxUnits.Text = "kV";
                    break;
                case 62:
                    TextBoxUnits.Text = "NONE";
                    break;
                default:
                    TextBoxUnits.Text = "Undefined";
                    break;
            }
        }

        private void TimerReading_Tick(object sender, EventArgs e)
        {
            do
            {
                Temp = oFUTEKUSBDLL.Normal_Data_Request(DeviceHandle);
            } while (IsNumeric(Temp) == false);

            try {
                NormalData = Int32.Parse(Temp);
            }catch {}

            CalculatedReading = (double)(NormalData - OffsetValue) / (FullscaleValue - OffsetValue) * FullScaleLoad / Math.Pow(10, DecimalPoint);
            TextBoxCalculatedReading.Text = String.Format("{0:0.000}", (CalculatedReading - Tare));
        }
    }
}
