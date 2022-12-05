#pragma once
#include <cctype>
#include <typeinfo>
namespace USBExample {
	using namespace System;
	using namespace System::ComponentModel;
	using namespace System::Collections;
	using namespace System::Windows::Forms;
	using namespace System::Data;
	using namespace System::Drawing;
	using namespace FUTEK_USB_DLL;

	public ref class MyForm : public System::Windows::Forms::Form
	{
	public:
		MyForm(void)
		{
			InitializeComponent();
		}

	protected:
		/// <summary>
		/// Clean up any resources being used.
		/// </summary>
		~MyForm()
		{
			delete SerialNumber;
			delete DeviceHandle;
			delete Temp;
			if (components)
			{
				delete components;
			}
		}
	internal: System::Windows::Forms::Button^  ButtonGross;
	protected:
	internal: System::Windows::Forms::Button^  ButtonTare;
	internal: System::Windows::Forms::Button^  ButtonStop;
	internal: System::Windows::Forms::Button^  ButtonStart;
	internal: System::Windows::Forms::TextBox^  TextBoxUnits;
	internal: System::Windows::Forms::TextBox^  TextBoxCalculatedReading;
	internal: System::Windows::Forms::TextBox^  TextBoxSerialNumber;
	internal: System::Windows::Forms::Label^  LabelUnits;
	internal: System::Windows::Forms::Label^  LabelCalculatedReading;
	internal: System::Windows::Forms::Label^  LabelSerialNumber;
	private: System::Windows::Forms::Timer^  TimerReading;
	internal:
	private: System::ComponentModel::IContainer^  components;

	private:
		USB_DLL oFutekUSBDLL;
		String ^ SerialNumber,
			^ DeviceHandle,
			^ Temp;

		Int32 OffsetValue,
			FullscaleValue;

		Int32 FullScaleLoad,
			DecimalPoint,
			UnitCode;
		double Tare;

		Int32 NormalData;
		double CalculatedReading;

		bool OpenedConnection;

#pragma region Windows Form Designer generated code
		/// <summary>
		/// Required method for Designer support - do not modify
		/// the contents of this method with the code editor.
		/// </summary>
		void InitializeComponent(void)
		{
			this->components = (gcnew System::ComponentModel::Container());
			this->ButtonGross = (gcnew System::Windows::Forms::Button());
			this->ButtonTare = (gcnew System::Windows::Forms::Button());
			this->ButtonStop = (gcnew System::Windows::Forms::Button());
			this->ButtonStart = (gcnew System::Windows::Forms::Button());
			this->TextBoxUnits = (gcnew System::Windows::Forms::TextBox());
			this->TextBoxCalculatedReading = (gcnew System::Windows::Forms::TextBox());
			this->TextBoxSerialNumber = (gcnew System::Windows::Forms::TextBox());
			this->LabelUnits = (gcnew System::Windows::Forms::Label());
			this->LabelCalculatedReading = (gcnew System::Windows::Forms::Label());
			this->LabelSerialNumber = (gcnew System::Windows::Forms::Label());
			this->TimerReading = (gcnew System::Windows::Forms::Timer(this->components));
			this->SuspendLayout();
			// 
			// ButtonGross
			// 
			this->ButtonGross->Location = System::Drawing::Point(610, 29);
			this->ButtonGross->Name = L"ButtonGross";
			this->ButtonGross->Size = System::Drawing::Size(58, 23);
			this->ButtonGross->TabIndex = 46;
			this->ButtonGross->Text = L"Gross";
			this->ButtonGross->UseVisualStyleBackColor = true;
			this->ButtonGross->Click += gcnew System::EventHandler(this, &MyForm::ButtonGross_Click);
			// 
			// ButtonTare
			// 
			this->ButtonTare->Location = System::Drawing::Point(548, 29);
			this->ButtonTare->Name = L"ButtonTare";
			this->ButtonTare->Size = System::Drawing::Size(58, 23);
			this->ButtonTare->TabIndex = 45;
			this->ButtonTare->Text = L"Tare";
			this->ButtonTare->UseVisualStyleBackColor = true;
			this->ButtonTare->Click += gcnew System::EventHandler(this, &MyForm::ButtonTare_Click);
			// 
			// ButtonStop
			// 
			this->ButtonStop->Location = System::Drawing::Point(486, 29);
			this->ButtonStop->Name = L"ButtonStop";
			this->ButtonStop->Size = System::Drawing::Size(58, 23);
			this->ButtonStop->TabIndex = 44;
			this->ButtonStop->Text = L"Stop";
			this->ButtonStop->UseVisualStyleBackColor = true;
			this->ButtonStop->Click += gcnew System::EventHandler(this, &MyForm::ButtonStop_Click);
			// 
			// ButtonStart
			// 
			this->ButtonStart->Location = System::Drawing::Point(424, 29);
			this->ButtonStart->Name = L"ButtonStart";
			this->ButtonStart->Size = System::Drawing::Size(58, 23);
			this->ButtonStart->TabIndex = 43;
			this->ButtonStart->Text = L"Start";
			this->ButtonStart->UseVisualStyleBackColor = true;
			this->ButtonStart->Click += gcnew System::EventHandler(this, &MyForm::ButtonStart_Click);
			// 
			// TextBoxUnits
			// 
			this->TextBoxUnits->BackColor = System::Drawing::SystemColors::ButtonShadow;
			this->TextBoxUnits->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 9.75F, System::Drawing::FontStyle::Bold, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->TextBoxUnits->Location = System::Drawing::Point(300, 29);
			this->TextBoxUnits->Name = L"TextBoxUnits";
			this->TextBoxUnits->ReadOnly = true;
			this->TextBoxUnits->Size = System::Drawing::Size(120, 22);
			this->TextBoxUnits->TabIndex = 42;
			this->TextBoxUnits->Text = L"Units";
			this->TextBoxUnits->TextAlign = System::Windows::Forms::HorizontalAlignment::Center;
			// 
			// TextBoxCalculatedReading
			// 
			this->TextBoxCalculatedReading->BackColor = System::Drawing::SystemColors::ButtonShadow;
			this->TextBoxCalculatedReading->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 9.75F, System::Drawing::FontStyle::Bold,
				System::Drawing::GraphicsUnit::Point, static_cast<System::Byte>(0)));
			this->TextBoxCalculatedReading->Location = System::Drawing::Point(136, 29);
			this->TextBoxCalculatedReading->Name = L"TextBoxCalculatedReading";
			this->TextBoxCalculatedReading->ReadOnly = true;
			this->TextBoxCalculatedReading->Size = System::Drawing::Size(160, 22);
			this->TextBoxCalculatedReading->TabIndex = 41;
			this->TextBoxCalculatedReading->Text = L"000.000";
			this->TextBoxCalculatedReading->TextAlign = System::Windows::Forms::HorizontalAlignment::Center;
			// 
			// TextBoxSerialNumber
			// 
			this->TextBoxSerialNumber->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 9.75F, System::Drawing::FontStyle::Bold,
				System::Drawing::GraphicsUnit::Point, static_cast<System::Byte>(0)));
			this->TextBoxSerialNumber->Location = System::Drawing::Point(12, 29);
			this->TextBoxSerialNumber->Name = L"TextBoxSerialNumber";
			this->TextBoxSerialNumber->Size = System::Drawing::Size(120, 22);
			this->TextBoxSerialNumber->TabIndex = 40;
			this->TextBoxSerialNumber->Text = L"Enter Here";
			this->TextBoxSerialNumber->TextAlign = System::Windows::Forms::HorizontalAlignment::Center;
			// 
			// LabelUnits
			// 
			this->LabelUnits->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 9.75F, System::Drawing::FontStyle::Bold, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->LabelUnits->Location = System::Drawing::Point(300, 9);
			this->LabelUnits->Name = L"LabelUnits";
			this->LabelUnits->Size = System::Drawing::Size(120, 16);
			this->LabelUnits->TabIndex = 39;
			this->LabelUnits->Text = L"Units";
			this->LabelUnits->TextAlign = System::Drawing::ContentAlignment::MiddleCenter;
			// 
			// LabelCalculatedReading
			// 
			this->LabelCalculatedReading->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 9.75F, System::Drawing::FontStyle::Bold,
				System::Drawing::GraphicsUnit::Point, static_cast<System::Byte>(0)));
			this->LabelCalculatedReading->Location = System::Drawing::Point(136, 9);
			this->LabelCalculatedReading->Name = L"LabelCalculatedReading";
			this->LabelCalculatedReading->Size = System::Drawing::Size(160, 16);
			this->LabelCalculatedReading->TabIndex = 38;
			this->LabelCalculatedReading->Text = L"Calculated Reading";
			this->LabelCalculatedReading->TextAlign = System::Drawing::ContentAlignment::MiddleCenter;
			// 
			// LabelSerialNumber
			// 
			this->LabelSerialNumber->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 9.75F, System::Drawing::FontStyle::Bold, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->LabelSerialNumber->Location = System::Drawing::Point(12, 9);
			this->LabelSerialNumber->Name = L"LabelSerialNumber";
			this->LabelSerialNumber->Size = System::Drawing::Size(120, 16);
			this->LabelSerialNumber->TabIndex = 37;
			this->LabelSerialNumber->Text = L"Serial Number";
			this->LabelSerialNumber->TextAlign = System::Drawing::ContentAlignment::MiddleCenter;
			// 
			// TimerReading
			// 
			this->TimerReading->Tick += gcnew System::EventHandler(this, &MyForm::TimerReading_Tick);
			// 
			// MyForm
			// 
			this->AutoScaleDimensions = System::Drawing::SizeF(6, 13);
			this->AutoScaleMode = System::Windows::Forms::AutoScaleMode::Font;
			this->ClientSize = System::Drawing::Size(679, 75);
			this->Controls->Add(this->ButtonGross);
			this->Controls->Add(this->ButtonTare);
			this->Controls->Add(this->ButtonStop);
			this->Controls->Add(this->ButtonStart);
			this->Controls->Add(this->TextBoxUnits);
			this->Controls->Add(this->TextBoxCalculatedReading);
			this->Controls->Add(this->TextBoxSerialNumber);
			this->Controls->Add(this->LabelUnits);
			this->Controls->Add(this->LabelCalculatedReading);
			this->Controls->Add(this->LabelSerialNumber);
			this->Name = L"MyForm";
			this->Text = L"MyForm";
			this->Load += gcnew System::EventHandler(this, &MyForm::MyForm_Load);
			this->ResumeLayout(false);
			this->PerformLayout();

		}
