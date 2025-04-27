import asyncio
import datetime

from PyQt6.QtCharts import QChart, QValueAxis, QChartView, QBarCategoryAxis, QBarSet, QBarSeries, QLegend, QCategoryAxis
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QLabel, QSizePolicy
from PyQt6.QtGui import QPainter, QPixmap, QColor
from PyQt6.QtCore import Qt, pyqtSlot, QSize
from qasync import asyncSlot

from services.supabase.controllers.appointment.apponitment_controller import AppointmentController
from signals import SignalRepositorySingleton
import pandas as pd
from dateutil import parser

from views.componenets.customsComponents.custom_lable_with_icon import CustomLabelWithIcon


class AppointmentsAnalyticView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.data = None
        self.parent = parent

        self.signals = SignalRepositorySingleton.instance()
        self.parent.year_picker.currentTextChanged.connect(self.update_analytic_based_on_year)

        # self.signals.updateAnalyticBasedOnYearSignal.connect(self.update_analytic_based_on_year, Qt.ConnectionType.UniqueConnection)

        self.appointment_controller = AppointmentController()

        # Monthly Appointments Chart
        self.monthly_appointment_chart = QChart()
        self.monthly_appointment_chart_view = QChartView(self.monthly_appointment_chart)
        self.monthly_appointment_chart_view.setMinimumSize(400, 400)

        # Appointment Types Chart
        self.no_show_and_cancellation_chart = QChart()
        self.no_show_and_cancellation_chart_view = QChartView(self.no_show_and_cancellation_chart)
        self.no_show_and_cancellation_chart_view.setMinimumSize(400, 400)

        # Appointment Types Chart
        self.appointment_types_chart = QChart()
        self.appointment_types_chart_view = QChartView(self.appointment_types_chart)
        self.appointment_types_chart_view.setMinimumSize(400, 400)


        self.appointment_types_chart.setAnimationOptions(QChart.AnimationOption.AllAnimations)
        self.appointment_types_chart.setAnimationDuration(1000)

        self.months_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
                             "October", "November", "December"]

        central_widget = QWidget()
        central_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.total_appointment_and_types_layout = QHBoxLayout()

        self.create_monthly_appointment_chart()
        self.create_appointment_types_chart()

        self.number_of_no_show_and_cancellation_layout = QHBoxLayout()
        self.create_no_show_and_cancellation_chart()

        self.main_layout.addLayout(self.total_appointment_and_types_layout)
        self.main_layout.addLayout(self.number_of_no_show_and_cancellation_layout)

        central_layout = QVBoxLayout(central_widget)

        central_layout.addLayout(self.main_layout)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        layout.addWidget(central_widget)
        self.setLayout(layout)

        asyncio.create_task(self.get_initial_data())

    def create_monthly_appointment_chart(self):

        legend = self.monthly_appointment_chart.legend()
        legend.setAlignment(Qt.AlignmentFlag.AlignTop)
        legend.setMarkerShape(QLegend.MarkerShape.MarkerShapeCircle)
        legend.setLabelColor(Qt.GlobalColor.darkGray)

        self.monthly_appointment_chart.setAnimationOptions(QChart.AnimationOption.AllAnimations)
        self.monthly_appointment_chart.setAnimationDuration(1000)

        self.monthly_appointment_chart.setTitle("Total Appointments VS New Appointments")

        self.monthly_appointment_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.total_appointment_and_types_layout.addWidget(self.monthly_appointment_chart_view)

    def create_appointment_types_chart(self):

        legend = self.appointment_types_chart.legend()
        legend.setAlignment(Qt.AlignmentFlag.AlignTop)
        legend.setMarkerShape(QLegend.MarkerShape.MarkerShapeCircle)
        legend.setLabelColor(Qt.GlobalColor.darkGray)

        self.appointment_types_chart.setTitle("Appointments Types")
        self.appointment_types_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.total_appointment_and_types_layout.addWidget(self.appointment_types_chart_view)

    def create_no_show_and_cancellation_chart(self):
        legend = self.no_show_and_cancellation_chart.legend()
        legend.setAlignment(Qt.AlignmentFlag.AlignTop)
        legend.setMarkerShape(QLegend.MarkerShape.MarkerShapeCircle)
        legend.setLabelColor(Qt.GlobalColor.darkGray)

        self.no_show_and_cancellation_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.no_show_and_cancellation_chart.setTitle("Number of Appointment's No-Shows and Cancellations")
        self.number_of_no_show_and_cancellation_layout.addWidget(self.no_show_and_cancellation_chart_view)

    def update_monthly_appointment_chart(self):
        if self.data:
            df = pd.DataFrame(self.data, columns=["appointment_id", "appointment_status", "created_at"])
            df['created_at'] = df['created_at'].apply(parser.parse)
            df['month'] = df['created_at'].dt.strftime('%B')

            occurred_appointments = df[~df['appointment_status'].isin(['canceled', 'rejected', 'no-show', 'expired'])]

            # Group and aggregate the data
            monthly_data = occurred_appointments.groupby('month').agg(
                total_appointments=('appointment_id', 'nunique'),
                new_appointments=('appointment_id', 'size')
            ).reset_index()

            # Ensure the 'month' column is sorted according to the specified order
            monthly_data['month'] = pd.Categorical(monthly_data['month'], categories=self.months_order, ordered=True)
            monthly_data = monthly_data.sort_values('month')

            total_appointments_list = []
            new_appointments_list = []

            for month in self.months_order:
                if month in monthly_data['month'].values:
                    total_appointments = monthly_data.loc[monthly_data['month'] == month, 'total_appointments'].values[
                        0]
                    new_appointments = monthly_data.loc[monthly_data['month'] == month, 'new_appointments'].values[0]
                else:
                    total_appointments = 0
                    new_appointments = 0

                total_appointments_list.append(total_appointments)
                new_appointments_list.append(new_appointments)

            total_appointments_set = QBarSet("Total Appointments")
            new_appointments_set = QBarSet("New Appointments")

            new_appointments_set.setColor(QColor("#ff734d"))
            total_appointments_set.setColor(QColor("#0dbab5"))

            total_appointments_set.append(total_appointments_list)
            new_appointments_set.append(new_appointments_list)

            new_series = QBarSeries()
            new_series.append(total_appointments_set)
            new_series.append(new_appointments_set)

            # Clear existing series and axes
            self.monthly_appointment_chart.removeAllSeries()

            for axis in self.monthly_appointment_chart.axes():
                self.monthly_appointment_chart.removeAxis(axis)

            # Add new series
            self.monthly_appointment_chart.addSeries(new_series)

            axis_x = QBarCategoryAxis()
            axis_x.append(self.months_order)
            self.monthly_appointment_chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
            new_series.attachAxis(axis_x)

            # Create and add new axes
            axis_y = QValueAxis()
            self.monthly_appointment_chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
            new_series.attachAxis(axis_y)

            # Calculate percentage change
            current_month = datetime.datetime.now().month

            percentage_change_data = calculate_percentage_change(
                total_appointments_list[current_month - 1],
                total_appointments_list[current_month - 2]
            )
            self.update_percentage_change_card(percentage_change_data)

        else:
            self.update_percentage_change_card({
                "trend_type": "no change",
                "trend_value": 0,
                "total_appointments": 0
            })

            self.monthly_appointment_chart.removeAllSeries()

            total_appointments_set = QBarSet("Total appointments")
            new_appointments_set = QBarSet("New appointments")

            new_empty_series = QBarSeries()
            new_empty_series.append(total_appointments_set)
            new_empty_series.append(new_appointments_set)

            # Clear existing series and axes
            self.monthly_appointment_chart.removeAllSeries()
            for axis in self.monthly_appointment_chart.axes():
                self.monthly_appointment_chart.removeAxis(axis)

            self.monthly_appointment_chart.addSeries(new_empty_series)

            axis_x = QBarCategoryAxis()
            axis_x.append(self.months_order)
            self.monthly_appointment_chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
            new_empty_series.attachAxis(axis_x)

    def update_appointment_types_chart(self):
        if self.data:

            df = pd.DataFrame(self.data, columns=["appointment_id", "appointment_type", "appointment_date"])

            df['appointment_date'] = df['appointment_date'].apply(parser.parse)
            df['month'] = df['appointment_date'].dt.strftime('%B')

            df = df[df['appointment_type'].notna() & df['appointment_type'].str.strip().astype(bool)]

            grouped_df = df.groupby(['month', 'appointment_type']).size().unstack(fill_value=0).reindex(
                self.months_order, fill_value=0)

            self.appointment_types_chart.setTitle("Appointments Types")

            self.appointment_types_chart.removeAllSeries()

            for axis in self.appointment_types_chart.axes():
                self.appointment_types_chart.removeAxis(axis)

            # Create the stacked bar series
            series = QBarSeries()

            # Add data to the series
            for appointment_type in grouped_df.columns:
                bar_set = QBarSet(appointment_type)
                for value in grouped_df[appointment_type]:
                    bar_set.append(value)
                series.append(bar_set)
            # Add the series to the chart
            self.appointment_types_chart.addSeries(series)

            # Set the X axis
            axis_x = QBarCategoryAxis()
            axis_x.append(self.months_order)

            self.appointment_types_chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
            series.attachAxis(axis_x)

            # Set the Y axis
            axis_y = QValueAxis()
            self.appointment_types_chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
            series.attachAxis(axis_y)

        else:
            self.appointment_types_chart.setTitle("")
            new_empty_series = QBarSeries()
            new_empty_series.append([])

            self.appointment_types_chart.removeAllSeries()

            for axis in self.appointment_types_chart.axes():
                self.appointment_types_chart.removeAxis(axis)

            self.appointment_types_chart.addSeries(new_empty_series)

            axis_x = QBarCategoryAxis()
            axis_x.append(self.months_order)
            self.appointment_types_chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
            new_empty_series.attachAxis(axis_x)

    def update_percentage_change_card(self, data):
        self.parent.total_appointments_card.update_data(data)

    def update_no_show_and_cancellation_charts(self):
        if self.data:
            df = pd.DataFrame(self.data, columns=["appointment_id", "appointment_status", "created_at"])
            df['created_at'] = df['created_at'].apply(parser.parse)
            df['month'] = df['created_at'].dt.strftime('%B')

            no_shows = df[df['appointment_status'] == 'no-show'].groupby('month').size().reindex(self.months_order,
                                                                                                 fill_value=0)
            cancellations = df[df['appointment_status'] == 'canceled'].groupby('month').size().reindex(
                self.months_order, fill_value=0)

            bar_series = QBarSeries()

            no_show_set = QBarSet('No-Shows')
            no_show_set.append(no_shows.values)
            bar_series.append(no_show_set)

            no_show_set.setColor(QColor("#2db5cd"))

            cancellation_set = QBarSet('Cancellations')
            cancellation_set.append(cancellations.values)
            bar_series.append(cancellation_set)

            cancellation_set.setColor(QColor("#fb696b"))

            self.no_show_and_cancellation_chart.removeAllSeries()
            for axis in self.no_show_and_cancellation_chart.axes():
                self.no_show_and_cancellation_chart.removeAxis(axis)

            self.no_show_and_cancellation_chart.addSeries(bar_series)
            self.no_show_and_cancellation_chart.setTitle("Number of Appointment's No-Shows and Cancellations")

            axis_x = QBarCategoryAxis()
            axis_x.append(self.months_order)
            self.no_show_and_cancellation_chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
            bar_series.attachAxis(axis_x)

            axis_y = QValueAxis()
            axis_y.setRange(0, max(no_shows.max(), cancellations.max()) + 2)
            self.no_show_and_cancellation_chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
            bar_series.attachAxis(axis_y)
        else:
            self.no_show_and_cancellation_chart.setTitle("")
            new_empty_series = QBarSeries()
            new_empty_series.append([])

            self.no_show_and_cancellation_chart.removeAllSeries()

            for axis in self.no_show_and_cancellation_chart.axes():
                self.no_show_and_cancellation_chart.removeAxis(axis)

            self.no_show_and_cancellation_chart.addSeries(new_empty_series)

            axis_x = QBarCategoryAxis()
            axis_x.append(self.months_order)
            self.no_show_and_cancellation_chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
            new_empty_series.attachAxis(axis_x)

    async def get_initial_data(self):
        self.data = await self.appointment_controller.get_all_appointments_by_year(self.parent.current_year)

    @pyqtSlot(str)
    @asyncSlot()
    async def update_analytic_based_on_year(self, year):
        self.data = await self.appointment_controller.get_all_appointments_by_year(year)
        self.update_appointment_types_chart()
        self.update_monthly_appointment_chart()
        self.update_no_show_and_cancellation_charts()


