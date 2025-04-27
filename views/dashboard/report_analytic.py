import asyncio
import datetime

from PyQt6.QtCharts import QChart, QValueAxis, QChartView, QBarCategoryAxis, QBarSet, QBarSeries, QPieSeries, QPieSlice, \
    QLegend
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QLabel
from PyQt6.QtGui import QPainter, QPixmap, QColor
from PyQt6.QtCore import Qt, pyqtSlot, QSize
from qasync import asyncSlot

from services.supabase.controllers.report.report_controller import ReportController
from signals import SignalRepositorySingleton
import pandas as pd
from dateutil import parser

from views.componenets.customsComponents.custom_lable_with_icon import CustomLabelWithIcon
from views.dashboard.report_data_process import ReportDataProcessor


class ReportsAnalyticView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.data = None
        self.parent = parent
        self.data_processor = None

        self.signals = SignalRepositorySingleton.instance()
        self.parent.year_picker.currentTextChanged.connect(self.update_analytic_based_on_year)

        self.months_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
                             "October", "November", "December"]

        self.report_controller = ReportController()

        self.report_chart = QChart()
        self.report_chart_view = QChartView(self.report_chart)
        self.report_chart_view.setMinimumSize(400, 400)

        self.report_category_chart = QChart()
        self.report_category_chart_view = QChartView(self.report_category_chart)
        self.report_category_chart_view.setMinimumSize(400, 400)

        self.main_layout = QHBoxLayout()
        self.create_report_chart()
        self.create_report_category_chart()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        layout.addLayout(self.main_layout)

        self.setLayout(layout)

        asyncio.create_task(self.get_initial_data())

    @pyqtSlot(str)
    @asyncSlot()
    async def update_analytic_based_on_year(self, year):
        self.data = await self.report_controller.get_all_reports_by_year(year)
        self.start_data_processing(self.data)

    def start_data_processing(self, data):
        if self.data_processor is not None:
            self.data_processor.terminate()
        self.data_processor = ReportDataProcessor(data)
        self.data_processor.data_is_ready.connect(self.update_report_chart)
        self.data_processor.error.connect(self.handle_error)
        self.data_processor.start()

    def handle_error(self, message):
        print("Error:", message)

    async def get_initial_data(self):
        self.data = await self.report_controller.get_all_reports_by_year(
            self.parent.current_year)

    def create_report_chart(self):

        legend = self.report_chart.legend()
        legend.setAlignment(Qt.AlignmentFlag.AlignTop)
        legend.setMarkerShape(QLegend.MarkerShape.MarkerShapeCircle)
        legend.setLabelColor(Qt.GlobalColor.darkGray)

        self.report_chart.setAnimationOptions(QChart.AnimationOption.AllAnimations)
        self.report_chart.setAnimationDuration(1000)

        self.report_chart.setTitle("Reports")

        self.report_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.main_layout.addWidget(self.report_chart_view)

    def create_report_category_chart(self):

        legend = self.report_category_chart.legend()
        legend.setAlignment(Qt.AlignmentFlag.AlignTop)
        legend.setMarkerShape(QLegend.MarkerShape.MarkerShapeCircle)
        legend.setLabelColor(Qt.GlobalColor.darkGray)

        self.report_category_chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        self.report_category_chart.setTitle("Report's Category Distribution")

        self.report_category_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.main_layout.addWidget(self.report_category_chart_view)

    def update_report_chart(self, df):
        if not df.empty:
            # Data preparation is already handled by the DataProcessor thread
            monthly_data = df.groupby('month').agg(
                total_reports=('report_id', 'nunique'),
            ).reset_index()

            monthly_data['month'] = pd.Categorical(monthly_data['month'], categories=self.months_order,
                                                   ordered=True)
            monthly_data = monthly_data.sort_values('month')

            total_reports_set = QBarSet("Reports")
            total_reports_set.setColor(QColor("#f87171"))

            total_reports_list = []

            for month in self.months_order:
                if month in monthly_data['month'].values:
                    total_reports = monthly_data.loc[monthly_data['month'] == month, 'total_reports'].values[0]
                else:
                    total_reports = 0

                total_reports_list.append(total_reports)

            total_reports_set.append(total_reports_list)

            self.report_chart.removeAllSeries()

            for axis in self.report_chart.axes():
                self.report_chart.removeAxis(axis)

            series = QBarSeries()
            series.append(total_reports_set)

            self.report_chart.addSeries(series)

            axis_x = QBarCategoryAxis()
            axis_x.append(self.months_order)

            axis_y = QValueAxis()

            self.report_chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
            self.report_chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)

            series.attachAxis(axis_x)
            series.attachAxis(axis_y)

            # Calculate percentage change if there are at least 2 months of data to compare
            if len(total_reports_list) > 1:
                current_month = datetime.datetime.now().month
                percentage_change_data = calculate_percentage_change(
                    total_reports_list[current_month - 1],
                    total_reports_list[max(0, current_month - 2)]
                )
                self.update_percentage_change_card(percentage_change_data)
        else:
            self.report_chart.setTitle("No Data Available")
            self.update_percentage_change_card({
                "trend_type": "no change",
                "trend_value": 0,
                "total_reports": 0
            })

            self.report_chart.removeAllSeries()

            for axis in self.report_chart.axes():
                self.report_chart.removeAxis(axis)

            series = QBarSeries()

            self.report_chart.addSeries(series)

            axis_x = QBarCategoryAxis()
            axis_x.append(self.months_order)

            axis_y = QValueAxis()

            self.report_chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
            self.report_chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)

    def update_report_category_chart(self):
        if self.data:
            df = pd.DataFrame(self.data, columns=["report_id", "created_at", "category"])
            df['created_at'] = df['created_at'].apply(parser.parse)

            df['month'] = df['created_at'].dt.strftime('%B')

            report_category_chart = df['category'].value_counts()

            self.report_category_chart.setTitle("Report's Category Distribution")

            total_count = report_category_chart.sum()

            self.report_category_chart.removeAllSeries()

            series = QPieSeries()
            for method, count in report_category_chart.items():
                percentage = QPieSlice(f"{method} {count / total_count:.1%}", count)
                series.append(percentage)

            self.report_category_chart.addSeries(series)

        else:
            self.report_category_chart.removeAllSeries()

            series = QPieSeries()
            series.append([])

            self.report_category_chart.addSeries(series)

    # @pyqtSlot(str)
    # @asyncSlot()
    # async def update_analytic_based_on_year(self, year):
    #     self.data = await self.report_controller.get_all_reports_by_year(year)
    #     self.update_report_chart()
    #     self.update_report_category_chart()

    def update_percentage_change_card(self, data):
        self.parent.total_reports_card.update_data(data)


class TotalReportsCard(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)

        reports_label = CustomLabelWithIcon(name="Total Reports",
                                            icon_path=":resources/icons/reports_analytic.svg",
                                            icon_size=QSize(25, 25))

        reports_label.label.setStyleSheet("""
         QLabel {
                  border:0;
                  background-color:transparent;
                  color:#24282B;
                  font-size:12pt;
                  padding-left:5px;
              }
        """)

        self.total_reports_label = QLabel(str(data["total_reports"]))
        self.total_reports_label.setStyleSheet("""
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

        top_central_layout.addWidget(reports_label)
        top_central_layout.addWidget(self.total_reports_label)

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
        self.total_reports_label.setText(str(data["total_reports"]))

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
            "total_reports": current_month_patients
        }
    return {
        "trend_type": "no change",
        "trend_value": 0,
        "total_reports": current_month_patients
    }