#pragma endregion
	private: System::Void MyForm_Load(System::Object^  sender, System::EventArgs^  e)
	{

		Text = "Microsoft Visual C++ Example Using FUTEK USB DLL " +
			System::Reflection::Assembly::GetAssembly(FUTEK_USB_DLL::USB_DLL::typeid)->GetName()->Version->ToString();
		SerialNumber = gcnew String("");
		TextBoxSerialNumber->Text = "Enter Here";

		DeviceHandle = gcnew String("0");
		Temp = gcnew String("");
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
	private: System::Void Dispose(System::Object^ sender, System::EventArgs^ e)
	{
		TimerReading->Enabled = false;

		if (OpenedConnection) {}
		else { return; }

		oFutekUSBDLL.Close_Device_Connection(DeviceHandle);
		if (oFutekUSBDLL.DeviceStatus == "0") {}
		else {
			MessageBox::Show("Device Error " + oFutekUSBDLL.DeviceStatus);
			return;
		}

		OpenedConnection = false;
	}

			 /// <summary>
			 /// The function checks the object whether it contains all numeric or not
			 /// </summary>
			 /// <param name="obj"></param>
			 /// <returns>System.Boolean</returns>
	private: System::Boolean IsNumeric(String ^ obj)
	{
		for each (char c in obj) {
			if (!isdigit(c))
				return false;
		}
		return true;
	}

	private: System::Void ButtonStart_Click(System::Object^  sender, System::EventArgs^  e)
	{
		SerialNumber = TextBoxSerialNumber->Text;

		if (OpenedConnection == false) {}
		else { return; }

		oFutekUSBDLL.Open_Device_Connection(SerialNumber);

		if (oFutekUSBDLL.DeviceStatus == "0") {}
		else {
			MessageBox::Show("Device Error " + oFutekUSBDLL.DeviceStatus);
			return;
		}

		DeviceHandle = oFutekUSBDLL.DeviceHandle;

		OpenedConnection = true;

		GetOffsetValue();
		GetFullscaleValue();
		GetFullscaleLoad();
		GetDecimalPoint();
		GetUnitCode();
		FindUnits();

		TimerReading->Interval = 500;
		TimerReading->Enabled = true;
	}
	private: System::Void ButtonStop_Click(System::Object^  sender, System::EventArgs^  e) {
		TimerReading->Enabled = false;

		if (OpenedConnection == true) {}
		else
		{
			return;
		}

		oFutekUSBDLL.Close_Device_Connection(DeviceHandle);
		if (oFutekUSBDLL.DeviceStatus == "0") {}
		else
		{
			MessageBox::Show("Device Error " + oFutekUSBDLL.DeviceStatus);
			return;
		}
		OpenedConnection = false;
	}

	private: System::Void ButtonTare_Click(System::Object^  sender, System::EventArgs^  e)
	{
		Tare = CalculatedReading;
	}

	private: System::Void ButtonGross_Click(System::Object^  sender, System::EventArgs^  e)
	{
		Tare = 0;
	}

			 /// <summary>
			 /// Gets the offset value by using the FUTEK DLL Method and
			 /// check if it's numeric and then parse it into integer
			 /// then store it into the memory
			 /// </summary>
	private: void GetOffsetValue()
	{
		do
		{
			Temp = oFutekUSBDLL.Get_Offset_Value(DeviceHandle, '0');
		} while (IsNumeric(Temp) == false);

		OffsetValue = Int32::Parse(Temp);
	}

			 /// <summary>
			 /// Gets the fullscale value by using the FUTEK DLL Method and
			 /// check if it's numeric and then parse it into integer
			 /// then store it into the memory
			 /// </summary>
	private: void GetFullscaleValue()
	{
		do
		{
			Temp = oFutekUSBDLL.Get_Fullscale_Value(DeviceHandle, '0');
		} while (IsNumeric(Temp) == false);

		FullscaleValue = Int32::Parse(Temp);
	}

			 /// <summary>
			 /// Gets the fullscale load by using the FUTEK DLL Method and
			 /// check if it's numeric and then parse it into integer
			 /// then store it into the memory
			 /// </summary>
	private: void GetFullscaleLoad()
	{
		do
		{
			Temp = oFutekUSBDLL.Get_Fullscale_Load(DeviceHandle, '0');
		} while (IsNumeric(Temp) == false);

		FullScaleLoad = Int32::Parse(Temp);
	}

			 /// <summary>
			 /// Gets the number of decimal places by using the FUTEK 
			 /// DLL Method and check if it's numeric and then parse
			 /// it into integer then store it into the memory
			 /// </summary>
	private: void GetDecimalPoint()
	{
		do
		{
			Temp = oFutekUSBDLL.Get_Decimal_Point(DeviceHandle, '0');
		} while (IsNumeric(Temp) == false);

		DecimalPoint = Int32::Parse(Temp);

		if (DecimalPoint > 3) { DecimalPoint = 0; }
	}

			 /// <summary>
			 /// Gets the unit code to later find unit needed for the device
			 /// by using the FUTEK DLL Method and check if it's numeric and
			 /// then parse it into integer and then store it into the memory
			 /// </summary>
	private: void GetUnitCode()
	{
		do
		{
			Temp = oFutekUSBDLL.Get_Unit_Code(DeviceHandle, '0');
		} while (IsNumeric(Temp) == false);

		UnitCode = Int32::Parse(Temp);
	}

			 /// <summary>
			 /// Uses the UnitCode from the memory to find the correct
			 /// unit for the device
			 /// </summary>
			 /// <remarks>
			 /// For more information about unit code visit:
			 /// http://www.futek.com/files/docs/API/FUTEK_USB_DLL/webframe.html#UnitCodes.html
			 /// </remarks>
	private: void FindUnits()
	{
		switch (UnitCode)
		{
		case 0:
			TextBoxUnits->Text = "atm";
			break;
		case 1:
			TextBoxUnits->Text = "bar";
			break;
		case 2:
			TextBoxUnits->Text = "dyn";
			break;
		case 3:
			TextBoxUnits->Text = "ft-H2O";
			break;
		case 4:
			TextBoxUnits->Text = "ft-lb";
			break;
		case 5:
			TextBoxUnits->Text = "g";
			break;
		case 6:
			TextBoxUnits->Text = "g-cm";
			break;
		case 7:
			TextBoxUnits->Text = "g-mm";
			break;
		case 8:
			TextBoxUnits->Text = "in-H2O";
			break;
		case 9:
			TextBoxUnits->Text = "in-lb";
			break;
		case 10:
			TextBoxUnits->Text = "in-oz";
			break;
		case 11:
			TextBoxUnits->Text = "kdyn";
			break;
		case 12:
			TextBoxUnits->Text = "kg";
			break;
		case 13:
			TextBoxUnits->Text = "kg-cm";
			break;
		case 14:
			TextBoxUnits->Text = "kg/cm2";
			break;
		case 15:
			TextBoxUnits->Text = "kg-m";
			break;
		case 16:
			TextBoxUnits->Text = "klbs";
			break;
		case 17:
			TextBoxUnits->Text = "kN";
			break;
		case 18:
			TextBoxUnits->Text = "kPa";
			break;
		case 19:
			TextBoxUnits->Text = "kpsi";
			break;
		case 20:
			TextBoxUnits->Text = "lbs";
			break;
		case 21:
			TextBoxUnits->Text = "Mdyn";
			break;
		case 22:
			TextBoxUnits->Text = "mmHG";
			break;
		case 23:
			TextBoxUnits->Text = "mN-m";
			break;
		case 24:
			TextBoxUnits->Text = "MPa";
			break;
		case 25:
			TextBoxUnits->Text = "MT";
			break;
		case 26:
			TextBoxUnits->Text = "N";
			break;
		case 27:
			TextBoxUnits->Text = "N-cm";
			break;
		case 28:
			TextBoxUnits->Text = "N-m";
			break;
		case 29:
			TextBoxUnits->Text = "N-mm";
			break;
		case 30:
			TextBoxUnits->Text = "oz";
			break;
		case 31:
			TextBoxUnits->Text = "psi";
			break;
		case 32:
			TextBoxUnits->Text = "Pa";
			break;
		case 33:
			TextBoxUnits->Text = "T";
			break;
		case 34:
			TextBoxUnits->Text = "mV/V";
			break;
		case 35:
			TextBoxUnits->Text = "µA";
			break;
		case 36:
			TextBoxUnits->Text = "mA";
			break;
		case 37:
			TextBoxUnits->Text = "A";
			break;
		case 38:
			TextBoxUnits->Text = "mm";
			break;
		case 39:
			TextBoxUnits->Text = "cm";
			break;
		case 40:
			TextBoxUnits->Text = "dm";
			break;
		case 41:
			TextBoxUnits->Text = "m";
			break;
		case 42:
			TextBoxUnits->Text = "km";
			break;
		case 43:
			TextBoxUnits->Text = "in";
			break;
		case 44:
			TextBoxUnits->Text = "ft";
			break;
		case 45:
			TextBoxUnits->Text = "yd";
			break;
		case 46:
			TextBoxUnits->Text = "mi";
			break;
		case 47:
			TextBoxUnits->Text = "µg";
			break;
		case 48:
			TextBoxUnits->Text = "mg";
			break;
		case 49:
			TextBoxUnits->Text = "LT";
			break;
		case 50:
			TextBoxUnits->Text = "mbar";
			break;
		case 51:
			TextBoxUnits->Text = "?C";
			break;
		case 52:
			TextBoxUnits->Text = "?F";
			break;
		case 53:
			TextBoxUnits->Text = "K";
			break;
		case 54:
			TextBoxUnits->Text = "?Ra";
			break;
		case 55:
			TextBoxUnits->Text = "kN-m";
			break;
		case 56:
			TextBoxUnits->Text = "g-m";
			break;
		case 57:
			TextBoxUnits->Text = "nV";
			break;
		case 58:
			TextBoxUnits->Text = "µV";
			break;
		case 59:
			TextBoxUnits->Text = "mV";
			break;
		case 60:
			TextBoxUnits->Text = "V";
			break;
		case 61:
			TextBoxUnits->Text = "kV";
			break;
		case 62:
			TextBoxUnits->Text = "NONE";
			break;
		default:
			TextBoxUnits->Text = "Undefined";
			break;
		}
	}
	private: System::Void TimerReading_Tick(System::Object^  sender, System::EventArgs^  e)
	{
		do
		{
			Temp = oFutekUSBDLL.Normal_Data_Request(DeviceHandle, '0');
		} while (IsNumeric(Temp) == false);
		NormalData = Int32::Parse(Temp);

		CalculatedReading = (double)(NormalData - OffsetValue) / (FullscaleValue - OffsetValue) * FullScaleLoad / Math::Pow(10, DecimalPoint);
		TextBoxCalculatedReading->Text = String::Format("{0:0.000}", (CalculatedReading - Tare));
	}
	};
}
