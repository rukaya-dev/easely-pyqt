import asyncio
import datetime

from PyQt6.QtCharts import QChart, QValueAxis, QChartView, QBarCategoryAxis, QBarSet, QBarSeries, QLegend
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QLabel, QSizePolicy
from PyQt6.QtGui import QPainter, QPixmap, QColor
from PyQt6.QtCore import Qt, pyqtSlot, QSize
from qasync import asyncSlot

from services.supabase.controllers.patient.patient_controller import PatientController
from signals import SignalRepositorySingleton
import pandas as pd
from dateutil import parser

from views.componenets.customsComponents.custom_lable_with_icon import CustomLabelWithIcon


class PatientsAnalyticView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.data = None
        self.parent = parent

        self.signals = SignalRepositorySingleton.instance()
        self.parent.year_picker.currentTextChanged.connect(self.update_analytic_based_on_year)
        # self.signals.updateAnalyticBasedOnYearSignal.connect(self.update_analytic_based_on_year, Qt.ConnectionType.UniqueConnection)

        self.patient_controller = PatientController()

        # Monthly Total Patient Chart
        self.monthly_patient_chart = QChart()
        self.monthly_patients_chart_view = QChartView(self.monthly_patient_chart)
        self.monthly_patients_chart_view.setMinimumSize(400, 400)

        # Patient Age Chart
        self.age_chart = QChart()
        self.age_chart_view = QChartView(self.age_chart)
        self.age_chart_view.setMinimumSize(400, 400)

        self.months_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
                             "October", "November", "December"]

        central_widget = QWidget()
        central_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.monthly_and_age_layout = QHBoxLayout()
        self.create_monthly_patient_chart()
        self.create_patient_age_chart()

        self.main_layout.addLayout(self.monthly_and_age_layout)

        central_layout = QVBoxLayout(central_widget)
        central_layout.addLayout(self.main_layout)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        layout.addWidget(central_widget)
        self.setLayout(layout)

        asyncio.create_task(self.get_initial_data())

    def create_monthly_patient_chart(self):

        legend = self.monthly_patient_chart.legend()
        legend.setAlignment(Qt.AlignmentFlag.AlignTop)
        legend.setMarkerShape(QLegend.MarkerShape.MarkerShapeCircle)
        legend.setLabelColor(Qt.GlobalColor.darkGray)

        self.monthly_patient_chart.setAnimationOptions(QChart.AnimationOption.AllAnimations)
        self.monthly_patient_chart.setAnimationDuration(1000)

        self.monthly_patient_chart.setTitle("Total Patients VS New Patients")

        self.monthly_patients_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        axis_x = QBarCategoryAxis()
        axis_x.append(self.months_order)

        axis_y = QValueAxis()

        self.monthly_patient_chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        self.monthly_patient_chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)

        self.monthly_and_age_layout.addWidget(self.monthly_patients_chart_view)

    def create_patient_age_chart(self):
        legend = self.age_chart.legend()
        legend.setAlignment(Qt.AlignmentFlag.AlignTop)
        legend.setMarkerShape(QLegend.MarkerShape.MarkerShapeCircle)
        legend.setLabelColor(Qt.GlobalColor.darkGray)

        self.age_chart.setTitle("Patient's Age Distribution")
        self.age_chart.setAnimationOptions(QChart.AnimationOption.AllAnimations)
        self.age_chart.setAnimationDuration(1000)
        self.age_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.monthly_and_age_layout.addWidget(self.age_chart_view)

    def update_monthly_patient_chart(self):
        if self.data:
            df = pd.DataFrame(self.data, columns=["patient_id", "created_at"])
            df['created_at'] = df['created_at'].apply(parser.parse)
            df['month'] = df['created_at'].dt.strftime('%B')

            monthly_data = df.groupby('month').agg(
                total_patients=('patient_id', 'nunique'),
                new_patients=('patient_id', 'size')
            ).reset_index()

            monthly_data['month'] = pd.Categorical(monthly_data['month'], categories=self.months_order, ordered=True)
            monthly_data = monthly_data.sort_values('month')

            total_patients_list = []
            new_patients_list = []

            for month in self.months_order:
                if month in monthly_data['month'].values:
                    total_patients = monthly_data.loc[monthly_data['month'] == month, 'total_patients'].values[0]
                    new_patients = monthly_data.loc[monthly_data['month'] == month, 'new_patients'].values[0]
                else:
                    total_patients = 0
                    new_patients = 0

                total_patients_list.append(total_patients)
                new_patients_list.append(new_patients)

            total_patients_set = QBarSet("Total Patients")
            new_patients_set = QBarSet("New Patients")

            total_patients_set.setColor(QColor("#ff734d"))
            new_patients_set.setColor(QColor("#dfd37e"))

            total_patients_set.append(total_patients_list)
            new_patients_set.append(new_patients_list)

            new_series = QBarSeries()
            new_series.append(total_patients_set)
            new_series.append(new_patients_set)

            # Clear existing series and axes
            self.monthly_patient_chart.removeAllSeries()

            for axis in self.monthly_patient_chart.axes():
                self.monthly_patient_chart.removeAxis(axis)

            # Add new series
            self.monthly_patient_chart.addSeries(new_series)

            axis_x = QBarCategoryAxis()
            axis_x.append(self.months_order)
            self.monthly_patient_chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
            new_series.attachAxis(axis_x)

            # Create and add new axes
            axis_y = QValueAxis()
            self.monthly_patient_chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
            new_series.attachAxis(axis_y)

            # Calculate percentage change
            current_month = datetime.datetime.now().month
            percentage_change_data = calculate_percentage_change(
                total_patients_list[current_month - 1],
                total_patients_list[current_month - 2]
            )
            self.update_percentage_change_card(percentage_change_data)

        else:
            self.update_percentage_change_card({
                "trend_type": "no change",
                "trend_value": 0,
                "total_patients": 0
            })

            self.monthly_patient_chart.removeAllSeries()

            new_empty_series = QBarSeries()
            new_empty_series.append([])
            new_empty_series.append([])

            # Clear existing series and axes
            self.monthly_patient_chart.removeAllSeries()
            for axis in self.monthly_patient_chart.axes():
                self.monthly_patient_chart.removeAxis(axis)

            self.monthly_patient_chart.addSeries(new_empty_series)

            axis_x = QBarCategoryAxis()
            axis_x.append(self.months_order)
            self.monthly_patient_chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
            new_empty_series.attachAxis(axis_x)

    def update_patient_age_chart(self):
        if self.data:
            df = pd.DataFrame(self.data, columns=["patient_id", "patient_age", "patient_age_unit"])
            df['age_in_years'] = df.apply(
                lambda row: row['patient_age'] if row['patient_age_unit'] == 'years' else
                (row['patient_age'] / 12 if row['patient_age_unit'] == 'months' else row['patient_age'] / 365),
                axis=1
            )

            age_bins = [0, 18, 30, 40, 50, 60, 70, 80, 90, 100]
            age_labels = ['0-18', '19-30', '31-40', '41-50', '51-60', '61-70', '71-80', '81-90', '91-100']
            df['age_group'] = pd.cut(df['age_in_years'], bins=age_bins, labels=age_labels, right=False)

            age_group_counts = df['age_group'].value_counts().sort_index()

            age_set = QBarSet("Age")
            age_set.setColor(QColor("#2db5cd"))

            age_set.append([age_group_counts.get(label, 0) for label in age_labels])

            age_series = QBarSeries()
            age_series.append(age_set)

            self.age_chart.removeAllSeries()
            self.age_chart.addSeries(age_series)

            # Clear existing axes
            for axis in self.age_chart.axes():
                self.age_chart.removeAxis(axis)

            axis_x = QBarCategoryAxis()
            axis_x.append(age_labels)

            age_axis_y = QValueAxis()

            self.age_chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
            self.age_chart.addAxis(age_axis_y, Qt.AlignmentFlag.AlignLeft)

            age_series.attachAxis(axis_x)
            age_series.attachAxis(age_axis_y)
        else:
            self.age_chart.setTitle("")

            new_empty_series = QBarSeries()

            self.age_chart.removeAllSeries()
            self.age_chart.addSeries(new_empty_series)

    def update_percentage_change_card(self, data):
        self.parent.total_patients_card.update_data(data)

    async def get_initial_data(self):
        self.data = await self.patient_controller.get_all_patients_by_year(self.parent.current_year)

    @pyqtSlot(str)
    @asyncSlot()
    async def update_analytic_based_on_year(self, year):
        self.signals.globalCreateLoadingNotificationSignal.emit("UPDATE_PATIENT_ANALYTIC")

        self.data = await self.patient_controller.get_all_patients_by_year(year)

        self.update_monthly_patient_chart()
        self.update_patient_age_chart()
        self.update_patient_age_chart()
        self.signals.globalLoadingNotificationControllerSignal.emit("UPDATE_PATIENT_ANALYTIC")


