namespace USBExample
{
    partial class FormMain
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.components = new System.ComponentModel.Container();
            this.ButtonGross = new System.Windows.Forms.Button();
            this.ButtonTare = new System.Windows.Forms.Button();
            this.ButtonStop = new System.Windows.Forms.Button();
            this.ButtonStart = new System.Windows.Forms.Button();
            this.TextBoxUnits = new System.Windows.Forms.TextBox();
            this.TextBoxCalculatedReading = new System.Windows.Forms.TextBox();
            this.TextBoxSerialNumber = new System.Windows.Forms.TextBox();
            this.LabelUnits = new System.Windows.Forms.Label();
            this.LabelCalculatedReading = new System.Windows.Forms.Label();
            this.LabelSerialNumber = new System.Windows.Forms.Label();
            this.TimerReading = new System.Windows.Forms.Timer(this.components);
            this.SuspendLayout();
            // 
            // ButtonGross
            // 
            this.ButtonGross.Location = new System.Drawing.Point(606, 28);
            this.ButtonGross.Name = "ButtonGross";
            this.ButtonGross.Size = new System.Drawing.Size(58, 23);
            this.ButtonGross.TabIndex = 36;
            this.ButtonGross.Text = "Gross";
            this.ButtonGross.UseVisualStyleBackColor = true;
            this.ButtonGross.Click += new System.EventHandler(this.ButtonGross_Click);
            // 
            // ButtonTare
            // 
            this.ButtonTare.Location = new System.Drawing.Point(544, 28);
            this.ButtonTare.Name = "ButtonTare";
            this.ButtonTare.Size = new System.Drawing.Size(58, 23);
            this.ButtonTare.TabIndex = 35;
            this.ButtonTare.Text = "Tare";
            this.ButtonTare.UseVisualStyleBackColor = true;
            this.ButtonTare.Click += new System.EventHandler(this.ButtonTare_Click);
            // 
            // ButtonStop
            // 
            this.ButtonStop.Location = new System.Drawing.Point(482, 28);
            this.ButtonStop.Name = "ButtonStop";
            this.ButtonStop.Size = new System.Drawing.Size(58, 23);
            this.ButtonStop.TabIndex = 34;
            this.ButtonStop.Text = "Stop";
            this.ButtonStop.UseVisualStyleBackColor = true;
            this.ButtonStop.Click += new System.EventHandler(this.ButtonStop_Click);
            // 
            // ButtonStart
            // 
            this.ButtonStart.Location = new System.Drawing.Point(420, 28);
            this.ButtonStart.Name = "ButtonStart";
            this.ButtonStart.Size = new System.Drawing.Size(58, 23);
            this.ButtonStart.TabIndex = 33;
            this.ButtonStart.Text = "Start";
            this.ButtonStart.UseVisualStyleBackColor = true;
            this.ButtonStart.Click += new System.EventHandler(this.ButtonStart_Click);
            // 
            // TextBoxUnits
            // 
            this.TextBoxUnits.BackColor = System.Drawing.SystemColors.ButtonShadow;
            this.TextBoxUnits.Font = new System.Drawing.Font("Microsoft Sans Serif", 9.75F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.TextBoxUnits.Location = new System.Drawing.Point(296, 28);
            this.TextBoxUnits.Name = "TextBoxUnits";
            this.TextBoxUnits.ReadOnly = true;
            this.TextBoxUnits.Size = new System.Drawing.Size(120, 22);
            this.TextBoxUnits.TabIndex = 32;
            this.TextBoxUnits.Text = "Units";
            this.TextBoxUnits.TextAlign = System.Windows.Forms.HorizontalAlignment.Center;
            // 
            // TextBoxCalculatedReading
            // 
            this.TextBoxCalculatedReading.BackColor = System.Drawing.SystemColors.ButtonShadow;
            this.TextBoxCalculatedReading.Font = new System.Drawing.Font("Microsoft Sans Serif", 9.75F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.TextBoxCalculatedReading.Location = new System.Drawing.Point(132, 28);
            this.TextBoxCalculatedReading.Name = "TextBoxCalculatedReading";
            this.TextBoxCalculatedReading.ReadOnly = true;
            this.TextBoxCalculatedReading.Size = new System.Drawing.Size(160, 22);
            this.TextBoxCalculatedReading.TabIndex = 31;
            this.TextBoxCalculatedReading.Text = "000.000";
            this.TextBoxCalculatedReading.TextAlign = System.Windows.Forms.HorizontalAlignment.Center;
            // 
            // TextBoxSerialNumber
            // 
            this.TextBoxSerialNumber.Font = new System.Drawing.Font("Microsoft Sans Serif", 9.75F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.TextBoxSerialNumber.Location = new System.Drawing.Point(8, 28);
            this.TextBoxSerialNumber.Name = "TextBoxSerialNumber";
            this.TextBoxSerialNumber.Size = new System.Drawing.Size(120, 22);
            this.TextBoxSerialNumber.TabIndex = 30;
            this.TextBoxSerialNumber.Text = "Enter Here";
            this.TextBoxSerialNumber.TextAlign = System.Windows.Forms.HorizontalAlignment.Center;
            // 
            // LabelUnits
            // 
            this.LabelUnits.Font = new System.Drawing.Font("Microsoft Sans Serif", 9.75F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.LabelUnits.Location = new System.Drawing.Point(296, 8);
            this.LabelUnits.Name = "LabelUnits";
            this.LabelUnits.Size = new System.Drawing.Size(120, 16);
            this.LabelUnits.TabIndex = 29;
            this.LabelUnits.Text = "Units";
            this.LabelUnits.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // LabelCalculatedReading
            // 
            this.LabelCalculatedReading.Font = new System.Drawing.Font("Microsoft Sans Serif", 9.75F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.LabelCalculatedReading.Location = new System.Drawing.Point(132, 8);
            this.LabelCalculatedReading.Name = "LabelCalculatedReading";
            this.LabelCalculatedReading.Size = new System.Drawing.Size(160, 16);
            this.LabelCalculatedReading.TabIndex = 28;
            this.LabelCalculatedReading.Text = "Calculated Reading";
            this.LabelCalculatedReading.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // LabelSerialNumber
            // 
            this.LabelSerialNumber.Font = new System.Drawing.Font("Microsoft Sans Serif", 9.75F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.LabelSerialNumber.Location = new System.Drawing.Point(8, 8);
            this.LabelSerialNumber.Name = "LabelSerialNumber";
            this.LabelSerialNumber.Size = new System.Drawing.Size(120, 16);
            this.LabelSerialNumber.TabIndex = 27;
            this.LabelSerialNumber.Text = "Serial Number";
            this.LabelSerialNumber.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // TimerReading
            // 
            this.TimerReading.Tick += new System.EventHandler(this.TimerReading_Tick);
            // 
            // FormMain
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(672, 66);
            this.Controls.Add(this.ButtonGross);
            this.Controls.Add(this.ButtonTare);
            this.Controls.Add(this.ButtonStop);
            this.Controls.Add(this.ButtonStart);
            this.Controls.Add(this.TextBoxUnits);
            this.Controls.Add(this.TextBoxCalculatedReading);
            this.Controls.Add(this.TextBoxSerialNumber);
            this.Controls.Add(this.LabelUnits);
            this.Controls.Add(this.LabelCalculatedReading);
            this.Controls.Add(this.LabelSerialNumber);
            this.Name = "FormMain";
            this.Text = "Form Main";
            this.Load += new System.EventHandler(this.FormMain_Load);
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        internal System.Windows.Forms.Button ButtonGross;
        internal System.Windows.Forms.Button ButtonTare;
        internal System.Windows.Forms.Button ButtonStop;
        internal System.Windows.Forms.Button ButtonStart;
        internal System.Windows.Forms.TextBox TextBoxUnits;
        internal System.Windows.Forms.TextBox TextBoxCalculatedReading;
        internal System.Windows.Forms.TextBox TextBoxSerialNumber;
        internal System.Windows.Forms.Label LabelUnits;
        internal System.Windows.Forms.Label LabelCalculatedReading;
        internal System.Windows.Forms.Label LabelSerialNumber;
        private System.Windows.Forms.Timer TimerReading;
    }
}