def calculate_percentage_change(current_month, previous_month):
    if current_month:
        if previous_month == 0:
            percentage_change = 0
        else:
            percentage_change = ((
                                         current_month - previous_month) / previous_month) * 100
        trend_type = "increased" if percentage_change > 0 else "decreased"
        return {
            "trend_type": trend_type,
            "trend_value": abs(int(percentage_change)),
            "total_appointments": current_month
        }
    return {
        "trend_type": "no change",
        "trend_value": 0,
        "total_appointments": current_month
    }


class TotalAppointmentsCard(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)

        appointments_label = CustomLabelWithIcon(name="Total Appointments",
                                                 icon_path=":resources/icons/appointments_analytic.svg",
                                                 icon_size=QSize(25, 25))

        appointments_label.label.setStyleSheet("""
         QLabel {
                  border:0;
                  background-color:transparent;
                  color:#24282B;
                  font-size:12pt;
                  padding-left:5px;
              }
        """)

        self.total_appointments_label = QLabel(str(data["total_appointments"]))
        self.total_appointments_label.setStyleSheet("""
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

        top_central_layout.addWidget(appointments_label)
        top_central_layout.addWidget(self.total_appointments_label)

        if data["trend_type"] == "increased":
            self.trend_label = CustomLabelWithIcon(name=str(int(data["trend_value"])) + "%",
                                                   icon_path=":resources/icons/trend_up.svg",
                                                   icon_size=QSize(15, 15))
            self.trend_label.label.setStyleSheet("""
                       border:0;
                       background-color:transparent;
                       color:#2db5cd;
                       font-size:8pt;
             """)
        else:
            self.trend_label = CustomLabelWithIcon(name=str(int(data["trend_value"])) + "%",
                                                   icon_path=":resources/icons/trend_down.svg",
                                                   icon_size=QSize(15, 15))
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
        self.total_appointments_label.setText(str(int(data["total_appointments"])))

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
            self.trend_label.label.setText(str(data["trend_value"]) + "%")
            self.trend_label.label.setStyleSheet("""
                            border:0;
                            background-color:transparent;
                            color:#D02048;
                            font-size:10pt;
              """)
            pixmap = QPixmap(":resources/icons/trend_down.svg").scaled(15, 15)
            self.trend_label.icon_label.setPixmap(pixmap)