class PatientPercentageChangeCard(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)

        patient_label = CustomLabelWithIcon(name="Total Patients",
                                            icon_path=":resources/icons/patient_analytic.svg",
                                            icon_size=QSize(25, 25))
        patient_label.setMinimumSize(100, 30)
        patient_label.label.setStyleSheet("""
         QLabel {
                  border:0;
                  background-color:transparent;
                  color:#24282B;
                  font-size:12pt;
                  padding-left:5px;
              }
        """)

        self.total_patients_label = QLabel(str(data["total_patients"]))
        self.total_patients_label.setStyleSheet("""
         QLabel {
                  border:0;
                  background-color:transparent;
                  color:#24282B;
                  font-size:16pt;
                  padding-left:5px;
              }
        """)

        top_central_widget = QWidget()
        top_central_widget.setStyleSheet("border:1px solid #DCE6EB;border-radius:15px;background-color:white;")

        top_central_layout = QVBoxLayout(top_central_widget)
        top_central_layout.setSpacing(20)
        top_central_layout.setContentsMargins(15, 15, 15, 15)

        top_central_layout.addWidget(patient_label)
        top_central_layout.addWidget(self.total_patients_label)

        if data["trend_type"] == "increased":
            self.trend_label = CustomLabelWithIcon(name=str(int(data["trend_value"])) + "%",
                                                   icon_path=":resources/icons/trend_up.svg",
                                                   icon_size=QSize(10, 10))
            self.trend_label.label.setStyleSheet("""
                       border:0;
                       background-color:transparent;
                       color:#2db5cd;
                       font-size:8pt;
             """)
        else:
            self.trend_label = CustomLabelWithIcon(name=str(int(data["trend_value"])) + "%",
                                                   icon_path=":resources/icons/trend_down.svg",
                                                   icon_size=QSize(10, 10))
            self.trend_label.label.setStyleSheet("""
                           border:0;
                           background-color:transparent;
                           color:#D02048;
                           font-size:8pt;

                 """)

        compare_to_last_month_label = QLabel("Compare to last month")
        compare_to_last_month_label.setStyleSheet("""
         QLabel {
                  border:0;
                  background-color:transparent;
                  color:#848484;
                  font-size:8pt;
              }
        """)

        trending_layout = QHBoxLayout()
        trending_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        trending_layout.setContentsMargins(15, 0, 15, 0)
        trending_layout.setSpacing(20)

        trending_layout.addWidget(self.trend_label, Qt.AlignmentFlag.AlignLeft)
        trending_layout.addWidget(compare_to_last_month_label, Qt.AlignmentFlag.AlignRight)

        lower_central_widget = QWidget()
        lower_central_widget.setStyleSheet("""
            border:0;
            border-left:1px solid #DCE6EB;
            border-right:1px solid #DCE6EB;
            border-bottom:1px solid #DCE6EB;
            border-radius:15px;
            background-color:#f9f9f9;
        """)

        lower_central_layout = QVBoxLayout(lower_central_widget)
        lower_central_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        lower_central_layout.setContentsMargins(0, 0, 0, 10)

        lower_central_layout.addWidget(top_central_widget)

        lower_central_layout.addLayout(trending_layout)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(lower_central_widget)

        self.setFixedSize(235, 140)

        self.setLayout(layout)

    def update_data(self, data):
        self.total_patients_label.setText(str(data["total_patients"]))

        if data["trend_type"] == "increased":
            self.trend_label.label.setText(str(int(data["trend_value"])) + "%")
            self.trend_label.label.setStyleSheet("""
                        border:0;
                        background-color:transparent;
                        color:#2db5cd;
                       font-size:10pt;
              """)
            pixmap = QPixmap(":resources/icons/trend_up.svg").scaled(15, 15)
            self.trend_label.icon_label.setPixmap(pixmap)
        else:
            self.trend_label.label.setText(str(int(data["trend_value"])) + "%")
            self.trend_label.label.setStyleSheet("""
                            border:0;
                            background-color:transparent;
                            color:#D02048;
                           font-size:10pt;
              """)
            pixmap = QPixmap(":resources/icons/trend_down.svg").scaled(15, 15)
            self.trend_label.icon_label.setPixmap(pixmap)


def calculate_percentage_change(current_month_patients, previous_month_patients):
    if current_month_patients:
        if previous_month_patients == 0:
            percentage_change = 0
        else:
            percentage_change = ((current_month_patients - previous_month_patients) / previous_month_patients) * 100
        trend_type = "increased" if percentage_change > 0 else "decreased"
        return {
            "trend_type": trend_type,
            "trend_value": abs(int(percentage_change)),
            "total_patients": current_month_patients
        }
    return {
        "trend_type": "no change",
        "trend_value": 0,
        "total_patients": current_month_patients
    }
